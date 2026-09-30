# 하네스 역할 (harness-roles)

## 에이전트 (단계당 1개, 편집은 자기 파일 1개만)
| 에이전트 | 단계 | 편집 가능 | 읽기 | 도구 |
|---|---|---|---|---|
| researcher | 1 리서치 | runs/<화면>/01-research.md | prd.md, rules.json | uibowl 검색, Read, Write |
| spec-writer | 2 설계 | runs/<화면>/02-spec.md | 01, prd.md, story-service.md, rules.json | Read, Write |
| screen-maker | 3 제작 | runs/<화면>/03-screen.html | 02, design.md, rules.json | Read, Write |
| judge | 4 판정 | 없음 (읽기전용) | runs/<화면>/ 전체, rules.json | Read, Bash(scripts/judge.py 실행만) |

- `rules/`, `docs/`, `scripts/`는 어떤 에이전트도 수정하지 않는다.
- 편집 범위는 에이전트 지시문으로 지킨다. R8 검증에서 위반이 나오면 훅으로 강제한다.

## 판정자
- `scripts/judge.py`가 rules.json을 읽고 G1~G3를 세서 `04-verdict.json`을 쓴다.
- judge 에이전트는 스크립트를 실행하고 결과를 요약만 한다. 판정 결과를 바꾸지 않는다.

## 자연어 트리거
| 말 | 동작 |
|---|---|
| "<화면> 만들어줘" | 1→2→3→4 실행 (있는 단계는 건너뜀) |
| "<화면> 판정해줘" | 4 판정만 |
| "승인" | approval.md 생성 |
| "수정: <코멘트>" | 3 제작부터 다시 |
| "진행 상황" | 화면별 단계 상태 표 |

화면 이름: 홈=`home`, 스킬 라이브러리=`skill-library`, 미션 상세=`mission-detail`, 내 자산=`my-assets`
