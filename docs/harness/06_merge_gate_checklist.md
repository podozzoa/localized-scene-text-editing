# Merge Gate 체크리스트 및 승격 정책

## 1. 문서 목적
이 문서는 이미지 현지화 프로젝트에서 candidate 변경사항을 baseline 또는 mainline으로 승격할 때 사용하는 **공식 merge gate**를 정의한다.

이 문서가 필요한 이유는 분명하다.

- 결과물이 얼핏 좋아 보인다는 이유로 병합하면 회귀가 누적된다.
- 평균 점수만 좋아도 critical 케이스가 망가질 수 있다.
- Agent가 각자 좋은 결과라고 주장해도 비교 기준이 없으면 계속 흔들린다.
- 완전 자동화를 목표로 할수록 “사람 감각에 의존한 승인”을 줄여야 한다.

따라서 merge gate의 목적은 개발 속도를 늦추는 것이 아니라,
**좋아진 변경만 축적하고, 위험한 변경은 자동으로 보류시키는 것**이다.

---

## 2. 승격 정책의 핵심 원칙

### Principle A. baseline 이상이어야 한다
candidate는 적어도 baseline과 동등하거나, 명시된 핵심 지표에서 우위가 있어야 한다.

### Principle B. 평균 점수만으로 승격하지 않는다
critical split, severe issue, category regression을 함께 본다.

### Principle C. failure는 조기 차단한다
실행 실패, artifact 누락, clipping severe issue, legal text 훼손 같은 항목은 초기에 차단한다.

### Principle D. 연구 트랙과 제품 트랙을 분리한다
STE 연구 후보가 인상적인 결과를 일부 샘플에서 보여줘도,
재현성과 안정성이 확보되지 않으면 제품 mainline으로 바로 승격하지 않는다.

### Principle E. 체크리스트는 계층형이어야 한다
모든 조건을 한 번에 보는 것이 아니라,
- 실행 게이트
- 품질 게이트
- 회귀 게이트
- 운영 게이트
- 릴리스 게이트
순서로 본다.

---

## 3. 승격 단계 정의

### Stage 0. Draft Candidate
상태:
- 아이디어 또는 초기 구현
- smoke만 통과했거나 아직 full scoring 미실행

조치:
- baseline 승격 불가
- regression split으로 이동 필요

### Stage 1. Evaluation Candidate
상태:
- regression split 결과 확보
- 기본 정량 비교 가능

조치:
- critical split 평가 진행
- severe regression 검사 수행

### Stage 2. Promotion Candidate
상태:
- regression + critical 통과
- merge gate 대부분 충족

조치:
- mainline 승격 가능 후보
- 필요 시 manual review hold

### Stage 3. Release Candidate
상태:
- release split까지 통과
- 제품 배포 전 최종 후보

조치:
- 배포 승격 여부 판단

---

## 4. 게이트 계층 구조

```text
Gate 1. Execution Gate
Gate 2. Output Integrity Gate
Gate 3. Quality Gate
Gate 4. Regression Gate
Gate 5. Operational Gate
Gate 6. Human Review Gate
Gate 7. Release Gate
```

각 게이트는 앞단을 통과해야 다음으로 넘어간다.

---

## 5. Gate 1. Execution Gate

### 목적
candidate가 최소한 동일한 실험 조건으로 정상 실행되었는지 확인한다.

### 통과 조건
- 지정 benchmark split의 실행 완료율이 기준 이상
- stage crash가 허용치 이하
- timeout 비율 허용치 이하
- config snapshot 저장 완료
- code version / model version / font set 기록 완료

### 권장 기준
- smoke: 100% 성공
- regression: 98% 이상 성공
- critical: 100% 성공
- release: 99% 이상 성공

### 실패 시 처리
- 자동 reject 또는 draft 유지
- 품질 비교로 넘어가지 않음

### 체크리스트
- [ ] benchmark split이 명시되었는가
- [ ] baseline과 동일 split으로 실행되었는가
- [ ] config snapshot이 저장되었는가
- [ ] candidate version이 고정되었는가
- [ ] 실행 실패 샘플 목록이 남았는가

