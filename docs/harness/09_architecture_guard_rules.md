# 09. Architecture Guard Rules

## 1. 문서 목적
이 문서는 프로젝트의 아키텍처 경계를 명시하고, Maintenance Agent 또는 Architecture Guard가 어떤 규칙을 위반으로 판단할지 정의한다.

이 프로젝트는 이미지 기반 포스터 현지화 서비스로서 다음과 같은 주요 흐름을 포함한다.

- text region detection
- OCR
- translation / localization
- target copy generation
- background restoration / inpainting
- style estimation
- text re-rendering
- validation / quality scoring
- benchmark harness
- research experiment loop

구성 요소가 많고 연구/제품 경계가 쉽게 무너지므로, 의존성 방향과 금지 연결을 명확하게 정의해야 한다.

---

## 2. 기본 아키텍처 원칙

### 2.1 의존성 방향
기본 방향은 다음을 따른다.

- interfaces -> application -> core
- infra -> core contract 구현
- pipeline orchestrator -> core/service/policy 사용
- research/experiments는 production runtime에 영향을 주지 않음

### 2.2 외부 세부 구현은 안쪽 계층이 모르도록 유지
core/domain은 OCR 엔진 종류, 번역 provider, 이미지 라이브러리 세부 구현을 알지 못해야 한다.

### 2.3 evaluation과 runtime은 구분한다
validation/scoring은 runtime 결과를 평가할 수는 있지만, runtime 내부 구현을 강하게 결합해서는 안 된다.

### 2.4 research와 product를 분리한다
실험용 heuristic과 논문 재현 코드는 제품 코드와 같은 승격 기준을 갖지 않는다.

---

## 3. 권장 계층 맵

### 3.1 Production 경로
- `src/core/`
- `src/application/`
- `src/infra/`
- `src/interfaces/`
- `src/pipeline/`

### 3.2 Research 경로
- `research/`
- `experiments/`

### 3.3 Evaluation / Harness 경로
- `evaluation/`
- `benchmarks/`
- `harness/`

### 3.4 Protected 경로
- `core/contracts/`
- `evaluation/scoring/`
- `benchmarks/golden/`
- `harness/policies/`
- `release/`

---

## 4. 허용 의존성

### 4.1 core
허용:
- core 내부 모듈
- 표준 라이브러리
- 계약 수준 타입/모델

금지:
- infra/provider 직접 import
- interface/UI 직접 import
- research 코드 import
- benchmark/harness import

### 4.2 application / pipeline
허용:
- core
- 정책 객체
- 추상 계약
- adapter registration 수준의 참조

주의:
- 구체 provider 구현 직접 의존은 최소화
- orchestration 목적 외 저수준 구현 누수 금지

### 4.3 infra
허용:
- core contract
- 외부 SDK/라이브러리

금지:
- UI 레이어 의존
- benchmark golden 데이터에 대한 직접 의존

### 4.4 interfaces
허용:
- application/service
- request/response model

금지:
- domain/infra 세부 구현을 직접 조작하는 우회 로직

### 4.5 evaluation / benchmarks / harness
허용:
- contracts
- result schema
- runtime output artifact 읽기

금지:
- production behavior를 바꾸는 import
- runtime provider 선택 로직 변경

### 4.6 research / experiments
허용:
- 계약 import
- 별도 실험용 pipeline 구성

금지:
- production mainline에 직접 연결
- production config를 실험 편의상 오염시키는 변경

---

## 5. 금지 규칙 목록

### RULE-ARCH-001
**production must not import research runtime**

설명:
`src/`, `app/`, `pipeline/` 내부 코드가 `research/`, `experiments/` 모듈을 import하면 위반이다.

위험:
- 실험 코드가 서비스 안정성을 해침
- 재현성 및 배포 안정성 저하

심각도:
- critical

---

### RULE-ARCH-002
**core must not depend on infra or interface**

설명:
core/domain/service 계약이 외부 provider나 UI를 직접 알면 안 된다.

심각도:
- critical

---

### RULE-ARCH-003
**runtime must not depend on benchmark golden assets**

설명:
production runtime이 benchmark golden, label, answer key에 의존하면 안 된다.

심각도:
- critical

---

### RULE-ARCH-004
**scoring policy must not be hardcoded inside runtime logic**

설명:
score threshold, weight, evaluator rule을 renderer/localizer 내부에 하드코딩하면 위반이다.

심각도:
- high

---

### RULE-ARCH-005
**contracts must be centrally defined**

설명:
OCR result, translation unit, style token, render instruction, validation report 등 핵심 schema가 여러 위치에 중복 정의되면 위반 후보로 본다.

심각도:
- high

---

### RULE-ARCH-006
**evaluation should read outputs, not mutate runtime behavior**

설명:
evaluation/harness가 runtime 결과를 평가하는 것은 허용되나, runtime 내부 정책을 직접 덮어쓰는 것은 금지한다.

