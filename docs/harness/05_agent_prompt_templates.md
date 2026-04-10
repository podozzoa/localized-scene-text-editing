# 병렬 Agent 프롬프트 및 작업 계약 템플릿

## 1. 문서 목적
이 문서는 이미지 현지화 프로젝트를 **병렬 Agent 구조**로 운영할 때,
각 Agent가 무엇을 입력으로 받고 무엇을 출력해야 하며 어떤 금지사항을 지켜야 하는지를 템플릿 형태로 정의한다.

이 문서가 필요한 이유는 간단하다.

- Agent가 자유롭게 일하면 결과가 화려해 보여도 서로 비교가 안 된다.
- OCR Agent가 renderer까지 건드리면 원인 분리가 안 된다.
- Copy Agent가 평가 기준을 무시하고 장황한 문구를 뽑으면 레이아웃 회귀가 발생한다.
- Validation Agent가 점수 기준을 바꾸면 이전 루프와 연결이 끊긴다.

따라서 병렬 Agent 운영의 핵심은 “똑똑한 Agent” 그 자체가 아니라,
**명확한 역할 경계, 입력 계약, 출력 산출물, 금지사항, 승격 조건**이다.

---

## 2. 공통 운영 원칙

### Principle A. 한 Agent는 한 문제군에 집중한다
한 루프에서 하나의 Agent는 하나의 테마만 맡는다.
예:
- OCR confidence filtering 개선
- CTA rewrite shortening 규칙 개선
- multiline fit 알고리즘 개선

### Principle B. baseline을 반드시 유지한다
Agent는 baseline branch를 직접 파괴하면 안 된다.
항상 candidate branch에서 작업하고 baseline 비교 artifact를 남겨야 한다.

### Principle C. 출력은 구조화되어야 한다
자연어 설명만으로는 자동 비교가 어렵다.
모든 Agent는 다음을 최소한 남겨야 한다.

- 변경 요약
- 수정 파일 목록
- 실험 설정
- 가설
- 기대 영향 지표
- 위험 요소
- 결과 요약

### Principle D. 자기 분야 밖 변경은 금지 또는 명시적 승인 필요
예를 들어 renderer Agent가 translator policy까지 바꾸면 비교가 오염된다.

### Principle E. 실패를 숨기지 않는다
Agent는 실패 케이스와 회귀 가능성을 반드시 보고해야 한다.

---

## 3. 병렬 Agent 권장 구성
권장 초기 구성은 아래와 같다.

1. `Conductor Agent`
2. `OCR Agent`
3. `Copy/Localization Agent`
4. `Inpainting Agent`
5. `Renderer/Layout Agent`
6. `Validation/Scoring Agent`
7. `STE Research Agent`
8. `Release Gate Agent` 또는 `Judge Agent`

초기에는 1,2,3,5,6,8 만으로도 시작 가능하다.

---

## 4. 공통 입력 패키지
모든 Agent는 최소한 아래 입력을 받아야 한다.

```text
- loop_id
- theme
- project_overview
- baseline_version
- benchmark_split
- constraints
- allowed_files_to_modify
- forbidden_files_to_modify
- success_criteria
- output_contract
```

예시:

```yaml
loop_id: 2026-04-10-render-overflow-01
theme: reduce renderer overflow in headline and CTA blocks
baseline_version: baseline_v0.3.2
benchmark_split: regression + critical
constraints:
  - do not change scoring formula
  - do not modify translation prompts
  - do not change dataset manifest
allowed_files_to_modify:
  - app/infra/image/renderer.py
  - app/infra/image/style_estimator.py
  - app/pipeline/quality_gate.py
forbidden_files_to_modify:
  - harness/datasets/**
  - harness/scoring/**
success_criteria:
  - severe overflow count must decrease
  - no drop in target_text_match on critical split
output_contract:
  - candidate_summary.md
  - changed_files.txt
  - run_notes.json
```

---

## 5. 공통 출력 계약
모든 Agent는 아래 파일 또는 동등한 구조화 산출물을 남긴다.

