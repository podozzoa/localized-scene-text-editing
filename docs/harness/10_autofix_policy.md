# 10. Autofix Policy

## 1. 문서 목적
이 문서는 Maintenance Agent 또는 관련 자동화 시스템이 어떤 수정까지 자동 수행할 수 있는지, 어떤 수정은 절대 자동 수행하면 안 되는지 정의한다.

자동화의 목적은 작업량 절감이지만, 장기 프로젝트에서는 **자동 수정이 기능 의미를 바꾸지 않도록 제한**하는 것이 더 중요하다. 따라서 이 정책은 “많이 고친다”보다 “안전하게 고친다”를 우선한다.

---

## 2. 기본 원칙

### 2.1 의미 보존 우선
자동 수정은 코드의 의미를 바꾸지 않는 범위로 제한한다.

### 2.2 재검증 필수
모든 autofix는 실행 후 최소한 다음을 다시 통과해야 한다.
- formatter/lint
- typecheck
- changed-scope unit/integration test

### 2.3 protected path 불가침
protected path는 자동 수정 금지다.

### 2.4 설명 없는 수정 금지
모든 autofix는 어떤 규칙을 근거로 어떤 파일에 무엇을 바꿨는지 남겨야 한다.

### 2.5 실패 시 patch 폐기
재검증 실패 시 autofix 결과는 자동 폐기한다.

---

## 3. Autofix 실행 레벨

### Level 0. Disabled
- 자동 수정 없음
- audit/report only

### Level 1. Safe Cosmetic
- formatting
- import ordering
- trailing whitespace 제거
- newline normalization

### Level 2. Safe Structural Hygiene
- unused import 제거
- 명백한 dead local 변수 제거(엄격 조건)
- trivial convention rename 제안 또는 제한적 수정

### Level 3. Plan Only
- 구조적 리팩터링이 필요한 항목은 코드 수정하지 않고 plan 생성

기본 권장값은 **Level 1 또는 Level 2** 이다.

---

## 4. 자동 수정 허용 항목

### 4.1 formatting
허용:
- 코드 포맷 정리
- 공백, 줄바꿈, indentation 표준화

조건:
- formatter가 deterministic 해야 함
- 재실행 시 같은 결과여야 함

### 4.2 import order
허용:
- import 정렬
- 중복 import 제거
- unused import 제거

조건:
- side effect import가 아닌 경우만
- import 제거 후 재검증 필수

### 4.3 trivial lint fix
허용 예시:
- 사용되지 않는 지역 변수 제거
- 중복 공백/사소한 style 위반 정리
- 명백한 typo 수정 제안

조건:
- public contract, external interface, schema field 이름 변경 금지

### 4.4 boilerplate generation
허용:
- 누락된 test skeleton 생성
- 문서 템플릿/ADR 템플릿 생성
- schema/example output template 생성

조건:
- 기존 의미를 바꾸지 않는 보조 생성물이어야 함

---

## 5. 자동 수정 금지 항목
아래는 기본적으로 자동 수정 금지다.

### 5.1 public interface 변경
예:
- 함수 시그니처 변경
- API request/response field 변경
- schema key 변경
- config key rename

### 5.2 contract/schema 변경
예:
- OCR result schema field 구조 변경
- translation unit 필수 필드 수정
- render instruction 구조 변경

### 5.3 scoring / threshold 변경
예:
- merge gate threshold 변경
- benchmark weight 변경
- validation rule 기준값 변경

### 5.4 pipeline behavior 변경
예:
- OCR fallback 정책 변경
- translation provider 선택 정책 변경
- rendering layout 알고리즘 변경
- inpainting mask 규칙 변경

### 5.5 protected path 수정
예:
- `core/contracts/`
- `evaluation/scoring/`
- `benchmarks/golden/`
- `harness/policies/`
- `release/`

### 5.6 연구/제품 경계 수정
예:
- research 코드를 product로 옮김
- import 경계 재구성
- 모듈 split/merge

### 5.7 테스트 의미 변경
예:
- failing test를 pass시키기 위해 assertion 완화
- regression test baseline 무단 갱신

---

## 6. 조건부 허용 항목
아래는 조건을 만족할 때만 제한적으로 허용한다.

### 6.1 private symbol rename
허용 조건:
- 외부 참조 없음
- 테스트 통과
- contract 영향 없음
- path가 protected 아님

