# 하네스 오케스트레이터 (harness-orchestrator)

## 누가
- 메인 Claude 세션. 프로젝트를 열면 CLAUDE.md를 읽고 트리거를 받는다.

## 하는 일 / 안 하는 일
| 한다 | 안 한다 |
|---|---|
| 트리거 해석, 화면 이름 매핑 | 01~03 산출물 직접 작성 |
| 단계 순서 결정, 에이전트 호출 | 04-verdict.json 수정 |
| 판정 결과 요약 보고, 브라우저로 화면 열기 | rules/, docs/, scripts/ 수정 |
| "승인" 시 approval.md 작성 (유일하게 직접 쓰는 파일) | 사람 승인 없이 완료 처리 |

## 상태 판단 (상태 파일 없음, 매번 runs/<화면>/ 을 본다)
1. approval.md 있음 → 완료, 건너뜀
2. 04-verdict.json에 fail 있음 → 실패 조건의 복귀 단계로 (harness-gates.md 표)
3. 그 외 → 없는 파일 중 가장 앞 번호 단계부터
4. 04-verdict.json의 attempts가 같은 단계로 3회 → 멈추고 사람에게 알림
5. G3 전부 pass → 03-screen.html을 브라우저로 열고 "승인 / 수정: <코멘트>"를 기다림

## CLAUDE.md 원칙
- 짧게: 트리거, 단계 순서, 금지 사항만
- 세부 규칙은 링크: docs/harness-*.md, rules/rules.json (SSOT)

## 만들 파일 (R8에서 생성·검증)
- CLAUDE.md
- .claude/agents/researcher.md, spec-writer.md, screen-maker.md, judge.md
- scripts/judge.py