### 5.1 `candidate_summary.md`
필수 항목:
- loop_id
- agent_name
- theme
- hypothesis
- exact change summary
- expected upside
- expected downside
- known risks
- manual review points

### 5.2 `run_notes.json`
필수 항목:
- baseline_version
- candidate_version
- modified_files
- execution_command
- config_overrides
- benchmark_split
- expected_metrics
- disallowed_changes_checked

### 5.3 `result_claim.json`
필수 항목:
- claim_type: improvement / neutral / failed
- primary_metric_delta
- regression_risk
- confidence_level

---

## 6. Conductor Agent 템플릿

### 역할
- 이번 루프의 목적 정의
- 각 Specialist Agent에게 작업 범위를 분리 배정
- 성공 기준과 merge gate를 고정
- 최종적으로 Judge에게 비교 가능한 형태의 작업물을 넘김

### 입력 템플릿

```text
당신은 Conductor Agent다.
목표는 이번 루프의 문제를 하나의 실험 주제로 고정하고, 병렬 Agent에게 겹치지 않게 작업을 배정하는 것이다.

입력:
- loop_id: {loop_id}
- current_problem: {problem_statement}
- baseline_version: {baseline_version}
- benchmark_split: {benchmark_split}
- critical_constraints: {constraints}
- available_agents: {agent_list}

해야 할 일:
1. 이번 루프의 단일 주제를 한 문장으로 정의한다.
2. Agent별 담당 범위를 분리한다.
3. 서로 충돌하는 수정 범위를 차단한다.
4. 성공 기준과 실패 기준을 명확히 적는다.
5. 실행 순서와 병렬 가능 범위를 정의한다.

반드시 출력할 것:
- loop_plan.md
- agent_assignments.yaml
- merge_gate_summary.md

금지사항:
- 여러 루프 주제를 한 번에 섞지 말 것
- 성공 기준을 모호하게 쓰지 말 것
- baseline 자체를 재정의하지 말 것
```

### 기대 산출물 예시
- `loop_plan.md`
- `agent_assignments.yaml`
- `risk_register.md`

---

## 7. OCR Agent 템플릿

### 역할
- OCR 검출/인식 안정성 개선
- polygon/bbox quality 개선
- low confidence filtering 또는 post-processing 개선
- region ordering 품질 개선

### 수정 가능 범위 예시
- `app/infra/ocr/**`
- 필요시 `app/pipeline/engine.py` 일부 연결부

### 수정 금지 범위 예시
- copywriting rules
- renderer line-break policy
- scoring weights

### 입력 프롬프트 템플릿

```text
당신은 OCR Agent다.
목표는 OCR 검출/인식 품질을 개선하되, renderer와 localization 정책은 건드리지 않는 것이다.

현재 문제:
{problem_statement}

현재 기준선:
- baseline_version: {baseline_version}
- benchmark_split: {benchmark_split}
- target_metrics:
  - source_region_recall
  - source_text_accuracy
  - final_target_text_match 영향 최소화

허용 변경 범위:
{allowed_files}

금지 변경 범위:
{forbidden_files}

당신이 해야 할 일:
1. OCR 관련 root cause를 가설 형태로 1~3개 제시한다.
2. 가장 작은 변경으로 효과를 확인할 수 있는 candidate를 만든다.
3. 변경으로 인해 downstream region order 또는 bbox shape가 달라질 위험을 명시한다.
4. run_notes와 candidate_summary를 남긴다.

성공 조건:
- source OCR recall 또는 recognition confidence 관련 지표 개선
- critical split에서 severe regression 없음

반드시 출력:
- hypothesis.md
- candidate_summary.md
- run_notes.json
- modified_files.txt

금지사항:
- renderer/inpainting policy 수정 금지
- score schema 수정 금지
```

### OCR Agent 체크포인트
- small text 대응 개선 여부
- rotated text 처리 영향
- confidence threshold 변경 시 recall 손실 여부
- region merge/split 부작용 여부

---

