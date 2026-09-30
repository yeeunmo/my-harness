#!/usr/bin/env python3
"""허들링 디자인 하네스 판정 스크립트 (읽기전용 판정자).

rules/rules.json(SSOT)만 기준으로 runs/<화면>/ 의 01~03을 검사하고
04-verdict.json을 쓴다. 게이트 정의는 docs/harness-gates.md.

사용:
  python3 scripts/judge.py <화면>             # 판정 후 04-verdict.json 기록
  python3 scripts/judge.py <화면> --no-write  # 기록 없이 결과만 출력 (재현 확인용)

종료 코드: 0 = pass, 1 = fail, 2 = 사용법 오류
"""
import argparse
import datetime
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 게이트별 실패 시 되돌아갈 단계 (docs/harness-gates.md)
RETURN_STAGE = {
    "G1-1": 1, "G1-2": 1, "G1-3": 1,
    "G2-1": 2, "G2-2": 2, "G2-3": 2,
    "G3-1": 3, "G3-2": 3, "G3-3": 3, "G3-4": 3, "G3-5": 3, "G3-6": None,
    "G3-7": 2, "G3-8": 2, "G3-9": 2, "G3-10": 2,
}
WARN_ONLY = {"G3-6"}
MAX_ATTEMPTS = 3

GENERIC_FONTS = {"sans-serif", "serif", "monospace", "system-ui", "inherit", "initial", "unset"}
CSS_KEYWORDS = {"inherit", "initial", "unset", "none", "transparent", "currentcolor"}
NAMED_COLORS = {
    "black", "white", "red", "green", "blue", "gray", "grey", "yellow", "orange", "purple",
    "pink", "brown", "navy", "teal", "cyan", "magenta", "lime", "silver", "maroon", "olive",
    "aqua", "fuchsia", "gold", "indigo", "violet", "coral", "salmon", "tomato", "crimson",
    "beige", "ivory", "khaki", "lavender", "tan", "chocolate", "skyblue", "whitesmoke",
    "gainsboro", "lightgray", "lightgrey", "darkgray", "darkgrey", "dimgray", "dimgrey",
}
COLOR_PROPS = re.compile(
    r"^(color|background(-color)?|border(-(top|right|bottom|left))?(-color)?|outline(-color)?"
    r"|fill|stroke|stop-color|text-decoration(-color)?|caret-color|accent-color|column-rule(-color)?)$"
)
RADIUS_PROP = re.compile(r"^border(-[a-z]+)*-radius$")
SPACING_PROP = re.compile(r"^(margin|padding)(-[a-z]+)*$|^(row-|column-)?gap$")
HEX = re.compile(r"#([0-9a-fA-F]{3,8})\b")
COLOR_FUNC = re.compile(r"\b(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(", re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TEXT_ATTRS = ("alt", "title", "placeholder", "aria-label", "value")


def load_rules(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def gate(status, detail=None, count=None):
    return {"status": status, "count": count if count is not None else len(detail or []), "detail": detail or []}


def pass_or_fail(violations):
    return gate("fail" if violations else "pass", violations)


def missing(name):
    return gate("fail", [f"{name} 파일 없음"], 1)


def flatten_colors(colors):
    out = set()
    for v in colors.values():
        if isinstance(v, dict):
            out |= flatten_colors(v)
        else:
            out.add(v.upper())
    return out


def find_words(text, words):
    return [w for w in words if w in text]


def find_tokens(text, tokens):
    return [t for t in tokens if re.search(rf"(?<![a-z_]){re.escape(t)}(?![a-z_])", text)]


# ---------- G1 리서치 ----------

def parse_research(text):
    refs, points, section, cur = {}, [], None, None
    for line in text.splitlines():
        h2 = re.match(r"^##\s+(.*)", line)
        if h2:
            title = h2.group(1)
            section = "refs" if "레퍼런스" in title else "points" if "반영할 점" in title else None
            cur = None
            continue
        if section == "refs":
            h3 = re.match(r"^###\s+(R\d+)\b", line)
            if h3:
                cur = h3.group(1)
                refs[cur] = ""
            elif cur:
                refs[cur] += line + "\n"
        elif section == "points":
            m = re.match(r"^\s*[-*]\s+(.*)", line)
            if m:
                points.append(m.group(1))
    return refs, points


def judge_research(path, rules):
    if not path.exists():
        return {g: missing("01-research.md") for g in ("G1-1", "G1-2", "G1-3")}
    refs, points = parse_research(path.read_text(encoding="utf-8"))
    r = rules["research"]
    n = len(refs)
    g1 = gate("pass" if r["min_refs"] <= n <= r["max_refs"] else "fail",
              [] if r["min_refs"] <= n <= r["max_refs"] else [f"레퍼런스 {n}개 (허용 {r['min_refs']}~{r['max_refs']})"], n)
    g2 = pass_or_fail([f"{rid}: {r['source_url_prefix']} 출처 없음"
                       for rid, body in refs.items() if r["source_url_prefix"] not in body])
    v3 = []
    if not points:
        v3.append("'## 반영할 점' 항목 0개")
    for p in points:
        ids = re.findall(r"R\d+", " ".join(re.findall(r"\[([^\]]*)\]", p)))
        if not ids:
            v3.append(f"레퍼런스 번호 없음: {p[:40]}")
        for rid in ids:
            if rid not in refs:
                v3.append(f"없는 레퍼런스 {rid}: {p[:40]}")
    return {"G1-1": g1, "G1-2": g2, "G1-3": pass_or_fail(v3)}


# ---------- G2 설계 ----------

def judge_spec(path, rules):
    if not path.exists():
        return {g: missing("02-spec.md") for g in ("G2-1", "G2-2", "G2-3")}
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^##\s+", text, flags=re.M)[1:]
    v1 = [f"PRD 근거 없음: ## {s.splitlines()[0].strip()}"
          for s in sections if not re.search(r"PRD\s*[:：]\s*\d+(-\d+)?", s)]
    if not sections:
        v1.append("'## ' 섹션 0개")
    v2 = [f"범위 밖 단어: {w}" for w in find_words(text, rules["out_of_scope_words"])]
    allowed = rules["allowed_status"]
    v3 = [f"범위 밖 상태 값: {t}" for t in find_tokens(text, rules.get("out_of_scope_status", []))]
    key_re = "|".join(map(re.escape, allowed))
    for m in re.finditer(rf"`?\b({key_re})\b`?\s*[:=]\s*((?:`?[a-z_]+`?)(?:\s*[/,|]\s*`?[a-z_]+`?)*)", text):
        key, vals = m.group(1), re.findall(r"[a-z_]+", m.group(2))
        v3 += [f"{key}에 없는 값: {v}" for v in vals if v not in allowed[key]]
    return {"G2-1": pass_or_fail(v1), "G2-2": pass_or_fail(v2), "G2-3": pass_or_fail(sorted(set(v3)))}


# ---------- G3 화면 ----------

class ScreenParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, attrs)]
        self.css = []            # <style> 내용
        self.inline = []         # style="" 내용
        self.svg_colors = []     # fill/stroke 속성 값
        self.texts = []          # 화면에 보이는 글자 + 텍스트 속성
        self.all_attr_values = []
        self.elements = []       # (tag, attrs, ancestors)
        self.meta_viewport = None
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        self.elements.append((tag, a, [x[1] for x in self.stack]))
        if a.get("style"):
            self.inline.append(a["style"])
        for k in ("fill", "stroke", "stop-color"):
            if k in a:
                self.svg_colors.append(a[k])
        for k in TEXT_ATTRS:
            if a.get(k):
                self.texts.append(a[k])
        self.all_attr_values += list(a.values())
        if tag == "meta" and a.get("name") == "viewport":
            self.meta_viewport = a.get("content", "")
        if tag in ("style", "script"):
            self._in = tag
        if tag not in VOID:
            self.stack.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._in = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._in == "style":
            self.css.append(data)
        elif self._in is None and data.strip():
            self.texts.append(data)


