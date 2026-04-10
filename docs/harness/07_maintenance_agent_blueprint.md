# 07. Maintenance Agent Blueprint

## 1. 문서 목적
이 문서는 장기 프로젝트 운영을 위해 **유지보수 관리용 Agent(Maintenance Agent)** 를 어떻게 정의하고, 어떤 입력/출력 계약으로 동작시키며, 어떤 범위까지 자동화할지를 명확히 규정한다.

본 Agent의 목적은 단순한 코드 정리나 린트 통과가 아니다. 목표는 다음과 같다.

- 코드 품질 저하를 조기에 감지한다.
- 아키텍처 드리프트를 탐지한다.
- 컨벤션 위반을 누적되기 전에 차단한다.
- 자동 수정 가능한 항목은 안전하게 정리한다.
- 자동 수정이 위험한 항목은 계획과 근거를 남긴다.
- 최종적으로 기능 개발 루프와 하네스 엔지니어링 루프의 장기 안정성을 높인다.

이 프로젝트는 OCR, 번역, 광고 문구 현지화, inpainting, style estimation, rendering, validation, benchmark, research 실험 코드를 함께 다루므로 시간이 지날수록 구조가 쉽게 흔들린다. 따라서 Maintenance Agent는 선택 기능이 아니라 **프로젝트 거버넌스 구성 요소**로 취급한다.

---

## 2. Agent의 역할 정의

### 2.1 핵심 역할
Maintenance Agent는 아래 5가지 역할을 수행한다.

1. **Code Quality Watcher**
   - lint, format, type check, import 정리, dead code 후보 탐지
   - 과도한 복잡도, 긴 함수, god module 후보 탐지

2. **Architecture Guard**
   - 레이어 침범 탐지
   - 금지된 의존성 경로 탐지
   - research 코드가 production runtime으로 유입되는지 탐지
   - contract/schema drift 탐지

3. **Convention Enforcer**
   - 네이밍 규칙, 파일 배치 규칙, 테스트 규칙, config 배치 규칙 검사
   - prompt template, benchmark manifest, scoring 정책 파일의 위치/명명 규칙 검사

4. **Autofix Executor**
   - 허용된 범위 내에서만 자동 수정 수행
   - 의미 변경 가능성이 있는 수정은 절대 수행하지 않음

5. **Governance Reporter**
   - 위반 항목, 위험도, 영향 범위, 자동 수정 여부, 재실행 결과를 리포트로 남김
   - merge gate에 입력될 요약 보고서 생성

---

## 3. 프로젝트 내 위치
Maintenance Agent는 기능 Agent와 분리된 독립 역할로 운영한다.

### 3.1 권장 병렬 구조
- Feature Agent: 기능 구현
- Test Agent: 테스트 작성/보강
- Validation Agent: benchmark 및 quality 검증
- Research Agent: STE 논문/실험 경로 개선
- **Maintenance Agent: 구조/품질/규칙 감시 및 안전한 autofix**
- Judge/Conductor Agent: 전체 결과 취합 및 승격 판단

### 3.2 실행 타이밍
- PR/branch 생성 시
- 특정 폴더 변경량이 threshold 초과 시
- 일일/주간 저장소 정기 점검 시
- release candidate 생성 전

---

## 4. 입력 계약
Maintenance Agent는 아래 입력을 사용한다.

### 4.1 필수 입력
- repository snapshot 또는 target branch
- changed files 목록
- architecture rules 파일
- code convention policy 파일
- autofix allowlist policy 파일
- protected paths 목록
- test/lint/type 설정 파일
- benchmark/contract 관련 경로 목록

### 4.2 선택 입력
- 최근 7일간 drift report
- prior violations baseline
- flaky test 목록
- 팀이 승인한 예외 목록(waiver list)

### 4.3 입력 예시
```yaml
repo:
  root: .
  target_branch: feature/render-quality-v3
  compare_base: main

paths:
  protected:
    - core/contracts/
    - evaluation/scoring/
    - benchmarks/golden/
    - harness/policies/
    - release/
  research:
    - research/
    - experiments/
  production:
    - src/
    - app/

policies:
  convention: docs/08_code_convention_policy.md
  architecture_rules: docs/09_architecture_guard_rules.md
  autofix_policy: docs/10_autofix_policy.md

checks:
  run_lint: true
  run_typecheck: true
  run_unit_tests_changed_scope: true
  run_dependency_guard: true
  run_dead_code_scan: true
```

---

## 5. 출력 계약
Maintenance Agent는 언제나 구조화된 결과를 남긴다.

### 5.1 필수 출력물
- `maintenance_report.md`
- `violations.json`
- `autofix.patch` 또는 `autofix_summary.json`
- `architecture_drift_report.md`
- `merge_maintenance_recommendation.json`

### 5.2 violations.json 예시
```json
{
  "run_id": "maint-2026-04-10T12-30-00Z",
  "target_branch": "feature/render-quality-v3",
  "summary": {
    "total": 14,
    "critical": 1,
    "high": 3,
    "medium": 6,
    "low": 4,
    "autofix_applied": 5,
    "manual_review_required": 4
  },
  "violations": [
    {
      "id": "ARCH-004",
      "severity": "critical",
      "category": "architecture",
      "path": "src/rendering/renderer.py",
      "rule": "production_must_not_import_research_runtime",
      "message": "renderer imports research.experimental_style_selector",
      "autofix_allowed": false,
      "requires_human_review": true
    }
  ]
}
```

### 5.3 merge recommendation 예시
```json
{
  "maintenance_status": "fail",
  "blocking_reasons": [
    "critical architecture violation detected",
    "protected path modified without approved justification"
  ],
  "autofix_applied": true,
  "manual_followups": [
    "split experimental style selector from production rendering pipeline"
  ]
}
```

