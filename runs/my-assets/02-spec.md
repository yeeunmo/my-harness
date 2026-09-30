# 화면 설계서 — my-assets

> 화면: 내 자산 (390×844). 데모 화면의 보는 사람은 판매 승인 회원(`seller`)으로 가정한다. 유료 회원(`paid`)에게는 `data-role="seller"`가 붙은 요소가 보이지 않는다.
> 상태 값은 `rules/rules.json`의 `allowed_status`만 쓴다. 새 자산의 기본 공개 범위는 `private`이다.

## 화면 루트와 헤더
- PRD: 5, 7-3, 7-4
- 구성: 화면 제목 "내 자산", 한 줄 설명 "내가 만든 프롬프트·스킬 파일·자동화 템플릿·사용 사례", 우측 상단 "새 자산" 필(pill) 버튼(액센트 채움), 역할 표시 칩 "판매 승인 회원"
- 데이터: 화면 루트 `<main data-screen="my-assets" data-viewer-role="seller">`; 역할 표시 칩에 `data-role="seller"`
- 동작: "새 자산"을 누르면 새 자산 등록 폼 섹션으로 이동한다.
- 반영 레퍼런스: [R2]

## 상태 필터 탭
- PRD: 6-5, 7-4
- 구성: 가로 필 탭 4개 — 전체 · 임시저장 · 검수 중 · 완료. 탭마다 오른쪽에 개수 배지. 선택된 탭만 검정 채움, 나머지는 외곽선.
- 데이터: review_status: draft / pending / revision_requested / approved / rejected
- 탭과 값 연결: 전체 = 모든 행, 임시저장 = `draft`, 검수 중 = `pending` / `revision_requested`, 완료 = `approved` / `rejected`
- 속성: 각 탭 `<button data-filter="all|draft|in-review|done" data-status-group="...">`; 검수 중·완료 탭은 판매 신청 흐름에만 해당하므로 `data-role="seller"`
- 반영 레퍼런스: [R4]

## 내 자산 목록
- PRD: 6-5, 8, 14
- 구성: 한 줄 행 목록(행 사이 얇은 구분선, 그림자 없음). 행 구성 = 자산 종류 라벨(작은 회색) · 제목(굵은 검정) · 공개 범위 라벨+값(예: "공개 범위 · 비공개") · 오른쪽 끝 심사 상태 배지 + 화살표(>)
- 데이터: visibility: private / member_only / sale_requested
- 데이터: review_status: draft / pending / revision_requested / approved / rejected
- 속성: 각 행 `<li data-asset-id="..." data-visibility="private|member_only|sale_requested" data-status="draft|pending|revision_requested|approved|rejected">`
  - 비공개·멤버 공개로 등록된 자산은 심사 대상이 아니므로 심사 배지를 두지 않고 `data-status`를 생략한다. 단, 임시저장 상태면 `data-status="draft"`를 붙인다.
  - `data-visibility="sale_requested"`인 행에는 `data-role="seller"`를 함께 붙인다.