심각도:
- high

---

### RULE-ARCH-007
**entrypoints must not embed business logic**

설명:
CLI, API, UI entrypoint 파일에서 OCR/번역/렌더링 핵심 비즈니스 로직을 직접 구현하면 위반이다.

심각도:
- medium

---

### RULE-ARCH-008
**scripts must not become a shadow application layer**

설명:
`scripts/` 아래에 실제 서비스 핵심 로직이 쌓이는 것을 금지한다.

심각도:
- medium

---

### RULE-ARCH-009
**protected paths require explicit justification**

설명:
protected path 변경은 항상 승인 근거와 영향 분석이 있어야 한다.

심각도:
- high

---

### RULE-ARCH-010
**fallback behavior must be observable**

설명:
OCR 실패, translation fallback, render fallback 같은 우회 흐름은 반드시 로그 또는 report에 드러나야 한다.

심각도:
- medium

---

## 6. 파이프라인별 경계 규칙

### 6.1 OCR 단계
허용:
- 이미지 입력
- detection result 산출
- OCR text extraction
- confidence metadata 산출

금지:
- 광고 문구 생성 정책 직접 판단
- localization style policy 직접 결정
- rendering implementation 호출로 강결합

### 6.2 Localization / Translation 단계
허용:
- source text -> target text 변환
- 카피라이팅 정책 적용
- locale/market context 사용

금지:
- region geometry 직접 수정
- inpainting mask 직접 생성
- renderer 내부 layout 엔진 구현에 결합

### 6.3 Inpainting 단계
허용:
- original text 제거
- background restoration

금지:
- 문구 생성 정책 결정
- score threshold 조정

### 6.4 Style Estimation 단계
허용:
- font/style/spacing/color/anchor 추정
- render hint 생성

금지:
- benchmark scorer 직접 참조
- UI preset 하드코딩

### 6.5 Rendering 단계
허용:
- render instruction을 기반으로 텍스트 재배치/재렌더링
- region constraint 준수

금지:
- 논문 실험 코드 직접 import
- golden label에 맞춘 cheat logic

### 6.6 Validation 단계
허용:
- layout preservation
- readability
- semantic adequacy
- artifact detection
- score report 생성

금지:
- validation 결과를 사용해 runtime 결과 자체를 조용히 rewrite

---

## 7. Product Track / Research Track 분리 규칙

### 7.1 Product Track
- 서비스 제공용 코드
- release gate 통과 대상
- strict reproducibility 필요

### 7.2 Research Track
- 최신 STE 논문 구현 실험
- ablation, prototype, 실패한 시도 포함 가능
- 결과가 좋아도 바로 production 승격 금지

### 7.3 승격 규칙
research 결과를 product로 올리려면 최소 아래를 만족해야 한다.
- contract 호환성 확인
- benchmark 재현성 확보
- merge gate 통과
- protected path 영향 분석 완료
- rollback 가능성 확인

---

## 8. Architecture Guard 판정 방식
각 위반은 아래 정보를 남긴다.

- rule id
- path
- import edge 또는 dependency edge
- severity
- why it matters
- autofix 가능 여부
- remediation suggestion

예시:
```json
{
  "rule": "RULE-ARCH-001",
  "severity": "critical",
  "path": "src/pipeline/rendering/render_service.py",
  "edge": "imports research.experimental_style_selector",
  "why": "production path is coupled to research runtime",
  "autofix_allowed": false,
  "suggestion": "introduce contract-backed adapter under infra or move experiment behind isolated feature branch"
}
```

---

## 9. protected path 특별 규칙
아래 경로는 일반 경로보다 강하게 보호한다.

- `core/contracts/`
- `evaluation/scoring/`
- `benchmarks/golden/`
- `harness/policies/`
- `release/`

규칙:
- autofix 금지
- 변경 이유 필수
- 영향 범위 분석 필수
- reviewer 승인이 없으면 merge 금지

---

## 10. 허용 예외
긴급 핫픽스 또는 마이그레이션 중에는 일시적 예외가 가능하다. 다만 아래를 반드시 포함해야 한다.

- 예외 rule
- 예외 범위
- 만료일
- 복구 계획
- 승인자

예외는 waiver 없이 허용하지 않는다.

---

## 11. 목표 상태
Architecture Guard의 성공 기준은 “규칙 많이 만들기”가 아니다. 다음 상태를 유지하는 것이다.

- core가 바깥 계층에 오염되지 않음
- 연구/실험 코드가 제품 코드를 흔들지 않음
- benchmark와 runtime이 부정 결합되지 않음
- pipeline 단계 간 책임이 분리됨
- contract와 policy가 중앙에서 관리됨

이 상태가 유지되어야 장기적으로 병렬 Agent 실행과 랄프 위검 루프를 안전하게 반복할 수 있다.
