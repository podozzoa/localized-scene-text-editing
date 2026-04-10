# 08. Code Convention Policy

## 1. 문서 목적
이 문서는 장기 프로젝트 운영을 위한 저장소 전반의 코드 컨벤션, 파일 배치 원칙, 네이밍 규칙, 테스트 규칙, 설정 파일 규칙을 정의한다.

이 프로젝트는 기능 파이프라인과 연구 실험 코드가 병존하므로, 단순 스타일 규칙보다 **역할 분리와 변경 추적 가능성**을 유지하는 규칙이 중요하다.

---

## 2. 최상위 원칙

### 2.1 역할이 이름보다 먼저 드러나야 한다
파일, 모듈, 클래스, 함수 이름은 “무엇을 하는가”와 “어느 계층에 속하는가”를 드러내야 한다.

### 2.2 의미 있는 경계는 디렉토리 구조로 표현한다
production, research, evaluation, harness, contracts, config를 물리적으로 분리한다.

### 2.3 실험 코드는 실험답게, 제품 코드는 제품답게 둔다
“일단 되게 만든 코드”를 production 경로에 그대로 남기지 않는다.

### 2.4 암묵적 규칙보다 명시적 계약을 우선한다
schema, config, prompt template, benchmark manifest는 명시된 파일 규약을 따른다.

---

## 3. 권장 디렉토리 구조
```text
src/
  core/
    contracts/
    domain/
    services/
    policies/
  application/
  infra/
  interfaces/
  pipeline/
    ocr/
    localization/
    inpainting/
    style/
    rendering/
    validation/

research/
experiments/
benchmarks/
  datasets/
  manifests/
  golden/
  reports/

harness/
  runners/
  policies/
  prompts/
  reports/

tests/
  unit/
  integration/
  regression/
  golden/

docs/
config/
scripts/
```

### 3.1 금지 패턴
- production 코드와 experiment 코드가 같은 디렉토리에서 혼재
- benchmark asset과 runtime asset 혼재
- scripts 폴더에 domain logic 누적
- docs 없이 config 의미를 코드 안에 하드코딩

---

## 4. 네이밍 규칙

### 4.1 디렉토리명
- 소문자 + underscore 또는 소문자 단일 단어 사용
- 역할 중심으로 명명
- 예: `style_estimation`, `render_validation`, `benchmark_manifests`

### 4.2 파일명
- 기능과 역할을 함께 드러내야 한다
- 예:
  - `ocr_result_schema.py`
  - `render_quality_validator.py`
  - `poster_localization_service.py`
  - `merge_gate_policy.yaml`

금지:
- `utils.py`, `helpers.py`, `common.py` 같은 포괄적 이름 남발
- `temp.py`, `new.py`, `final2.py` 등 상태성 이름

### 4.3 클래스명
- PascalCase
- 역할 기반 접미사 사용 권장
  - `Service`
  - `Validator`
  - `Estimator`
  - `Policy`
  - `Runner`
  - `Repository`

### 4.4 함수명
- 동사 중심
- 부작용이 있는 함수는 동작을 드러내야 함
- 예:
  - `extract_text_regions`
  - `translate_copy_units`
  - `score_layout_preservation`
  - `validate_render_output`

### 4.5 상수명
- 대문자 + underscore
- 예: `MAX_REGION_OVERLAP`, `DEFAULT_RENDER_TIMEOUT_MS`

---

## 5. 계층별 규칙

### 5.1 Core / Domain
- 외부 provider, 파일 시스템, 네트워크 세부 구현에 직접 의존 금지
- domain object는 UI formatting 세부사항을 포함하지 않음
- 핵심 계약과 규칙은 가능한 core에 둔다

### 5.2 Application / Service
- 파이프라인 orchestration 담당
- provider 선택/실행 흐름은 허용되나 low-level 구현 세부사항 누수 금지

### 5.3 Infra
- OCR 엔진, 번역 API, LLM provider, 파일 입출력, 이미지 툴 구현
- core contract를 충족시키는 adapter 형태 유지

### 5.4 Interfaces
- CLI, HTTP, UI, batch entrypoint
- domain/service 로직 직접 내장 금지

### 5.5 Research / Experiments
- production import 금지
- 실험용 heuristic, ablation, 논문 재현 코드는 여기에만 둔다

---

## 6. 모듈 크기 및 복잡도 규칙

### 6.1 함수 길이
- 단일 함수가 지나치게 길어지지 않도록 관리
- 권장: 40~80라인 이내
- 120라인 초과 시 분리 검토 대상

