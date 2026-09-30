# 하네스 검증과 리뷰 (harness-verify)

## 1. 판정 스크립트 검증 (tests/fixtures/, scripts/test_judge.py)
- 정상 HTML 1개 → G3 전부 pass
- 위반 HTML을 조건마다 1개씩 → 해당 조건만 fail
  - 필수 ★: G2-2, G2-3, G3-7, G3-8, G3-9, G3-10
  - 그 외: G3-1 뷰포트, G3-2 색, G3-3 모서리, G3-4 폰트/크기, G3-5 그림자, G3-6 간격(warn)
- G1·G2도 정상 1개 + 위반 1개 이상
- `scripts/test_judge.py` 한 번 실행으로 전부 통과해야 한다

## 2. 실제 실행
- 대상 화면: my-assets (★ 조건이 가장 많이 걸림)
- "내 자산 화면 만들어줘"로 1→2→3→4 실행

## 3. 리뷰 항목
| 항목 | 확인 방법 | 통과 |
|---|---|---|
| 편집 범위 | 에이전트별 자기 파일 외 변경 (git diff) | 0개 |
| 판정 정직성 | 04-verdict.json vs judge.py 재실행 결과 | 같음 |
| 복귀 동작 | fail 발생 시 harness-gates.md 표의 단계로 복귀 | 일치 |
| 화면 품질 | 브라우저 스크린샷 → 사람 승인 | 승인 |

- 편집 범위 위반이 나오면 훅으로 강제한다 (harness-roles.md).

## 4. 마무리
- 테스트 전부 통과 → 커밋 → GitHub 푸시 (runs/my-assets/ 포함)