---

## 6. Gate 2. Output Integrity Gate

### 목적
산출물이 자동 채점과 시각 검토에 필요한 최소 구조를 만족하는지 확인한다.

### 통과 조건
- final image 존재
- intermediate artifacts 존재
- run_result.json 존재
- score_summary 생성 가능
- region 단위 결과와 샘플 단위 결과 연결 가능

### 필수 산출물
- `final/`
- `debug/`
- `run_result.json`
- `candidate_summary.md`
- `run_notes.json`

### 체크리스트
- [ ] final image가 모든 성공 샘플에 대해 존재하는가
- [ ] debug artifact 경로가 유효한가
- [ ] run_result schema 검증을 통과하는가
- [ ] 실패 stage가 구조화되어 기록되었는가
- [ ] baseline 비교에 필요한 metadata가 포함되었는가

---

## 7. Gate 3. Quality Gate

### 목적
candidate가 실제 품질 측면에서 baseline 이상인지 확인한다.

### 핵심 지표
- total_score
- target_text_match
- background_cleanliness
- layout_fitness
- style_similarity
- readability
- copy_acceptability

### 기본 통과 조건 예시
- overall weighted score: baseline 이상
- critical split weighted score: baseline 이상
- severe overflow/clipping: 0건
- target_text_match: baseline 대비 악화 금지

### stricter promotion 조건 예시
- overall weighted score: +1.5% 이상
- target_text_match: +0.5% 이상 또는 동일
- layout_fitness: +1.0% 이상
- background_cleanliness: 동일 이상

### 체크리스트
- [ ] overall weighted score가 baseline 이상인가
- [ ] critical split score가 baseline 이상인가
- [ ] severe clipping이 0건인가
- [ ] severe readability failure가 0건인가
- [ ] target_text_match가 악화되지 않았는가

---

## 8. Gate 4. Regression Gate

### 목적
평균 점수 상승에 가려진 치명적 회귀를 잡는다.

### regression 유형

#### Type A. Severe Regression
즉시 탈락에 가까운 회귀
예:
- 텍스트가 잘려 읽을 수 없음
- CTA가 사라짐
- 가격/날짜/브랜드명 오류
- disclaimer 누락
- 배경 손상으로 디자인이 심하게 붕괴

#### Type B. Category Regression
특정 카테고리에서 의미 있는 악화
예:
- textured background 샘플에서 잔상 급증
- fineprint heavy 샘플에서 OCR 재검출 하락
- Vietnamese CTA 샘플에서 어색한 카피 증가

#### Type C. Statistical Regression
전체 평균 또는 분포 상 악화
예:
- 평균 score 감소
- p90 latency 급증
- variance 증가로 안정성 악화

### 자동 탈락 규칙 예시
- severe regression 1건 이상 in critical split
- legal disclaimer region failure 1건 이상
- target_text_match가 critical split에서 baseline보다 낮음
- brand sensitive 샘플에서 금지어 위반 발생

### 체크리스트
- [ ] critical split severe regression 0건인가
- [ ] role별 치명 실패가 없는가
- [ ] category별 평균 악화가 허용 범위 이내인가
- [ ] locale별 급격한 성능 하락이 없는가
- [ ] statistical variance가 비정상적으로 커지지 않았는가

---

## 9. Gate 5. Operational Gate

### 목적
서비스화 가능한 수준의 운영 안정성을 보장한다.

### 핵심 항목
- 평균 latency
- p95 latency
- 메모리 사용량
- 배치 처리량
- 재현성
- 의존성 증가 여부

### 기본 통과 조건 예시
- p95 latency 증가율 허용 범위 내
- memory spike 없음
- 동일 입력 반복 실행 시 결과 드리프트 허용 범위 내
- 새 외부 의존성 도입 시 배포 영향 분석 완료

