# 12. Maintenance Gate Checklist

## 1. 목적

본 문서는 유지보수 Agent, Architecture Guard Agent, Autofix Runner Agent가 생성한 결과물을 병합 가능 상태인지 평가하기 위한 체크리스트를 정의한다.

이 체크리스트의 목적은 다음과 같다.

- 코드 위생 개선 작업이 기능 의미를 훼손하지 않았는지 확인한다.
- 자동 수정 범위가 정책을 벗어나지 않았는지 확인한다.
- 아키텍처 경계가 오히려 더 나빠지지 않았는지 확인한다.
- 장기 유지보수 비용을 줄이는 방향의 변경만 승격한다.

본 문서는 기능 성능 게이트를 대체하지 않는다. 기능 게이트와 별도로, 유지보수 관점의 승인 기준을 제공한다.

---

## 2. 평가 대상

다음 변경은 본 체크리스트 적용 대상이다.

- formatting / lint cleanup PR
- import 정리 PR
- dead code 제거 PR
- naming / placement convention 정리 PR
- 테스트 구조 정리 PR
- 설정 파일 정리 PR
- 아키텍처 의존성 정리 PR
- 자동 수정 Agent가 생성한 patch
- 대규모 리팩터링 계획의 일부 단계 PR

---

## 3. 게이트 레벨 정의

| 게이트 레벨 | 의미 | 결과 |
|---|---|---|
| L0 | 정보성 리포트만 생성 | 자동 차단 없음 |
| L1 | 소규모 위생 변경 | 규칙 위반 시 병합 차단 |
| L2 | 구조 변경 가능성 있는 유지보수 변경 | 리뷰어 승인 필수 |
| L3 | 고위험 리팩터링 / protected path 관련 변경 | 명시적 인간 승인 + 추가 검증 필수 |

---

## 4. 기본 원칙

### 4.1 유지보수 변경은 의미 보존이 기본이다
유지보수 PR은 기본적으로 기능 semantics를 바꾸지 않아야 한다.

### 4.2 자동 수정은 allowlist 범위만 허용한다
정책에 명시되지 않은 수정은 자동 수정으로 간주하지 않는다.

### 4.3 protected path 변경은 특별 취급한다
contracts, scoring, benchmark, release, security 관련 경로는 일반적인 cleanup 논리로 병합될 수 없다.

### 4.4 큰 리팩터링은 계획 단위로 분해한다
한 번에 많은 의미적 이동을 포함하는 patch는 승인하지 않는다.

---

## 5. Gate A: Execution Integrity

다음 항목을 모두 만족해야 한다.

- [ ] patch가 clean apply 된다.
- [ ] formatter / linter / type check가 통과한다.
- [ ] 변경 파일 목록이 선언된 범위와 일치한다.
- [ ] 임시 파일, debug artifact, local-only 설정이 포함되지 않았다.
- [ ] broken import, broken reference, broken path가 없다.

차단 조건:
- patch apply 실패
- 정적 검사 실패
- 선언되지 않은 파일 대량 변경

---

## 6. Gate B: Autofix Policy Compliance

자동 수정 Agent 결과라면 다음 항목을 추가로 본다.

- [ ] 수정 내용이 autofix allowlist 범위 안에 있다.
- [ ] public API signature를 변경하지 않았다.
- [ ] business rule, scoring rule, rendering rule을 수정하지 않았다.
- [ ] config semantics를 변경하지 않았다.
- [ ] protected path에 대한 수정이 없다. 또는 별도 승인 근거가 있다.
- [ ] patch rationale이 함께 제공된다.

차단 조건:
- allowlist 밖 수정 포함
- 의미 변경 가능성 높은 수정 포함
- rationale 없음

---

## 7. Gate C: Convention Compliance

- [ ] 파일 위치가 repository convention을 따른다.
- [ ] 네이밍 규칙을 만족한다.
- [ ] 테스트 파일 구조가 정책과 일치한다.
- [ ] schema / config / prompt / benchmark 파일 배치가 정책과 일치한다.
- [ ] 중복 유틸 생성 없이 기존 공통 모듈을 사용했다.

주의:
컨벤션 위반을 고친다는 명목으로 더 큰 구조 혼란을 만들면 실패다.

---

## 8. Gate D: Architecture Guard

- [ ] 의존성 방향이 허용 규칙을 따른다.
- [ ] UI / app / orchestration이 infra 세부 구현에 부적절하게 결합되지 않았다.
- [ ] research path와 product path가 섞이지 않았다.
- [ ] renderer, OCR, localization, validation, scoring, benchmark 모듈 간 책임 경계가 유지된다.
- [ ] forbidden dependency가 추가되지 않았다.
- [ ] cyclic dependency가 새로 생기지 않았다.

차단 조건:
- 레이어 침범
- research to production contamination
- scoring / contract / validation core 직접 훼손

---

## 9. Gate E: Semantic Safety