def css_declarations(parser):
    decls = []
    css = re.sub(r"/\*.*?\*/", "", "\n".join(parser.css), flags=re.S)
    blocks = re.findall(r"\{([^{}]*)\}", css) + parser.inline
    for block in blocks:
        for part in block.split(";"):
            if ":" in part:
                prop, val = part.split(":", 1)
                decls.append((prop.strip().lower(), val.strip()))
    return decls


def resolve_vars(decls):
    vars_ = {p: v for p, v in decls if p.startswith("--")}

    def sub(val, depth=0):
        if depth > 10 or "var(" not in val:
            return val
        def repl(m):
            name, fallback = m.group(1), m.group(2)
            return vars_.get(name, fallback.strip() if fallback else "")
        return sub(re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", repl, val), depth + 1)

    return [(p, sub(v)) for p, v in decls]


def color_violations(value, allowed, check_named):
    out = []
    for h in HEX.findall(value):
        if len(h) in (4, 8):
            out.append(f"투명도 포함 색 #{h}")
            continue
        full = ("#" + "".join(c * 2 for c in h) if len(h) == 3 else "#" + h).upper()
        if len(h) not in (3, 6) or full not in allowed:
            out.append(f"허용 밖 색 #{h}")
    if COLOR_FUNC.search(value):
        out.append(f"색 함수 사용: {value}")
    if check_named:
        for tok in re.findall(r"[a-zA-Z]+", value):
            if tok.lower() in NAMED_COLORS:
                out.append(f"이름 색 사용: {tok}")
    return out


def px_tokens(value):
    return [t for t in re.split(r"[\s/]+", value.strip()) if t]


def judge_screen(path, rules, screen):
    gates = ("G3-1", "G3-2", "G3-3", "G3-4", "G3-5", "G3-6", "G3-7", "G3-8", "G3-9", "G3-10")
    if not path.exists():
        return {g: missing("03-screen.html") for g in gates}
    p = ScreenParser()
    p.feed(path.read_text(encoding="utf-8"))
    decls = resolve_vars(css_declarations(p))
    res = {}

    # G3-1 뷰포트
    w, h = rules["viewport"]["width"], rules["viewport"]["height"]
    v = []
    if not p.meta_viewport or not re.search(rf"width\s*=\s*{w}\b", p.meta_viewport):
        v.append(f'<meta name="viewport" content="width={w}, ..."> 없음')
    roots = [a.get("data-viewport") for _, a, _ in p.elements if "data-viewport" in a]
    if f"{w}x{h}" not in roots:
        v.append(f'data-viewport="{w}x{h}" 요소 없음 (발견: {roots or "없음"})')
    res["G3-1"] = pass_or_fail(v)

    # G3-2 색
    allowed = flatten_colors(rules["colors"])
    v = []
    for prop, val in decls:
        if prop.startswith("--") or COLOR_PROPS.match(prop) or HEX.search(val) or COLOR_FUNC.search(val):
            v += [f"{prop}: {x}" for x in color_violations(val, allowed, bool(COLOR_PROPS.match(prop)))]
    for val in p.svg_colors:
        if val.lower() not in CSS_KEYWORDS:
            v += [f"svg: {x}" for x in color_violations(val, allowed, True)]
    res["G3-2"] = pass_or_fail(v)

    # G3-3 모서리
    radii = set(rules["radius_px"])
    v = []
    for prop, val in decls:
        if RADIUS_PROP.match(prop):
            for t in px_tokens(val):
                m = re.fullmatch(r"(\d+(?:\.\d+)?)px", t)
                if t in ("0", "inherit", "initial", "unset"):
                    continue
                if not m or float(m.group(1)) not in radii:
                    v.append(f"{prop}: {t}")
    res["G3-3"] = pass_or_fail(v)

    # G3-4 폰트·글자 크기
    families = {f.lower() for f in rules["font_family"]}
    sizes = set(rules["font_size_px"])
    v = []
    for prop, val in decls:
        if prop == "font":
            v.append(f"font 단축 속성 사용 금지: {val}")
        elif prop == "font-family":
            for f in val.split(","):
                name = f.strip().strip("'\"").lower()
                if name and name not in GENERIC_FONTS and name not in families:
                    v.append(f"허용 밖 폰트: {f.strip()}")
        elif prop == "font-size":
            m = re.fullmatch(r"(\d+(?:\.\d+)?)px", val)
            if val not in ("inherit", "initial", "unset") and (not m or float(m.group(1)) not in sizes):
                v.append(f"허용 밖 글자 크기: {val}")
    res["G3-4"] = pass_or_fail(v)

    # G3-5 그림자
    v = []
    if not rules.get("box_shadow_allowed", False):
        for prop, val in decls:
            if prop in ("box-shadow", "text-shadow") and val.lower() != "none":
                v.append(f"{prop}: {val}")
            elif "drop-shadow(" in val:
                v.append(f"{prop}: {val}")
    res["G3-5"] = pass_or_fail(v)

    # G3-6 간격 (warn)
    v = []
    for prop, val in decls:
        if SPACING_PROP.match(prop):
            for t in px_tokens(val):
                m = re.fullmatch(r"-?(\d+(?:\.\d+)?)px", t)
                if m and float(m.group(1)) % 4 != 0:
                    v.append(f"{prop}: {t}")
    res["G3-6"] = gate("warn" if v else "pass", v)

    # G3-7 ★② 범위 밖 단어
    text = " ".join(p.texts)
    res["G3-7"] = pass_or_fail([f"범위 밖 단어: {w}" for w in find_words(text, rules["out_of_scope_words"])])

    # G3-8 ★① 상태 값
    st = rules["allowed_status"]
    status_ok = set(st["review_status"]) | set(st["submission_status"])
    v = []
    for tag, a, _ in p.elements:
        if "data-status" in a and a["data-status"] not in status_ok:
            v.append(f'<{tag} data-status="{a["data-status"]}">')
        if "data-visibility" in a and a["data-visibility"] not in st["visibility"]:
            v.append(f'<{tag} data-visibility="{a["data-visibility"]}">')
    blob = " ".join(p.all_attr_values + p.texts)
    v += [f"범위 밖 상태 값: {t}" for t in find_tokens(blob, rules.get("out_of_scope_status", []))]
    res["G3-8"] = pass_or_fail(v)

    # G3-9 ★① 판매 신청은 seller만
    v = []
    for tag, a, anc in p.elements:
        is_sale = a.get("data-visibility") == "sale_requested" or a.get("value") == "sale_requested"
        if is_sale and not any(x.get("data-role") == "seller" for x in [a] + anc):
            v.append(f"<{tag}> sale_requested인데 data-role=\"seller\" 없음")
    res["G3-9"] = pass_or_fail(v)

    # G3-10 ★① 새 자산 기본 공개 범위는 private
    v = []
    forms = [a for _, a, _ in p.elements if a.get("data-form") == "new-asset"]
    for a in forms:
        if a.get("data-default-visibility") != "private":
            v.append(f'data-form="new-asset"의 data-default-visibility="{a.get("data-default-visibility", "")}"')
    for tag, a, anc in p.elements:
        in_form = any(x.get("data-form") == "new-asset" for x in anc)
        if not in_form:
            continue
        if tag == "input" and a.get("name") == "visibility" and "checked" in a and a.get("value") != "private":
            v.append(f'기본 선택 값이 {a.get("value")}')
        if tag == "option" and "selected" in a and any(x.get("name") == "visibility" for x in anc) \
                and a.get("value") != "private":
            v.append(f'기본 선택 값이 {a.get("value")}')
    g10 = pass_or_fail(v)
    if not forms and not v:
        g10["detail"] = ["새 자산 등록 폼 없음 — 검사 대상 아님"]
    res["G3-10"] = g10
    return res


# ---------- 종합 ----------

def judge(run_dir, rules, screen):
    run_dir = Path(run_dir)
    gates = {}
    gates.update(judge_research(run_dir / "01-research.md", rules))
    gates.update(judge_spec(run_dir / "02-spec.md", rules))
    gates.update(judge_screen(run_dir / "03-screen.html", rules, screen))
    failed = [g for g, r in gates.items() if r["status"] == "fail"]
    return {
        "screen": screen,
        "result": "fail" if failed else "pass",
        "failed": failed,
        "warned": [g for g, r in gates.items() if r["status"] == "warn"],
        "return_to": min(RETURN_STAGE[g] for g in failed) if failed else None,
        "gates": gates,
    }


def with_attempts(verdict, prev):
    attempts = dict((prev or {}).get("attempts", {"1": 0, "2": 0, "3": 0}))
    if verdict["return_to"]:
        k = str(verdict["return_to"])
        attempts[k] = attempts.get(k, 0) + 1
    verdict["attempts"] = attempts
    verdict["halt"] = bool(verdict["return_to"]) and attempts[str(verdict["return_to"])] >= MAX_ATTEMPTS
    return verdict


def main():
    ap = argparse.ArgumentParser(description="허들링 디자인 하네스 판정")
    ap.add_argument("screen")
    ap.add_argument("--rules", default=str(ROOT / "rules" / "rules.json"))
    ap.add_argument("--runs", default=str(ROOT / "runs"))
    ap.add_argument("--no-write", action="store_true", help="04-verdict.json을 쓰지 않는다")
    args = ap.parse_args()

    rules = load_rules(args.rules)
    if args.screen not in rules["screens"]:
        print(f"알 수 없는 화면: {args.screen} (가능: {', '.join(rules['screens'])})", file=sys.stderr)
        return 2
    run_dir = Path(args.runs) / args.screen
    verdict = judge(run_dir, rules, args.screen)

    out = run_dir / "04-verdict.json"
    if not args.no_write:
        prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
        verdict = with_attempts(verdict, prev)
        verdict["judged_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        run_dir.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mark = {"pass": "✅", "fail": "❌", "warn": "⚠️"}
    for g, r in verdict["gates"].items():
        print(f"{mark[r['status']]} {g:6} {r['status']:4}  " + "; ".join(r["detail"][:3]))
    print(f"\n결과: {verdict['result']}", end="")
    if verdict["return_to"]:
        print(f" → {verdict['return_to']}단계로 복귀", end="")
    if verdict.get("halt"):
        print(" (같은 단계 3회 복귀: 멈추고 사람에게 알림)", end="")
    print()
    return 0 if verdict["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