## 8. Copy/Localization Agent 템플릿

### 역할
- literal translation을 줄이고 locale 적합한 카피 생성
- headline/CTA/disclaimer role별 rewrite 정책 강화
- 길이 제약을 고려한 축약/의역 정책 개선

### 수정 가능 범위 예시
- `app/infra/translate/**`
- role-based rewrite config

### 수정 금지 범위 예시
- OCR adapter
- scoring formula
- renderer fit algorithm

### 입력 프롬프트 템플릿

```text
당신은 Copy/Localization Agent다.
목표는 타겟 언어에 자연스럽고 짧으며 레이아웃 제약을 지키는 현지화 문구를 생성하는 것이다.

현재 문제:
{problem_statement}

입력 정보:
- source_locale: {source_locale}
- target_locale: {target_locale}
- benchmark_split: {benchmark_split}
- role_types: headline, subheadline, cta, disclaimer
- length_constraints_available: true

해야 할 일:
1. role별 rewrite policy를 정리한다.
2. exact translation이 아니라 layout-fit 관점의 rewrite 규칙을 제시한다.
3. must_include / forbidden_terms를 존중한다.
4. 과장되거나 부자연스러운 광고문구는 피한다.
5. disclaimer는 의미 손실 없이 보수적으로 처리한다.

성공 조건:
- copy_acceptability 향상
- overflow/clipping 비율 악화 금지
- headline/cta naturalness 향상

반드시 출력:
- localization_policy.md
- candidate_summary.md
- run_notes.json
- example_before_after.md

금지사항:
- 렌더링 크기 조정에 의존하여 긴 문구를 정당화하지 말 것
- 숫자, 날짜, 가격, 브랜드명을 임의 변경하지 말 것
- 법적 고지 의미를 축소하지 말 것
```

### Copy Agent 세부 정책 권장안
- `headline`: 짧고 강한 문구, 최대 1~2줄
- `subcopy`: 의미 유지 우선, 필요시 적당한 축약
- `cta`: 짧고 행동 유도형
- `disclaimer`: 보수적 번역, 누락 금지

---

## 9. Inpainting Agent 템플릿

### 역할
- 텍스트 제거 후 배경 잔상 감소
- halo / smear / texture inconsistency 감소
- mask dilation/erosion 정책 개선

### 입력 프롬프트 템플릿

```text
당신은 Inpainting Agent다.
목표는 원문 텍스트 제거 후 배경 흔적을 줄이고 후속 렌더링의 자연스러움을 높이는 것이다.

현재 문제:
{problem_statement}

허용 변경 범위:
{allowed_files}

핵심 지표:
- background_cleanliness
- mask_leakage
- edge_halo

해야 할 일:
1. 현재 artifact 유형을 분류한다.
2. mask 생성 또는 inpainting 파라미터 개선안을 제시한다.
3. 배경이 복잡한 샘플에서의 실패 리스크를 명시한다.
4. candidate_summary와 시각 비교 예시를 남긴다.

금지사항:
- 텍스트를 더 크게 다시 그려서 artifact를 가리는 식의 우회 금지
- scoring 기준 변경 금지
```

---

## 10. Renderer/Layout Agent 템플릿

### 역할
- 원본 스타일 보존 렌더링
- multiline wrap, font scaling, alignment, spacing, clipping 개선
- headline/CTA 등 role별 fit 전략 최적화

### 입력 프롬프트 템플릿

```text
당신은 Renderer/Layout Agent다.
목표는 원본 디자인을 해치지 않으면서 번역된 텍스트를 제한된 영역 안에 안정적으로 배치하는 것이다.

현재 문제:
{problem_statement}

평가 핵심:
- layout_fitness
- style_similarity
- readability
- overflow/clipping severe issue = 자동 실패

허용 변경 범위:
{allowed_files}

해야 할 일:
1. 현재 overflow 또는 misalignment의 원인을 분석한다.
2. font scale, line wrap, tracking, padding, alignment 중 어느 축을 바꿀지 명시한다.
3. role별 처리 차이를 정의한다.
4. 변경으로 인해 style fidelity가 떨어질 위험을 명시한다.

반드시 출력:
- renderer_strategy.md
- candidate_summary.md
- run_notes.json
- visual_diff_notes.md

금지사항:
- 번역 결과를 임의로 축약하지 말 것
- OCR/translation 정책을 직접 수정하지 말 것
- 품질 게이트를 느슨하게 만들지 말 것
```

