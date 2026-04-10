# 하네스 엔지니어링 구성 초안

## 1. 문서 목적
이 문서는 현재의 이미지 현지화 MVP를 **실험 가능한 시스템**으로 전환하기 위한 하네스 엔지니어링 구조를 정의한다.

핵심은 다음 세 가지다.

- 개발자가 임의로 “좋아 보인다”고 판단하지 않도록 한다.
- 병렬 agent 가 동일한 입력과 동일한 평가 기준 위에서 경쟁하게 만든다.
- baseline 을 깨지 않고, 개선안만 안정적으로 흡수한다.

---

## 2. 원칙

### Principle A. 기준선 우선
항상 하나의 공식 baseline 이 존재해야 한다.

### Principle B. 측정 없는 개선 금지
점수 변화가 없는 “감성적 개선”은 병합하지 않는다.

### Principle C. 파이프라인 불변
기본 순서는 유지한다.

`detect -> recognize -> rewrite -> restore -> render -> validate`

단, 실험용 서브트랙은 병렬로 붙일 수 있다.

### Principle D. 작은 변경, 강한 비교
한 번에 여러 축을 크게 바꾸지 않는다.
한 agent 는 한 문제군에 집중한다.

### Principle E. 실패도 자산화
실패 실험도 artifact 와 score 를 남겨서 이후 루프의 학습 재료로 쓴다.

---

## 3. 하네스 전체 구조

```text
[Input Dataset]
   │
   ├─ baseline runner
   │    └─ baseline artifacts + scores
   │
   ├─ candidate runner (agent A)
   │    └─ candidate artifacts + scores
   │
   ├─ candidate runner (agent B)
   │    └─ candidate artifacts + scores
   │
   └─ candidate runner (agent C)
        └─ candidate artifacts + scores

[Comparator]
   ├─ baseline vs candidate diff
   ├─ regression detection
   └─ promotion decision

[Report]
   ├─ summary markdown
   ├─ failure cases
   └─ next-loop backlog
```

---

## 4. 권장 디렉토리 구조

```text
project/
  app/
  docs/
  harness/
    datasets/
      poster_benchmark/
        manifest.json
        images/
        expected/
    configs/
      baseline.yaml
      gate_strict.yaml
      gate_explore.yaml
    runners/
      run_baseline.py
      run_candidate.py
      run_batch.py
    scoring/
      ocr_score.py
      artifact_score.py
      layout_score.py
      copy_score.py
      aggregate.py
    comparators/
      compare_runs.py
      select_winner.py
    reports/
      build_report.py
    schemas/
      run_result.schema.json
      score.schema.json
      experiment.schema.json
  outputs/
  experiments/
    2026-xx-xx_runname/
      config_snapshot.json
      baseline/
      candidate_x/
      report.md
```

---

## 5. 핵심 하네스 구성요소

## 5.1 Dataset Harness
역할:
- 대표 테스트셋을 관리한다.
- 샘플별 기대값과 난이도 라벨을 관리한다.

필수 포함 항목:
- input image path
- source locale
- target locale
- source text regions or verification hints
- expected target text or acceptable candidates
- category tags
  - simple
  - dense
  - rotated
  - textured background
  - fineprint
  - headline-heavy

권장 추가 항목:
- human review tags
- forbidden outcomes
- region importance weights

---

## 5.2 Execution Harness
역할:
- baseline / candidate 를 동일 조건으로 실행한다.
- config snapshot 을 남긴다.
- 중간 산출물 경로를 표준화한다.

실행 입력:
- dataset manifest
- model config
- font config
- pipeline variant
- experiment tag

실행 출력:
- final image
- debug artifacts
- per-stage logs
- structured run_result.json

필수 규칙:
- seed 또는 deterministic 옵션 기록
- 코드 버전(commit hash 또는 build id) 기록
- 모델 버전 기록
- 사용 font 기록
- 실패 시 stage 명시

---

## 5.3 Scoring Harness
역할:
- 결과를 점수화한다.
- baseline 과 candidate 를 동일 기준으로 비교 가능하게 만든다.

권장 점수 체계 예시:

```text
total_score =
  0.25 * target_text_match
+ 0.20 * background_cleanliness
+ 0.20 * layout_fitness
+ 0.15 * style_similarity
+ 0.10 * readability
+ 0.10 * copy_acceptability
```

세부 score 예시:
- `target_text_match`: OCR 재인식 기반 문자열 일치율
- `background_cleanliness`: 잔상/artifact/halo
- `layout_fitness`: overflow, clipping, alignment
- `style_similarity`: color, weight, shadow, scale 근사
- `readability`: 사람이 읽을 수 있는지
- `copy_acceptability`: locale에 맞는 문구인지

주의:
`copy_acceptability` 는 완전 자동 점수화가 어려우므로 초기에는 human-in-the-loop 또는 LLM judge + human spot check 혼합이 현실적이다.

---

