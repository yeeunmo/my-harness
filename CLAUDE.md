# 허들링 앱 디자인 하네스

허들링 앱 화면 1개를 리서치 → 설계 → 제작 → 판정 순서로 만든다.
세부 규칙은 아래 문서가 기준이며, 이 파일에 옮겨 적지 않는다.

- 규칙 SSOT: `rules/rules.json` (값이 다르면 이 파일이 이긴다)
- 판정 기준: `docs/story-service.md` ("어기면 안 되는 것")
- 목적·파이프라인·산출물·게이트·역할: `docs/harness-*.md`

## 화면 이름
홈=`home` · 스킬 라이브러리=`skill-library` · 미션 상세=`mission-detail` · 내 자산=`my-assets`

## 트리거
| 말 | 동작 |
|---|---|
| "<화면> 만들어줘" | 아래 순서대로 실행. 있는 단계는 건너뛴다 |
| "<화면> 판정해줘" | 4 판정만 |
| "승인" | `runs/<화면>/approval.md` 작성 (승인자, 날짜, 코멘트) |
| "수정: <코멘트>" | 코멘트를 넘겨 3 제작부터 다시 |
| "진행 상황" | 화면별 단계 상태 표 |

## 순서 (`runs/<화면>/`)
| # | 에이전트 (`.claude/agents/`) | 쓰는 파일 |
|---|---|---|
| 1 | researcher | 01-research.md |
| 2 | spec-writer | 02-spec.md |
| 3 | screen-maker | 03-screen.html |
| 4 | judge → `python3 scripts/judge.py <화면>` | 04-verdict.json |

어디서 시작할지:
1. approval.md 있음 → 완료
2. 04-verdict.json에 fail → 그 파일의 `return_to` 단계로 (그 뒤 단계 전부 다시)
3. 그 외 → 없는 파일 중 가장 앞 번호부터
4. 04-verdict.json의 `halt`가 true (같은 단계로 3번 되돌아감) → 멈추고 나에게 알린다
5. G3 전부 pass → 03-screen.html을 브라우저로 열고 "승인 / 수정"을 기다린다

## 금지
- 오케스트레이터는 01~03을 직접 쓰지 않는다. 반드시 해당 에이전트에게 넘긴다.
- 04-verdict.json은 judge.py만 쓴다. 누구도 손으로 고치지 않는다.
- rules/, docs/, scripts/는 하네스 실행 중에 수정하지 않는다.
- 사람 승인 없이 완료 처리하지 않는다.
- MVP 범위 밖 기능(허들링 픽, 구매, 결제, 정산, 피드백 등)을 만들지 않는다.
