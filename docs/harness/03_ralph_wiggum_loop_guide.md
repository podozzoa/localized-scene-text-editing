# 랄프 위검 루프 운영 가이드

## 1. 이 문서에서 말하는 랄프 위검 루프
여기서의 “랄프 위검 루프”는 멋진 대규모 프레임워크 이름이라기보다,
**작게 바꾸고, 바로 돌려 보고, 비교하고, 안 좋으면 버리고, 좋으면 남기는 고빈도 반복 루프**로 정의한다.

이 프로젝트에서는 특히 다음 이유로 적합하다.

- 이미지 현지화 품질은 한 번에 정답이 나오기 어렵다.
- OCR, copy, inpainting, rendering, validation 이 서로 얽혀 있다.
- 개선처럼 보였던 것이 다른 샘플군에서는 회귀일 수 있다.
- 논문 수준 결과를 따라가려면 baseline 대비 실험 축적이 필수다.

즉, 이 루프의 목적은 “빨리 많이 시도” 자체가 아니라,
**측정 가능한 작은 개선을 계속 축적하는 것**이다.

---

## 2. 루프의 기본 형태

```text
[문제 선택]
   -> [가설 수립]
   -> [agent 별 병렬 구현]
   -> [하네스 일괄 실행]
   -> [baseline 비교]
   -> [승격/폐기/보류 결정]
   -> [다음 문제 선택]
```

핵심은 매 루프마다 아래 네 가지가 반드시 남아야 한다.

- 무엇을 고치려 했는가
- 무엇을 바꿨는가
- 점수가 어떻게 변했는가
- 다음 루프에서 무엇을 할 것인가

---

## 3. 한 번의 루프 단위 정의
한 번의 루프는 아래 조건을 만족해야 한다.

### Loop Unit
- 하나의 주제만 다룬다.
- baseline 과 비교 가능해야 한다.
- 결과가 artifact 와 report 로 남아야 한다.
- merge 여부를 결정할 수 있어야 한다.

### 좋은 루프 예시
- “headline 영역 auto font scaling 개선”
- “shadow 추정 로직 개선”
- “fineprint OCR 재검증 강화”
- “한국어->베트남어 CTA rewriting 규칙 보강”

### 나쁜 루프 예시
- “OCR도 바꾸고, 렌더러도 뜯고, STE도 붙이고, 서비스화도 같이 진행”

이렇게 되면 무엇이 좋아졌는지 절대 분리되지 않는다.

---

## 4. 루프의 운영 역할

### 4.1 Conductor
역할:
- 이번 루프의 문제 정의
- baseline 확정
- agent 별 작업 할당
- 최종 승격 결정

### 4.2 Specialist Agents
권장 분리:
- OCR Agent
- Copy Agent
- Inpainting Agent
- Renderer Agent
- Validation Agent
- STE Research Agent

### 4.3 Judge
역할:
- 결과 비교
- regression 판단
- 수동 검토 필요 샘플 선정

실제로는 코드상 별도 agent 가 아니어도 되지만,
운영 개념상 이 세 역할이 분리되어야 루프가 덜 흔들린다.

---

## 5. 병렬 실행 구조
권장 방식은 “하나의 루프 주제 아래 여러 candidate branch 를 동시에 검증”하는 것이다.

예시:

```text
Loop Theme: renderer overflow 감소

candidate_A: font shrink 로직 개선
candidate_B: multiline wrap 로직 개선
candidate_C: box-fit + tracking 조정
```

그리고 세 후보를 같은 benchmark 에 대해 동시에 실행한다.

비교 결과:
- A: overflow 감소, style similarity 소폭 하락
- B: overflow 감소, headline 레이아웃 개선, fineprint 악화
- C: 평균은 무난하지만 극단 케이스 불안정

이 경우 B를 일부 채택하거나, A+B의 장점을 다시 다음 루프로 넘길 수 있다.

---

## 6. 루프 템플릿
매 루프마다 아래 템플릿을 유지하는 것을 권장한다.

## Loop Header
- loop_id
- date
- owner
- theme
- baseline version
- benchmark set

## Problem Statement
- 현재 무엇이 문제인가
- 어떤 샘플군에서 특히 심한가
- 사용자 가치에 어떤 영향을 주는가

## Hypothesis
- 어떤 변경이 어떤 지표를 개선할 것이라 예상하는가

## Candidate Changes
- candidate_A
- candidate_B
- candidate_C

## Run Configuration
- dataset
- model version
- font set
- locale pair
- deterministic options

## Evaluation Summary
- overall score delta
- regressions
- critical failures
- manual review notes

## Decision
- promote / reject / hold