## 5.4 Regression Harness
역할:
- candidate 가 특정 샘플군에서 baseline 보다 나빠졌는지 탐지한다.

규칙 예시:
- 전체 평균 점수 +2% 이상 개선
- critical set 에서 단 한 건도 severe regression 금지
- OCR target match 가 baseline 보다 낮아지면 자동 탈락
- overflow/clipping severe issue 발생 시 자동 탈락

critical set 예시:
- 대표 고객 포스터
- dense fineprint 샘플
- high-value demo 샘플

---

## 5.5 Reporting Harness
역할:
- 실행 결과를 사람이 빠르게 판단할 수 있게 요약한다.

보고서 필수 내용:
- baseline vs candidate 총점 비교
- 항목별 점수 변화
- top improved cases
- top regressed cases
- stage failure count
- 수동 검토 필요 목록
- 다음 루프 우선순위

권장 산출물:
- `report.md`
- `summary.json`
- `regressions.csv`
- sample side-by-side 비교 이미지

---

## 6. 병렬 Agent 구조
현재 프로젝트 성격상 agent 는 기능 단위가 아니라 **문제군 단위**로 분리하는 것이 적합하다.

### Agent A. OCR/Detection Agent
목표:
- 검출 recall 향상
- rotated/small text 대응 개선
- polygon 품질 향상

입력:
- 원본 이미지
- OCR config
- baseline 결과

출력:
- OCR 결과 JSON
- detection score 변화
- 실패 샘플 목록

### Agent B. Localization Copy Agent
목표:
- literal translation 감소
- 카피 길이/문맥 적합성 향상
- locale 별 rewriting rule 정교화

입력:
- source text
- role classification
- locale

출력:
- candidate copy set
- copy score
- overflow risk estimate

### Agent C. Inpainting Agent
목표:
- 잔상 감소
- 질감 복원 향상
- complex background 대응

입력:
- source image
- region mask

출력:
- restored image
- artifact score

### Agent D. Renderer/Style Agent
목표:
- 폰트 크기, 줄바꿈, 정렬, 색상, 그림자 보존 개선
- overflow/clipping 감소

입력:
- restored image
- target text
- style estimate

출력:
- rendered image
- layout/style score

### Agent E. Validation Agent
목표:
- score 신뢰도 향상
- 자동 탈락 규칙 정교화
- human review burden 감소

입력:
- all artifacts
- OCR rerun result

출력:
- quality report
- pass/fail decision

### Agent F. STE Research Agent
목표:
- baseline renderer 대신 STE backbone 적용 가능성 검증
- AnyText류 또는 기타 STE 계열 모델 comparative track 운영

입력:
- exported crop/mask/target text set

출력:
- edited crop/result
- baseline 대비 score diff

---

## 7. Agent 간 계약
병렬 구조가 흔들리는 가장 큰 이유는 agent 마다 출력 포맷이 달라지는 것이다.
따라서 아래 계약을 강제하는 것이 좋다.

### 공통 입력 계약
- `job_id`
- `sample_id`
- `config_snapshot`
- `input_image_path`
- `regions[]`
- `baseline_artifact_refs`

### 공통 출력 계약
- `status`: success / failed / partial
- `artifacts`: 경로 목록
- `metrics`: key-value score 목록
- `issues`: 발견한 문제
- `decision`: keep / reject / review

이 공통 계약이 있어야 comparator 와 report builder 가 재사용 가능해진다.

---

## 8. 승격 규칙
candidate 를 baseline 으로 승격시키는 규칙 예시는 다음과 같다.

### Promote 조건
- 평균 total score 개선
- critical regression 없음
- stage failure rate 악화 없음
- latency 악화가 허용 범위 내
- 수동 검토 샘플에서 명백한 품질 저하 없음

### Reject 조건
- OCR 재인식 품질 저하
- overflow/clipping severe 증가
- 배경 artifact 증가
- 특정 핵심 데모셋 품질 하락

### Hold 조건
- 총점은 좋아졌지만 특정 카테고리에서 불안정
- human review 필요 샘플 다수
- 편차가 커서 재현성 부족

---

## 9. 현재 프로젝트에 바로 추가할 실무 항목
1. `harness/` 디렉토리 신설
2. `poster_benchmark/manifest.json` 작성
3. `run_result.json` 스키마 정의
4. `quality_gate.py` 확장
5. batch run 스크립트 추가
6. baseline/candidate 비교 리포트 생성기 추가
7. “실패했지만 유의미한 케이스” 수집용 bucket 추가

---

## 10. 구현 우선순위
### 우선순위 1
- dataset manifest
- batch runner
- structured run result
- aggregate score
- markdown report

### 우선순위 2
- regression gate
- side-by-side diff export
- category weighted scoring

### 우선순위 3
- STE adapter track
- candidate auto ranking
- merge recommendation

이 순서로 가야 하네스가 먼저 서고, 그 다음에 개선 속도가 붙는다.