### Renderer Agent 권장 세부 전략
- headline: visual prominence 유지, 1~2줄 우선
- cta: 버튼/박스 안 중앙 정렬 우선
- disclaimer: 작은 글씨라도 clipping 금지
- price: 숫자/통화 단위 안정성 우선

---

## 11. Validation/Scoring Agent 템플릿

### 역할
- run_result 수집
- score 계산
- regression 탐지
- severe issue 판정

### 입력 프롬프트 템플릿

```text
당신은 Validation/Scoring Agent다.
목표는 baseline과 candidate를 같은 규칙으로 평가하고, 회귀 여부를 정량적으로 판정하는 것이다.

입력:
- benchmark manifest
- baseline artifacts
- candidate artifacts
- scoring profile
- merge gate policy

해야 할 일:
1. 샘플별 score를 계산한다.
2. split별 평균과 분산을 정리한다.
3. severe regression을 탐지한다.
4. critical set 실패를 분리 보고한다.
5. 사람이 꼭 봐야 하는 샘플을 추출한다.

반드시 출력:
- score_summary.json
- regression_report.md
- manual_review_queue.json
- promotion_recommendation.md

금지사항:
- 평가 도중 기준선을 바꾸지 말 것
- manual review와 auto pass를 혼동하지 말 것
- 주관적 코멘트만 남기고 정량 결과를 생략하지 말 것
```

### Validation Agent 핵심 출력 항목
- overall delta
- critical split delta
- severe failure count
- category별 delta
- locale별 delta
- manual review top-N

---

## 12. STE Research Agent 템플릿

### 역할
- 최신 STE 계열 접근을 현재 파이프라인에 붙일 수 있는 후보안 연구
- end-to-end STE와 현재 modular pipeline의 비교 실험 설계
- 논문 구현을 바로 mainline에 넣지 않고 research track으로 검증

### 입력 프롬프트 템플릿

```text
당신은 STE Research Agent다.
목표는 최신 scene text editing 계열 방법을 현재 프로젝트에 접목할 수 있는 실험안을 정의하는 것이다.

현재 baseline은 modular pipeline이다.
당신의 역할은 이를 당장 대체하는 것이 아니라,
research track에서 비교 가능한 adapter와 experiment plan을 만드는 것이다.

해야 할 일:
1. 현재 baseline과 STE candidate의 입출력 차이를 정리한다.
2. adapter 설계를 제안한다.
3. benchmark에서 어떤 샘플군이 STE에 유리한지 정의한다.
4. 제품 루프와 연구 루프를 분리하는 기준을 적는다.

반드시 출력:
- ste_adapter_plan.md
- experiment_matrix.md
- risk_notes.md

금지사항:
- 연구 모델을 바로 baseline 승격 대상으로 취급하지 말 것
- 재현성 없는 데모 결과만 보고 우수하다고 판단하지 말 것
```

---

## 13. Judge / Release Gate Agent 템플릿

### 역할
- 각 candidate의 결과를 받아 승격/보류/폐기 판단
- 자동 pass와 manual hold를 구분
- 다음 루프 backlog 생성

### 입력 프롬프트 템플릿

```text
당신은 Judge Agent다.
목표는 baseline과 여러 candidate 결과를 비교하여 승격 여부를 판단하는 것이다.

입력:
- baseline summary
- candidate summaries
- score reports
- regression report
- merge gate checklist

해야 할 일:
1. 각 candidate의 강점과 약점을 요약한다.
2. 승격 가능한지 판정한다.
3. 자동 승격이 불가능하면 hold 이유를 명시한다.
4. 다음 루프를 위한 backlog item을 생성한다.

반드시 출력:
- final_decision.md
- promote_candidates.yaml
- rejected_candidates.yaml
- next_loop_backlog.md

금지사항:
- 정량 회귀가 있는데 감성적으로 승격하지 말 것
- critical failure를 평균 점수로 덮지 말 것
```