## Next Loop
- 다음 루프 주제

---

## 7. 루프의 게이트 규칙
루프가 계속 흔들리는 이유 중 하나는 “이번에는 이 정도면 된 것 같음” 같은 주관적 판단이 들어오기 때문이다.
이를 막기 위한 최소 게이트 예시는 아래와 같다.

### Gate 1. 실행 성공 게이트
- 전체 benchmark 중 X% 이상 성공 실행
- stage crash 허용치 이하

### Gate 2. 품질 게이트
- total score baseline 이상
- critical set 평균 baseline 이상
- severe regression 0건

### Gate 3. 제품 게이트
- 타겟 카피가 읽히지 않는 결과 금지
- CTA 또는 headline 이 어색한 결과 비율 제한

### Gate 4. 운영 게이트
- latency 증가 허용 범위 내
- 메모리 사용량 허용 범위 내

---

## 8. 루프에서 반드시 남겨야 할 산출물
각 루프는 아래를 남겨야 다음 반복이 빨라진다.

1. `loop_plan.md`
   - 무엇을 왜 고치는지
2. `config_snapshot.json`
   - 어떤 조건으로 돌렸는지
3. `run_summary.json`
   - 점수 요약
4. `report.md`
   - 사람이 읽는 결론
5. `regression_cases/`
   - 망가진 케이스 모음
6. `winning_cases/`
   - 개선이 잘 보이는 케이스 모음

특히 `regression_cases/` 를 모아두지 않으면 같은 실패를 반복하게 된다.

---

## 9. 논문 추종형 루프와 제품형 루프 분리
이 프로젝트는 “논문 수준 품질追求”와 “서비스 배포”라는 두 축이 동시에 있다.
이 둘을 같은 루프로 돌리면 충돌한다.

따라서 루프를 두 계열로 나누는 것이 좋다.

### 9.1 Product Loop
목표:
- 현재 서비스 품질 점진 개선
- baseline 안정성 유지
- 배포 가능한 결과 축적

대상:
- renderer 개선
- quality gate 개선
- batch reliability 개선
- locale copy rules 개선

### 9.2 Research Loop
목표:
- STE backbone 실험
- AnyText류, diffusion류, 새 논문 기법 비교
- 공격적 실험 수행

대상:
- crop-level editing
- mask-conditioned generation
- typography-aware editing
- text consistency research

원칙:
Research Loop 의 결과는 바로 mainline 으로 들어오지 않는다.
반드시 Product Loop 의 benchmark 와 gate 를 통과해야 한다.

---

## 10. 실제 운영 순서 예시

### Day 1
- benchmark set 30장 고정
- baseline 점수 산출
- current pain point 상위 3개 선정

### Day 2
- theme: fineprint OCR 안정화
- candidate 2~3개 병렬 실행
- comparator 리포트 생성

### Day 3
- 승자안 반영
- 새 baseline 생성
- 다음 theme 선정

### Day 4
- theme: headline style preservation
- renderer / style estimator 병렬 실험

### Day 5
- research loop: STE adapter로 subset 실험
- baseline renderer 와 비교

이렇게 가면 매일 “무엇이 실제로 좋아졌는지”가 쌓인다.

---

## 11. Codex/Agent 프롬프트 작성 원칙
병렬 agent 를 돌릴 때 프롬프트는 다음 정보를 반드시 포함하는 것이 좋다.

- 이번 루프의 단일 목표
- 건드려도 되는 파일 범위
- 건드리면 안 되는 baseline 계약
- 출력해야 할 artifact / report 형식
- 성공 기준과 탈락 기준

예시:

```text
Goal:
Reduce renderer overflow on headline and CTA regions without degrading OCR target match.

Scope:
Modify only renderer-related modules and tests.
Do not change OCR adapter or translation logic.

Required Outputs:
- code changes
- test cases
- before/after sample outputs
- run_result.json compatible metrics

Success Criteria:
- overflow severe count reduced
- total score >= baseline
- no regression on critical poster set
```

이렇게 해야 agent 가 “열심히 많이 바꿨지만 비교 불가능한 결과”를 만드는 일을 줄일 수 있다.

---

## 12. 가장 먼저 시작할 실제 작업
지금 이 프로젝트에서 랄프 위검 루프를 시작하려면 우선 아래 순서가 적합하다.

1. benchmark dataset 고정
2. baseline run 저장
3. score schema 정의
4. report generator 추가
5. agent 역할 분리
6. theme 단위 병렬 loop 시작

즉, **루프의 첫 번째 구현 대상은 모델이 아니라 하네스 자체**다.
하네스가 먼저 서야 이후 반복이 축적된다.
