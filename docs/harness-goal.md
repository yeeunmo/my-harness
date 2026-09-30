# 하네스 목적 (harness-goal)

## 매번 달라지는 것 (입력)
- 만들 화면 이름 1개: `home` | `skill-library` | `mission-detail` | `my-assets`
- 고정 입력(매번 같음): docs/prd.md, docs/design.md, docs/story-service.md, docs/story-work.md

## 사용자
- 나(디자이너). 수업 제출용.
- 개발자 전달은 이번 범위 밖.

## 결과물 형태
- HTML 1개, 뷰포트 390×844
- Figma는 이번 범위 밖 (필요하면 나중에 HTML → Figma 단계를 추가)

## 완료 기준 (한 문장)
요청한 화면의 390×844 HTML이 있고, design.md 밖의 색·모서리·폰트 값이 0개,
MVP 범위 밖 단어가 0개, 반영한 레퍼런스마다 출처가 1개 이상 있으며, 사람 1명이 승인했다.

## 완료 기준 → 셀 수 있는 조건
| # | 조건 | 통과 값 | 연결 |
|---|---|---|---|
| D1 | 결과 HTML 파일 존재 | 1개 | — |
| D2 | 뷰포트 너비·높이 | 390 × 844 | story-work ④ |
| D3 | design.md에 없는 색·모서리·폰트 값 | 0개 | story-work ⑦ 멈칫 |
| D4 | MVP 범위 밖 단어 (허들링 픽, 구매, 결제, 정산, 피드백, 판매 중, 판매 중지) | 0개 | story-service 어기면 안 되는 것 ② |
| D5 | 반영할 점 중 출처 레퍼런스가 없는 항목 | 0개 | story-work ② 멈칫 |
| D6 | 사람 승인 기록 | 1건 | story-work ⑤ 넘김 |

> story-service "어기면 안 되는 것 ①(권한·상태)"은 R5에서 게이트 조건으로 추가한다.