### 6.2 클래스 책임
- 하나의 클래스는 한 가지 핵심 책임만 가진다
- “OCR + 번역 + 렌더링 + 검증”을 모두 하는 god class 금지

### 6.3 분기 복잡도
- 다중 if/elif 체인이 길어질 경우 policy object 또는 dispatch 구조로 리팩터링 검토

---

## 7. Contract / Schema 규칙

### 7.1 중앙 관리
아래 계약은 중앙 경로에서 관리한다.
- OCR result schema
- region schema
- translation unit schema
- style token schema
- render instruction schema
- validation report schema
- benchmark result schema

### 7.2 중복 정의 금지
동일한 schema가 여러 모듈에 중복 선언되면 drift 위험이 커진다. 중앙 계약을 import해서 사용한다.

### 7.3 변경 규칙
contract 변경 시 반드시 아래가 함께 수행되어야 한다.
- consumer 영향 확인
- 관련 테스트 갱신
- benchmark/validator 영향 확인
- migration note 작성

---

## 8. 테스트 규칙

### 8.1 테스트 디렉토리
- `tests/unit/`
- `tests/integration/`
- `tests/regression/`
- `tests/golden/`

### 8.2 네이밍
- `test_<behavior>.py`
- 시나리오가 명확해야 함
- 예:
  - `test_renderer_preserves_text_region_bounds.py`
  - `test_translation_unit_schema_rejects_missing_target_text.py`

### 8.3 테스트 내용 규칙
- assertion 없는 smoke test 금지
- 지나치게 광범위한 snapshot test 남발 금지
- failure 원인이 명확하지 않은 megatest 금지

### 8.4 연구 테스트와 제품 테스트 분리
- 논문 실험 재현 테스트는 `tests/research/` 또는 `research/tests/`에 분리
- production gate에 자동 반영할지 별도 정책으로 관리

---

## 9. Config / Prompt / Policy 파일 규칙

### 9.1 위치 규칙
- 일반 설정: `config/`
- harness 정책: `harness/policies/`
- prompt template: `harness/prompts/`
- benchmark manifest: `benchmarks/manifests/`

### 9.2 하드코딩 금지
threshold, score weight, provider 선택 정책, benchmark split 기준을 코드에 직접 박지 않는다.

### 9.3 명명 예시
- `render_quality_policy.yaml`
- `merge_gate_policy.yaml`
- `poster_localization_prompt_v1.md`
- `benchmark_manifest_poster_ko_vi_v2.yaml`

---

## 10. Logging / Error Handling 규칙

### 10.1 broad except 최소화
원인 분류가 어려운 `except Exception` 남발 금지. 필요한 경우에도 반드시 context log를 남긴다.

### 10.2 silent fallback 금지
실패했는데도 조용히 fallback으로 넘어가면 품질 분석이 불가능해진다. fallback은 명시 로그가 있어야 한다.

### 10.3 사용자 노출 에러와 내부 에러 분리
내부 stack trace와 사용자 메시지를 구분한다.

---

## 11. 문서화 규칙

### 11.1 public contract 변경 시 문서 갱신 필수
API, schema, benchmark policy, merge gate policy가 바뀌면 docs도 같이 수정한다.

### 11.2 ADR 권장
중요 구조 변경은 ADR(Architecture Decision Record)로 남긴다.

권장 위치:
- `docs/adr/ADR-0001-*.md`

---

## 12. 금지 항목 요약
아래는 기본적으로 금지한다.

- `utils.py` 하나에 무분별한 유틸 누적
- research 코드의 production import
- benchmark golden 파일 임의 수정
- threshold/weight 하드코딩
- protected path 자동 수정
- broad exception + 무로그 fallback
- contract 중복 정의
- 테스트 없는 public behavior 변경

---

## 13. Maintenance Agent 적용 방식
Maintenance Agent는 이 문서를 기준으로 아래를 판정한다.

- 파일/디렉토리 배치 위반
- 네이밍 위반
- 금지 import 위반
- contract 중복/드리프트 후보
- protected path 무단 변경
- config 하드코딩 후보

모든 위반은 severity와 autofix 가능 여부를 함께 남긴다.

---

## 14. 예외 허용 방식
일시적 예외는 waiver를 통해서만 허용한다.

waiver에는 아래가 포함되어야 한다.
- rule
- path
- justification
- owner
- expiry

코드 안에 “TODO: later”로 남기는 방식은 공식 예외로 인정하지 않는다.
