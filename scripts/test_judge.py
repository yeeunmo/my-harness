#!/usr/bin/env python3
"""judge.py 검증 (docs/harness-verify.md 1번).

tests/fixtures/good/ 의 정상 파일은 전부 pass여야 하고,
조건마다 한 곳만 망가뜨린 사본은 그 조건만 fail(또는 warn)이어야 한다.

사용: python3 scripts/test_judge.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GOOD = ROOT / "tests" / "fixtures" / "good"
RULES = judge.load_rules(ROOT / "rules" / "rules.json")

R, S, H = "01-research.md", "02-spec.md", "03-screen.html"

# (이름, 기대 게이트, 기대 상태, 파일, 바꿀 문자열, 새 문자열)
CASES = [
    ("레퍼런스 2개", "G1-1", "fail", R,
     "### R3 · 앱C — 상태 배지\n- url: https://uibowl.io/example/3\n- 관찰: 카드 우상단 배지로 검수 상태를 보여준다.\n", ""),
    ("uibowl 출처 없음", "G1-2", "fail", R, "https://uibowl.io/example/2", "https://example.com/2"),
    ("반영할 점에 번호 없음", "G1-3", "fail", R, "- [R1] 상태별", "- 상태별"),
    ("PRD 근거 없는 섹션", "G2-1", "fail", S, "## 헤더\n- PRD: 5, 6-5\n", "## 헤더\n"),
    ("★ 설계서에 범위 밖 단어", "G2-2", "fail", S, "새 자산 등록 버튼", "새 자산 등록 버튼, 허들링 픽 바로가기"),
    ("★ 설계서에 없는 상태 값", "G2-3", "fail", S,
     "visibility: private / member_only / sale_requested", "visibility: private / member_only / sale_requested / for_sale"),
    ("뷰포트 375×812", "G3-1", "fail", H, 'data-viewport="390x844"', 'data-viewport="375x812"'),
    ("허용 밖 색", "G3-2", "fail", H, "--accent: #D4FF3A;", "--accent: #D4FF3A; --danger: #FF0000;"),
    ("모서리 8px", "G3-3", "fail", H, "--r-card: 12px", "--r-card: 8px"),
    ("글자 크기 15px", "G3-4", "fail", H, ".sub { color: var(--sub); font-size: 14px; }",
     ".sub { color: var(--sub); font-size: 15px; }"),
    ("허용 밖 폰트", "G3-4", "fail", H, "font-family: Pretendard, sans-serif", "font-family: Inter, sans-serif"),
    ("그림자", "G3-5", "fail", H, ".card { background: var(--surface);",
     ".card { box-shadow: 0 2px 8px #0A0A0A; background: var(--surface);"),
    ("간격 10px (warn)", "G3-6", "warn", H, "padding: 8px 12px", "padding: 10px 12px"),
    ("★ 화면에 범위 밖 단어", "G3-7", "fail", H, "<h1>내 자산</h1>", "<h1>내 자산</h1><a>구매 내역</a>"),
    ("★ 허용 밖 상태 값", "G3-8", "fail", H, 'data-status="approved">승인됨', 'data-status="selling">판매중'),
    ("★ 판매 신청인데 seller 없음", "G3-9", "fail", H,
     'data-visibility="sale_requested" data-status="pending" data-role="seller"',
     'data-visibility="sale_requested" data-status="pending"'),
    ("★ 새 자산 기본값이 멤버 공개", "G3-10", "fail", H,
     'data-default-visibility="private"', 'data-default-visibility="member_only"'),
    ("★ 새 자산 기본 선택이 판매 신청", "G3-10", "fail", H,
     'value="private" checked> 비공개', 'value="private"> 비공개'),
]


def run_case(tmp, name, target, expect, fname, old, new):
    d = Path(tmp) / name.replace(" ", "_")
    shutil.copytree(GOOD, d)
    p = d / fname
    text = p.read_text(encoding="utf-8")
    assert old in text, f"[{name}] 바꿀 문자열을 fixture에서 못 찾음: {old[:40]}"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    if name.startswith("★ 새 자산 기본 선택"):
        # 판매 신청 라디오를 기본 선택으로 (seller 라벨 안이므로 G3-9는 통과)
        p.write_text(p.read_text(encoding="utf-8").replace('value="sale_requested">', 'value="sale_requested" checked>'),
                     encoding="utf-8")
    v = judge.judge(d, RULES, "my-assets")
    got = v["gates"][target]["status"]
    others = [g for g, r in v["gates"].items() if g != target and r["status"] != "pass"]
    ok = got == expect and not others
    return ok, got, others, v["gates"][target]["detail"]


def main():
    good = judge.judge(GOOD, RULES, "my-assets")
    bad_good = [g for g, r in good["gates"].items() if r["status"] != "pass"]
    results = [("정상 파일 전부 pass", not bad_good, "pass" if not bad_good else f"실패: {bad_good}")]
    with tempfile.TemporaryDirectory() as tmp:
        for case in CASES:
            ok, got, others, detail = run_case(tmp, *case)
            note = f"{case[1]}={got}" + (f", 다른 게이트도 걸림: {others}" if others else "") + \
                   (f"  ({detail[0]})" if detail else "")
            results.append((case[0], ok, note))
    for name, ok, note in results:
        print(f"{'✅' if ok else '❌'} {name:28} {note}")
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - failed}/{len(results)} 통과")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