### 6.2 dead code 제거
허용 조건:
- 완전한 미참조 상태가 도구로 확인됨
- reflection/dynamic loading/registry 사용 여부가 없음을 확인
- rollback 용이

### 6.3 문서/주석 정리
허용 조건:
- 코드 의미와 불일치 제거
- 계약 문서 변경 시 관련 영향 표기

---

## 7. Autofix 의사결정 표

| 항목 | 자동 수정 | 재검증 | 사람 승인 |
|---|---:|---:|---:|
| formatting | 허용 | 필요 | 불필요 |
| import ordering | 허용 | 필요 | 불필요 |
| unused import 제거 | 허용 | 필요 | 불필요 |
| private local dead code 제거 | 조건부 | 필요 | 경우에 따라 |
| public function rename | 금지 | - | 필요 |
| schema field 변경 | 금지 | - | 필요 |
| scoring threshold 변경 | 금지 | - | 필요 |
| protected path 수정 | 금지 | - | 필요 |
| research->product 이동 | 금지 | - | 필요 |
| test baseline 갱신 | 금지 | - | 필요 |

---

## 8. 실행 후 검증 규칙
Autofix 적용 후 반드시 아래를 수행한다.

1. formatter/lint 재실행
2. typecheck 재실행
3. changed-file 또는 changed-scope tests 재실행
4. import/dependency graph 재스캔
5. protected path 침범 여부 재확인

하나라도 실패하면:
- patch 폐기
- `autofix_status = reverted`
- manual review 항목으로 승격

---

## 9. 리포트 형식
Autofix 결과는 아래를 포함해야 한다.

- fix id
- target path
- violated rule
- changed lines summary
- why safe
- verification results
- reverted 여부

예시:
```json
{
  "fix_id": "AUTOFIX-2026-0410-003",
  "path": "src/pipeline/ocr/text_extractor.py",
  "rule": "unused_import",
  "change": "removed unused import 'json'",
  "why_safe": "import had no side effects and symbol was not referenced",
  "verification": {
    "lint": "pass",
    "typecheck": "pass",
    "tests": "pass"
  },
  "reverted": false
}
```

---

## 10. protected path 정책
아래 경로는 자동 수정 대상에서 제외한다.

- `core/contracts/`
- `evaluation/scoring/`
- `benchmarks/golden/`
- `harness/policies/`
- `release/`

예외 없음이 기본이다. 정말 필요한 경우에도 autofix가 아니라 **plan only** 로 처리한다.

---

## 11. Human-in-the-loop 규칙
다음 항목은 자동 수정 대신 항상 사람 승인 절차를 거친다.

- external behavior 변경 가능성 있는 수정
- public interface 변경
- 실험 코드 승격 관련 수정
- benchmark/merge gate 정책 변경
- 테스트 baseline 재생성
- 성능과 품질의 trade-off가 있는 수정

---

## 12. 실패 사례 예시

### 잘못된 자동 수정 예시 1
failing regression test를 없애기 위해 golden baseline 파일을 갱신함.

판정:
- 금지
- benchmark integrity 훼손

### 잘못된 자동 수정 예시 2
unused처럼 보이는 branch를 제거했지만 실제로 feature flag 경로에서 사용됨.

판정:
- 금지 또는 강한 조건부
- dynamic path 확인 필요

### 잘못된 자동 수정 예시 3
naming 통일을 이유로 schema field 이름을 rename함.

판정:
- 금지
- external contract 파손

---

## 13. 운영 권장안
초기에는 아래처럼 운영한다.

### 단계 1
- Level 0 또는 Level 1
- false positive와 unsafe patch를 최소화

### 단계 2
- Level 2 확장
- dead code/unused 제거를 제한적으로 허용

### 단계 3
- 구조적 문제는 autofix하지 않고 plan 생성
- 리팩터링 전용 branch에서 별도 처리

---

## 14. 최종 목표 상태
Autofix의 최종 목표는 “사람 없이 다 고친다”가 아니다.

진짜 목표는 다음이다.
- 반복적으로 발생하는 사소한 위반을 자동으로 청소한다.
- 위험한 수정은 자동으로 건드리지 않는다.
- 모든 수정은 재검증과 기록을 남긴다.
- 장기적으로 코드 품질을 유지하면서 기능/평가/배포 안정성을 해치지 않는다.

즉, Autofix는 **무인 리팩터링 시스템**이 아니라 **안전한 저장소 위생 관리 시스템**이어야 한다.