- 배지 문구: `draft` 임시저장 · `pending` 검수 대기 · `revision_requested` 수정 요청 · `approved` 승인됨 · `rejected` 반려
- 배지 색: 모노크롬(회색 외곽선) 기본, 사용자가 행동해야 하는 `revision_requested`만 액센트(#D4FF3A) 채움. `approved`가 MVP 1차의 최종 상태이며 그 뒤 단계는 두지 않는다.
- 데모 행(최소 6개): 비공개 자산 1, 멤버 공개 자산 1, 판매 신청 자산 `draft`·`pending`·`revision_requested`·`approved`·`rejected` 각 1
- 반영 레퍼런스: [R1], [R2]

## 행 보조 문구
- PRD: 6-5, 6-7, 6-8
- 구성: 행 제목 아래 12px 회색 한 줄로 다음 행동을 안내
  - `draft`: "마지막 저장 2026.09.28 14:20"
  - `pending`: "운영자가 판매 기준 체크리스트로 검수하고 있어요"
  - `revision_requested`: "운영자 수정 요청을 확인하고 다시 제출하세요" + 운영자 검수 코멘트 한 줄 미리보기
  - `approved`: "검수를 통과했어요"
  - `rejected`: "반려 사유를 확인하세요"
- 데이터: review_status: draft / pending / revision_requested / approved / rejected
- 속성: 보조 문구 요소에 `data-hint-for="<status 값>"`; 운영자 코멘트 미리보기에 `data-field="review_comment"` `data-role="seller"`
- 반영 레퍼런스: [R1], [R4]

## 제출물에서 가져오기
- PRD: 6-4, 8
- 구성: 목록 위 얇은 안내 카드 "제출 완료된 미션 산출물을 자산으로 저장할 수 있어요" + 제출물 1~2개(미션 이름 · 제출물 제목 · 제출일) + 각 항목 오른쪽 "자산으로 저장" 외곽선 필 버튼
- 데이터: submission_status: submitted
- 속성: 각 항목 `<li data-submission-id="..." data-submission-status="submitted">`; "자산으로 저장" 버튼 `data-action="convert-to-asset"` `data-default-visibility="private"` (전환된 자산도 비공개로 시작)
- 규칙: 작성 중(`draft`) 제출물은 이 영역에 보이지 않는다.
- 반영 레퍼런스: [R4]

## 새 자산 등록 폼
- PRD: 6-5, 8, 14
- 구성: 자산 종류 필 칩(프롬프트 · 스킬 파일 · 자동화 템플릿 · 사용 사례, 단일 선택) → 제목 (필수, 0/30 카운터) → 설명 (필수, 0/200 카운터) → 사용 방법 (선택) → 파일 첨부 → 공개 범위 선택 → 하단 버튼
- 데이터: visibility: private / member_only / sale_requested
- 데이터: review_status: draft
- 속성: 폼 `<form data-form="new-asset" data-default-visibility="private">`; 각 입력에 `data-field="category|title|description|usage_guide"`
- 입력 라벨에 필수/선택을 적고, 글자 수 카운터를 입력칸 오른쪽 아래에 둔다.
- 반영 레퍼런스: [R3]

## 공개 범위 선택
- PRD: 6-5, 7-3, 7-4, 9, 14
- 구성: 필 칩 3개 — 비공개(기본 선택) · 멤버 공개 · 판매 신청. 선택된 칩만 검정 테두리·굵은 글자. 칩 아래 한 줄 설명
  - 비공개: "나만 볼 수 있어요"
  - 멤버 공개: "유료 멤버가 볼 수 있어요"
  - 판매 신청: "등록하면 운영자 검수 대기로 넘어가요"
- 데이터: visibility: private / member_only / sale_requested
- 속성: 칩 그룹 `data-group="visibility"`; 각 칩 `data-visibility="private|member_only|sale_requested"`; 첫 화면에서 `private` 칩이 `aria-pressed="true"`
- 권한: 판매 신청 칩과 그 설명에는 `data-role="seller"`를 붙인다. 판매 승인 회원에게만 렌더링되며, 유료 회원 화면에서는 이 칩이 아예 없다(비공개 · 멤버 공개 2개만 보임). 데모는 `seller` 기준이므로 3개 모두 보인다.
- 반영 레퍼런스: [R2], [R3]

## 파일 첨부
- PRD: 6-5, 8
- 구성: "+" 아이콘이 달린 첨부 행 "파일 추가 +", "예시 결과 추가 +". 첨부된 파일은 같은 영역에 파일명 · 용량 · 삭제(×) 행으로 쌓는다.
- 데이터: 첨부 행 `data-field="files"` / `data-field="example_output"`; 첨부된 파일 행 `data-file-name="..."`
- 반영 레퍼런스: [R5]

## 하단 고정 버튼
- PRD: 6-5, 7-4
- 구성: 폭 전체를 나누는 두 버튼 — "임시저장"(흰 배경 외곽선, radius 999) · "등록"(액센트 채움, radius 999)
- 데이터: review_status: draft / pending
- 속성: 임시저장 `data-action="save-draft" data-status="draft"`; 등록 `data-action="register"`
- 규칙: 임시저장은 `draft`로 남는다. 공개 범위가 `sale_requested`일 때만 등록 시 `pending`(검수 대기)으로 넘어가며, 이 안내 문구 "등록하면 검수 대기로 넘어가요"에는 `data-role="seller"`를 붙인다. 비공개·멤버 공개는 등록 즉시 저장된다.
- 반영 레퍼런스: [R3], [R5]

## 빈 상태
- PRD: 6-5
- 구성: 자산이 하나도 없을 때 목록 자리에 "첫 자산을 등록해 보세요" 문구 + "새 자산" 필 버튼. 제출 완료된 제출물이 있으면 "제출물에서 가져오기"도 함께 안내.
- 데이터: `data-empty="my-assets"` (데모에서는 숨김 처리 `hidden`으로 마크업만 포함)
- 반영 레퍼런스: [R2], [R4]