---

## 6. 실행 모드

### 6.1 Audit Only
- 리포트만 생성
- 수정 없음
- 프로젝트 초반이나 false positive가 많을 때 사용

### 6.2 Safe Autofix
- formatting, import order, unused import 제거, 명백한 trivial convention fix만 수행
- 실행 후 반드시 lint/typecheck 재검증

### 6.3 Plan Only
- 구조 변경이 필요한 항목에 대해 patch 대신 단계별 리팩터링 계획 생성
- 사람이 승인하기 전에는 코드 수정 금지

### 6.4 Release Guard
- release candidate 대상에 대해 가장 엄격하게 적용
- autofix보다 **차단 및 리포팅** 중심

---

## 7. 분류 체계
모든 위반 항목은 아래 축으로 분류한다.

### 7.1 카테고리
- formatting
- lint
- typing
- architecture
- dependency
- convention
- duplication
- dead_code
- config_drift
- test_gap
- documentation_gap

### 7.2 심각도
- `critical`: merge 차단
- `high`: 기본적으로 merge 차단, waiver 필요
- `medium`: 누적 감시, 특정 개수 이상이면 차단
- `low`: 리포트만 남김

### 7.3 수정 가능 여부
- `autofix_allowed`
- `manual_review_required`
- `plan_required`

---

## 8. 핵심 판단 원칙

### 8.1 안전성 우선
“더 깔끔한 코드”보다 “기능 의미 불변”이 우선이다.

### 8.2 계약 우선
schema, benchmark manifest, scoring rule, protected config는 일반 코드보다 더 엄격하게 다룬다.

### 8.3 연구와 제품 분리
연구 코드의 편의성과 제품 코드의 안정성을 혼동하지 않는다.

### 8.4 반복 가능성
같은 입력에서 같은 결과가 나와야 한다. Agent 판단이 매번 흔들리면 governance 역할을 할 수 없다.

### 8.5 설명 가능성
모든 수정 제안은 “무엇이 문제인지 / 왜 문제인지 / 어떤 규칙을 위반했는지 / 자동 수정 가능한지”를 남겨야 한다.

---

## 9. 이 프로젝트에서 특히 감시해야 할 항목

### 9.1 파이프라인 경계 위반
- OCR 단계가 localization 정책을 직접 참조
- renderer가 번역 provider 세부 구현에 의존
- validation이 UI formatting 레이어를 직접 참조

### 9.2 연구 코드 유입
- `research/`, `experiments/` 내부 모듈을 production runtime에서 import
- 논문 실험용 heuristic이 mainline policy로 유입

### 9.3 계약 드리프트
- OCR result schema 변경 후 renderer/validator 미반영
- style token 구조 변경 후 benchmark scorer 미반영
- prompt template의 필수 필드 누락

### 9.4 무분별한 예외 처리
- broad exception 증가
- fallback 누적
- silent failure 증가

### 9.5 평가/배포 경계 훼손
- benchmark golden file을 feature branch에서 임의 갱신
- score threshold를 코드 내에서 직접 수정

---

## 10. 운영 지표
Maintenance Agent 자체도 품질 지표로 관리한다.

### 10.1 필수 지표
- false positive rate
- unsafe autofix rate
- missed violation rate
- protected path false touch count
- rerun reproducibility rate
- autofix 후 lint/typecheck success rate

### 10.2 운영 목표 예시
- critical false positive rate < 3%
- unsafe autofix rate = 0%
- protected path 무단 수정 = 0
- safe autofix 후 재검증 성공률 > 98%

---

## 11. 예외 처리 정책
일시적으로 허용된 예외는 waiver로 관리한다.

예외는 아래 정보를 반드시 포함해야 한다.
- rule id
- 적용 경로
- 예외 사유
- 승인자
- 만료일
- 후속 제거 계획

예외는 코드 주석으로 남기지 말고 중앙 waiver 파일에서 관리한다.

---

## 12. 실패 시 동작 원칙
Maintenance Agent 실패는 아래로 나뉜다.

### 12.1 Agent 자체 실패
- tool crash
- parser error
- repo scan incomplete
- report 생성 실패

이 경우 결과를 신뢰할 수 없으므로 **status = infra_error** 로 남기고 재시도를 수행한다.

### 12.2 위반 탐지 실패 아님
검사 결과 위반이 많은 것은 Agent 실패가 아니라 **프로젝트 상태의 경고**이다. 이 둘을 구분해야 한다.

---

## 13. 단계별 도입 전략

### Phase 1. Read-only 도입
- audit only
- false positive 조정
- 팀 합의 규칙 고정

### Phase 2. Safe autofix 도입
- formatting/import/unused 범위만 허용
- 재검증 성공 시에만 patch 사용

### Phase 3. Governance 통합
- merge gate 연결
- protected path 및 architecture drift 강제 차단
- release guard 모드 활성화

---

## 14. 최종 목표 상태
프로젝트가 성숙 단계에 들어가면 Maintenance Agent는 아래 상태를 달성해야 한다.

- 모든 PR/branch에 대해 자동 검사 수행
- 안전한 정리는 자동 처리
- 위험한 변경은 자동 차단 또는 계획 생성
- 연구 트랙과 제품 트랙의 경계를 계속 유지
- 장기적으로 코드 퀄리티와 구조 일관성을 비용 낮게 유지

즉, Maintenance Agent의 성공 기준은 “코드를 많이 고쳤다”가 아니라 **프로젝트가 오랫동안 덜 망가지게 만들었다**이다.