### 체크리스트
- [ ] latency가 허용 범위 이내인가
- [ ] memory 사용량이 관리 가능한가
- [ ] deterministic drift가 허용 범위 이내인가
- [ ] 신규 dependency 리스크가 기록되었는가
- [ ] 배포 경로에 치명 영향이 없는가

---

## 10. Gate 6. Human Review Gate

### 목적
자동 점수만으로 판정하기 어려운 사례를 사람 검토로 보완한다.

### 사람 검토가 필요한 대표 사례
- copy naturalness가 미묘한 경우
- cultural fit 논란 가능성
- style similarity 수치와 체감이 어긋나는 경우
- premium visual 디자인에서 작은 미세 차이가 중요한 경우
- research track 후보의 인상적 샘플이 있는 경우

### Human Review 우선순위 큐 생성 기준
- score delta는 좋지만 style similarity가 불안한 샘플
- severe는 아니지만 borderline clipping 샘플
- acceptable variant가 많은 headline/CTA 샘플
- brand sensitive, legal disclaimer 샘플

### 체크리스트
- [ ] manual review queue가 생성되었는가
- [ ] top risk 샘플이 포함되었는가
- [ ] critical demo 샘플이 포함되었는가
- [ ] reviewer note가 기록되었는가
- [ ] auto-pass와 manual-hold가 구분되었는가

---

## 11. Gate 7. Release Gate

### 목적
candidate를 단순 merge가 아니라 실제 배포 가능한 상태로 승격할지 판단한다.

### 통과 조건 예시
- release split 통과
- critical severe issue 0건
- 운영 지표 허용 범위 내
- 릴리스 노트 작성 완료
- rollback 가능성 확보

### 추가 조건
- demo/customer-sensitive 샘플에서 체감 품질 향상 확인
- known issue 목록이 업데이트됨
- feature flag 또는 staged rollout 계획 존재

### 체크리스트
- [ ] release split 결과가 저장되었는가
- [ ] critical severe issue가 0건인가
- [ ] release note 초안이 작성되었는가
- [ ] rollback plan이 존재하는가
- [ ] staged rollout 여부가 결정되었는가

---

## 12. 승격 판정 매트릭스

| 상태 | 설명 | 조치 |
|---|---|---|
| Promote | 모든 핵심 게이트 통과, 회귀 없음 | baseline/mainline 승격 |
| Promote with Flag | 품질 개선은 확인되나 운영 리스크 존재 | feature flag 하 승격 |
| Hold | 일부 개선 있으나 manual review 또는 추가 실험 필요 | 다음 루프로 보류 |
| Reject | severe regression 또는 실행/품질 게이트 실패 | 폐기 또는 재작업 |
| Research Only | 인상적 결과 있으나 재현성/운영성 부족 | research branch 유지 |

---

## 13. 권장 수치 기준 초안
아래 값은 초기 초안이며, 실제 프로젝트 기준선에 맞춰 조정해야 한다.

### Product Loop 기본 기준
- smoke 성공률: 100%
- regression 성공률: 98% 이상
- critical 성공률: 100%
- overall weighted score: baseline 이상
- critical weighted score: baseline 이상
- severe clipping: 0
- severe legal/price/brand error: 0
- p95 latency 증가: +10% 이내

### Promotion 강화 기준
- overall weighted score: +1.0% 이상
- critical split: baseline 이상 + severe 0
- target_text_match: baseline 이상
- layout_fitness: baseline 이상
- background_cleanliness: baseline 이상

### Release 기준
- release split 통과
- critical severe: 0
- manual review hold: 0 또는 승인 완료
- rollback plan 있음

---

## 14. merge gate 자동화 의사결정 로직 예시

```text
if execution_gate_failed:
    reject
elif output_integrity_failed:
    reject
elif severe_regression_in_critical > 0:
    reject
elif target_text_match_critical < baseline:
    reject
elif overall_score >= baseline and critical_score >= baseline:
    if operational_risk_low and manual_review_clear:
        promote
    elif operational_risk_medium or manual_review_pending:
        hold_or_promote_with_flag
    else:
        hold
else:
    hold_or_reject
```