유지보수 PR이라도 최소한의 의미 안전성 확인이 필요하다.

- [ ] 주요 유닛 테스트가 통과한다.
- [ ] 관련 integration test가 통과한다.
- [ ] 변경 영역 benchmark smoke subset에서 회귀가 없다.
- [ ] 시각적 산출물이 예상과 다르게 변하지 않았다.
- [ ] prompt/template 정리라면 출력 계약이 유지된다.

고위험 항목 예시:
- renderer 관련 정리
- OCR normalization 관련 정리
- translation unit schema 변경
- validation report formatter 변경

이 경우 L2 또는 L3로 승격해야 한다.

---

## 10. Gate F: Protected Path Review

다음 경로에 변경이 있다면 반드시 별도 검토한다.

- `contracts/`
- `schemas/`
- `evaluation/scoring/`
- `benchmarks/golden/`
- `harness/policies/`
- `release/`
- `security/`

체크 항목:
- [ ] 왜 protected path 수정이 필요한지 설명이 있다.
- [ ] 기능 변경인지 유지보수 변경인지 구분이 명확하다.
- [ ] 영향 범위가 기록되어 있다.
- [ ] 재현성 또는 benchmark 영향 검토가 있다.
- [ ] human reviewer가 명시적으로 승인했다.

차단 조건:
- 설명 없는 protected path 변경
- 유지보수 PR로 위장된 정책/규칙 변경

---

## 11. Gate G: Risk and Reversibility

- [ ] 변경을 롤백하기 쉽다.
- [ ] patch가 너무 크지 않다.
- [ ] 변경 사유와 기대 효과가 문서화되어 있다.
- [ ] 실패 시 복구 절차가 명확하다.
- [ ] 대규모 rename / move라면 분리된 단계로 수행되었다.

권장 기준:
- 한 PR에서 여러 종류의 정리를 동시에 하지 않는다.
- rename, move, logic touch를 섞지 않는다.

---

## 12. Gate H: Reporting Completeness

- [ ] violation report가 첨부되었다.
- [ ] autofix report가 첨부되었다. 해당하는 경우.
- [ ] architecture drift diff가 첨부되었다. 해당하는 경우.
- [ ] benchmark smoke result가 첨부되었다.
- [ ] reviewer가 판단 가능한 최소 근거가 제공된다.

근거 없는 “cleanup” PR은 병합하지 않는다.

---

## 13. 승인 결정 규칙

### 자동 승인 가능
다음을 모두 만족하면 자동 승인 후보가 될 수 있다.

- formatting / import / trivial lint fix only
- allowlist 내 수정 only
- protected path untouched
- tests green
- benchmark smoke no regression
- architecture rule no violation

### 리뷰어 승인 필요
다음 중 하나라도 해당하면 리뷰어 승인이 필요하다.

- directory move 포함
- public symbol rename 포함
- test structure wide change 포함
- config reorganization 포함
- architecture boundary 근처 파일 수정

### 고위험 승인 절차 필요
다음 중 하나라도 해당하면 L3로 간주한다.

- protected path 수정
- contract/schema 수정
- scoring or validation core 수정
- renderer pipeline 주변 리팩터링
- research/product 경계 수정

---

## 14. 차단 사유 템플릿

차단 시 아래 형식으로 기록한다.

```text
[Maintenance Gate Failure]
Gate: <A-H>
Reason: <구체적 사유>
Risk Level: <low|medium|high|critical>
Required Action: <수정 또는 재분리 필요 항목>
Reviewer Note: <선택>
```

예시:

```text
[Maintenance Gate Failure]
Gate: B
Reason: Autofix patch modified renderer instruction mapping, which is outside allowlist.
Risk Level: high
Required Action: revert semantic changes and split formatting-only patch from renderer logic patch.
Reviewer Note: maintenance PR must not alter rendering semantics.
```

---

## 15. 승인 기록 템플릿

```text
[Maintenance Gate Pass]
Level: <L1|L2|L3>
Scope: <변경 범위>
Evidence:
- lint/type/test: pass
- architecture guard: pass
- benchmark smoke: pass
- protected path: no change
Notes: <추가 메모>
```

---

## 16. 운영 팁

- cleanup PR은 작게 유지한다.
- 의미 변경 가능성이 있으면 maintenance PR로 포장하지 않는다.
- autofix Agent는 보수적으로 운용한다.
- Architecture Guard 결과와 Maintenance Gate 결과를 함께 본다.
- weekly governance에서 반복 실패 패턴을 추적한다.

---

## 17. 결론

유지보수 변경은 기능 개발보다 안전해 보여서 쉽게 병합되기 쉽다. 그러나 장기 프로젝트에서는 오히려 작은 cleanup 누적이 구조를 무너뜨릴 수 있다. 따라서 유지보수 PR도 명시적인 게이트를 통과해야 하며, 자동 수정은 항상 정책과 증거 기반으로만 승인되어야 한다.