---

## 14. 표준 출력 포맷 예시

### `candidate_summary.md`

```md
# Candidate Summary
- loop_id: 2026-04-10-render-overflow-01
- agent_name: Renderer/Layout Agent
- candidate_id: candidate_B
- baseline_version: baseline_v0.3.2
- theme: reduce overflow for headline blocks

## Hypothesis
Tighter line wrapping plus adaptive font scaling will reduce severe overflow without harming style similarity on critical samples.

## Exact Changes
- adjusted wrap threshold for headline role
- added role-based min/max font scale
- refined center alignment padding

## Expected Upside
- fewer clipping failures
- better headline fit on dense Korean-to-Vietnamese cases

## Risks
- possible visual shrink on premium headline samples
- possible style similarity drop on short English headlines

## Files Changed
- app/infra/image/renderer.py
- app/pipeline/quality_gate.py
```

### `run_notes.json`

```json
{
  "loop_id": "2026-04-10-render-overflow-01",
  "agent_name": "Renderer/Layout Agent",
  "candidate_id": "candidate_B",
  "baseline_version": "baseline_v0.3.2",
  "benchmark_split": ["regression", "critical"],
  "modified_files": [
    "app/infra/image/renderer.py",
    "app/pipeline/quality_gate.py"
  ],
  "config_overrides": {
    "headline_wrap_threshold": 0.88,
    "headline_min_scale": 0.72
  },
  "expected_metrics": [
    "layout_fitness",
    "readability"
  ],
  "disallowed_changes_checked": true
}
```

---

## 15. 병렬 운영 시 충돌 방지 규칙

### 규칙 1. 파일 오너십 분리
한 루프에서 동일 파일을 여러 Agent가 동시에 크게 수정하지 않는다.

### 규칙 2. scoring과 dataset은 보호 자산으로 취급
실험 중에는 점수 계산식과 benchmark manifest를 자주 바꾸지 않는다.

### 규칙 3. candidate naming 표준화
예:
- `candidate_A_ocr_conf_filter`
- `candidate_B_cta_rewrite_short`
- `candidate_C_renderer_wrap_fit`

### 규칙 4. one-claim-per-candidate
한 candidate는 주된 개선 주장 하나만 가져야 한다.

### 규칙 5. no silent coupling
다른 단계의 가정을 바꾸면 반드시 `run_notes.json`에 적는다.

---

## 16. 완전 자동화를 위한 운영 시퀀스
아래 시퀀스로 돌리면 병렬 Agent 구조가 자동화에 가깝게 정리된다.

1. Conductor가 loop plan 생성
2. Agent별 작업 범위와 금지 범위 배정
3. 각 Agent가 candidate branch 또는 candidate config 생성
4. Execution Harness가 동일 benchmark에 대해 일괄 실행
5. Validation Agent가 점수 산출
6. Judge Agent가 merge gate 체크
7. pass 시 promote, fail 시 backlog로 환류

즉,
**Agent는 아이디어를 만들고 구현하지만, 승격 권한은 하네스와 게이트가 가진다**
는 구조를 유지해야 한다.

---

## 17. 결론
병렬 Agent 운영이 실패하는 가장 흔한 이유는 Agent 성능 부족이 아니라,
역할이 섞이고 출력 계약이 없고 평가 기준이 흔들리기 때문이다.

따라서 이 문서의 핵심은 다음 세 가지다.

- 역할 분리
- 출력 표준화
- 승격 판단의 자동화 가능성 확보

다음 단계에서는 이 템플릿을 실행 체계와 연결하기 위해,
`merge gate checklist` 와 `run_result / score_result schema` 를 확정해야 한다.