---

## 15. merge gate 결과 보고서 템플릿

```md
# Merge Gate Result
- loop_id: 2026-04-10-render-overflow-01
- candidate_id: candidate_B
- baseline_version: baseline_v0.3.2
- decision: Hold

## Gate Summary
- Execution Gate: Pass
- Output Integrity Gate: Pass
- Quality Gate: Pass
- Regression Gate: Pass
- Operational Gate: Borderline
- Human Review Gate: Pending
- Release Gate: Not evaluated

## Key Metrics
- overall_weighted_score_delta: +1.8%
- critical_weighted_score_delta: +0.4%
- severe_regression_count: 0
- p95_latency_delta: +12%

## Decision Rationale
Candidate improves layout fit and reduces overflow, but p95 latency exceeds the current product-loop tolerance. Hold for optimization or feature-flagged promotion.

## Required Next Actions
- optimize renderer latency
- rerun critical split
- review premium headline samples manually
```

---

## 16. 병렬 Agent 환경에서의 merge 원칙

### 원칙 1. 후보 간 직접 경쟁보다 baseline 비교를 우선한다
candidate_A가 candidate_B보다 좋아 보여도, baseline보다 나쁘면 승격 불가다.

### 원칙 2. 부분 승격을 허용한다
예를 들어 renderer candidate의 일부 설정만 채택할 수 있다.
단, 새 baseline은 다시 공식 benchmark로 재측정해야 한다.

### 원칙 3. 혼합 승격은 별도 후보로 재평가한다
A와 B의 장점을 합친 버전은 새로운 candidate로 간주한다.

### 원칙 4. scoring 변경은 별도 루프로 관리한다
점수 계산 자체를 바꾸면 이전 기록과 비교가 끊긴다.
따라서 scoring formula 변경은 일반 기능 후보와 분리한다.

---

## 17. 완전 자동화를 위한 최소 구현 포인트
merge gate를 자동화하려면 아래 구조가 필요하다.

1. `run_result.schema.json`
2. `score_result.schema.json`
3. `merge_gate_policy.yaml`
4. `promotion_decider.py`
5. `manual_review_queue_builder.py`
6. `report_builder.py`

권장 정책 파일 예시:

```yaml
product_loop:
  smoke_success_rate: 1.0
  regression_success_rate_min: 0.98
  critical_success_rate_min: 1.0
  severe_regression_critical_max: 0
  overall_score_min_delta: 0.0
  critical_score_min_delta: 0.0
  p95_latency_max_delta: 0.10
  require_manual_review_for_brand_sensitive: true

release_loop:
  require_release_split: true
  severe_regression_critical_max: 0
  require_rollback_plan: true
  require_manual_review_clear: true
```

---

## 18. 지금 프로젝트에 바로 적용하는 권장안
현재 프로젝트는 modular pipeline 구조를 이미 가지고 있으므로,
merge gate는 다음 순서로 바로 붙이는 것이 현실적이다.

### 1단계
- smoke / regression / critical split 정의
- run_result.json 표준화
- severe failure 기준 정의

### 2단계
- total score 계산기 연결
- baseline vs candidate comparator 구현
- hold/reject/promote 자동 판정 도입

### 3단계
- release gate + feature flag 정책 연결
- research track STE 후보를 별도 승격 경로로 분리

---

## 19. 결론
merge gate는 단순 승인 절차가 아니라,
**랄프 위검 루프를 무한 반복해도 결과가 누적 향상되도록 만드는 안전장치**다.

이 문서의 핵심은 다음이다.

- 평균 점수만 보지 말 것
- critical과 severe를 우선 볼 것
- 연구 후보와 제품 후보를 분리할 것
- promote / hold / reject를 구조화할 것

이 기준이 고정되어야 병렬 Agent를 많이 돌릴수록 시스템이 더 안정해지고,
최종적으로는 사람 개입을 줄인 상태에서도 자동 승격에 가까운 운영이 가능해진다.
