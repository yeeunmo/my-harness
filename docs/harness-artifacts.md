# 하네스 산출물 (harness-artifacts)

## 단계별 파일 (화면마다 폴더 1개)
```
runs/<화면이름>/
├── 01-research.md    # 1 리서치: 레퍼런스 3~5개 + 반영할 점 + uibowl URL
├── 02-spec.md        # 2 설계: 섹션, 기능, 데이터 필드, PRD 근거 번호
├── 03-screen.html    # 3 제작: 390×844 HTML
├── 04-verdict.json   # 4 판정: 조건별 pass/fail, 위반 목록
└── approval.md       # 사람 승인 기록 (승인자, 날짜, 한 줄 코멘트)
```

화면이름: `home` | `skill-library` | `mission-detail` | `my-assets`

## 규칙 SSOT
- `rules/rules.json` 하나만 기준이다. 판정 스크립트는 이 파일만 읽는다.
- `docs/design.md`는 사람이 읽는 설명서다. 값이 다르면 rules.json이 이긴다.
- 규칙을 바꿀 때는 rules.json을 먼저 고치고, design.md를 맞춘다.

## 재개
- 판정 기록은 `04-verdict.json` 한 곳에만 남긴다.
- 다시 실행하면 파일이 없거나 판정 실패한 첫 단계부터 이어서 한다.
- `approval.md`가 있으면 그 화면은 완료로 보고 건너뛴다.
