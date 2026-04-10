# 11. Repository Governance Schedule

## 1. 목적

본 문서는 장기 프로젝트 운영을 위해 저장소 차원의 거버넌스 실행 주기를 정의한다. 목적은 다음과 같다.

- 코드 품질 저하를 조기에 발견한다.
- 아키텍처 드리프트를 누적되기 전에 차단한다.
- 기능 개발 속도와 유지보수 안정성 사이의 균형을 유지한다.
- 병렬 Agent 환경에서도 저장소의 일관성을 보장한다.
- 릴리즈 직전이 아니라 평소부터 배포 가능 상태를 유지한다.

이 문서의 대상은 다음과 같다.

- Feature Agent
- Test Agent
- Validation Agent
- Maintenance Agent
- Architecture Guard Agent
- Autofix Runner Agent
- Judge / Conductor Agent
- 인간 리뷰어 및 릴리즈 담당자

---

## 2. 운영 원칙

### 2.1 작은 주기로 자주 검사한다
대형 점검을 드물게 수행하는 방식은 장기적으로 실패한다. 가능한 많은 규칙을 PR 이전 또는 PR 단계에서 감지해야 한다.

### 2.2 빠른 검사와 무거운 검사를 분리한다
모든 규칙을 매 커밋마다 돌리면 개발 흐름이 과도하게 느려진다. 따라서 검사 레이어를 다음과 같이 분리한다.

- Fast lane: 수 초~수 분 내 종료 가능한 검사
- Standard lane: 일 단위 정기 검사
- Deep lane: 주간 또는 릴리즈 전 정밀 검사

### 2.3 자동 수정은 제한적으로만 사용한다
자동 수정은 저장소 위생을 돕는 수단이지, 의미 변경을 위임하는 수단이 아니다.

### 2.4 Protected Path는 별도 관리한다
다음 영역은 기본적으로 강한 보호를 받는다.

- contracts / schemas
- scoring rules
- golden benchmark assets
- release configs
- harness policy files
- security-sensitive config

### 2.5 연구 경로와 제품 경로를 분리한다
연구 실험은 자유롭게 시도하되, mainline 승격은 별도 게이트를 통과해야 한다.

---

## 3. 실행 레이어 개요

| 레이어 | 실행 주기 | 목적 | 대표 담당 |
|---|---|---|---|
| Pre-commit | 개발자 로컬 / Agent 작업 직후 | 즉시 차단 가능한 문제 제거 | Developer, Feature Agent |
| Pull Request | 모든 PR | 병합 전 기본 품질 확인 | CI, Maintenance Agent |
| Daily Governance | 매일 | 드리프트 조기 감지 | Maintenance Agent |
| Weekly Governance | 매주 | 구조적 부채 및 추세 관리 | Architecture Guard Agent |
| Release Governance | 릴리즈 전 | 배포 적합성 검증 | Judge, Release Owner |
| Quarterly Review | 분기 | 규칙 재설계 및 정책 개선 | Human Owner |

---

## 4. Pre-commit Governance

## 4.1 목적
개발자 또는 Agent가 만든 작은 변경이 저장소 위생을 즉시 깨뜨리지 않도록 한다.

## 4.2 실행 시점
- 로컬 커밋 전
- Agent가 patch 생성 직후
- 자동 수정 적용 전후

## 4.3 필수 검사
- formatter
- import ordering
- basic lint
- syntax check
- file naming convention
- forbidden temporary artifact detection
- changed-file scope unit test (가능한 경우)

## 4.4 실패 시 처리
- 자동 수정 가능 항목은 즉시 수정
- 자동 수정 불가 항목은 커밋 차단
- protected path 위반은 무조건 차단

## 4.5 허용 시간 예산
- 목표: 30초 이내
- 상한: 2분 이내

---

## 5. Pull Request Governance

## 5.1 목적
PR이 main branch 품질을 저하시키지 않는지 확인한다.

## 5.2 필수 입력
- PR diff
- changed files list
- 영향받는 모듈 목록
- 관련 benchmark subset
- 관련 contracts / schema 목록

## 5.3 필수 검사
- full lint / static analysis
- type check
- dependency rule validation
- architecture boundary validation
- output schema validation
- changed-path integration tests
- relevant benchmark smoke run
- prompt/template contract validation
- no secret / no credential check
- changelog or rationale check (정책상 필요한 경우)

## 5.4 PR 분류별 추가 검사

### 기능 변경 PR
- 관련 golden sample subset 실행
- regression diff 생성
- user-visible artifact snapshot 비교

### 아키텍처 변경 PR
- dependency graph diff
- module ownership diff
- public interface change report

### 연구 결과 승격 PR
- research track vs product track 비교 리포트
- 재현성 확인
- benchmark uplift 근거 제출

### 유지보수 PR
- 의미 변경 없음 검증
- autofix 범위 준수 검증

## 5.5 실패 시 처리
- hard fail 항목은 병합 차단
- soft fail 항목은 reviewer override 가능하나 이유 기록 필수

---

## 6. Daily Governance

## 6.1 목적
매일 작은 드리프트를 추적하고 누적 부채를 눈에 보이게 만든다.

## 6.2 실행 시점
- 매일 업무 시작 전 또는 심야 배치
- 권장: 저장소 사용량이 낮은 시간대

## 6.3 실행 항목
- dead code scan
- orphaned config scan
- TODO / FIXME inventory update
- test flakiness scan
- dependency drift summary
- benchmark smoke subset
- protected path change audit
- failed autofix attempt inventory
- architectural violation inventory

## 6.4 산출물
- `reports/daily_governance_report.md`
- `reports/daily_violations.json`
- `reports/flaky_tests.json`
- `reports/protected_path_audit.json`

## 6.5 운영 규칙
- 동일 위반이 3일 이상 지속되면 weekly escalation 대상으로 승격
- flaky test가 연속 2회 이상 탐지되면 test owner에게 할당
- protected path 변경 흔적은 별도 강조 표기

---

## 7. Weekly Governance

## 7.1 목적
주간 단위로 구조적 건전성과 유지보수 추세를 분석한다.

## 7.2 실행 항목
- duplication analysis
- module complexity trend
- dependency graph drift
- architecture violation trend
- test coverage drift
- benchmark category trend
- patch churn analysis
- ownership hot spot analysis
- repeated rollback / revert analysis
- research-to-product contamination scan

## 7.3 주간 리뷰 포인트
- 어떤 모듈이 반복적으로 깨지는가
- 어느 Agent가 unsafe patch를 자주 생성하는가
- 어느 benchmark split에서 지속적으로 회귀하는가
- 컨벤션 위반이 특정 디렉토리에 집중되는가
- 아키텍처 예외 규칙이 비정상적으로 늘어나는가

## 7.4 산출물
- `reports/weekly_architecture_drift.md`
- `reports/weekly_maintenance_scorecard.md`
- `reports/unsafe_autofix_trend.json`
- `reports/module_health_score.json`

---

## 8. Release Governance

## 8.1 목적
릴리즈 후보가 기능적으로뿐 아니라 운영적으로도 배포 가능한지 검증한다.

## 8.2 필수 검사
- full benchmark run
- golden set visual regression
- protected path integrity check
- config freeze check
- reproducibility check
- rollback artifact existence check
- release note completeness check
- security / secret scan
- maintenance debt waiver review

## 8.3 릴리즈 차단 조건 예시
- severe regression 존재
- unresolved architecture violation 존재
- protected path 무단 변경
- benchmark reproducibility 실패
- required rollback artifact 부재
- critical module test flakiness unresolved

## 8.4 릴리즈 승인 산출물
- `release/release_governance_report.md`
- `release/release_risk_matrix.json`
- `release/reproducibility_summary.md`

---

## 9. Quarterly Governance Review

## 9.1 목적
규칙 자체가 프로젝트 상황에 맞는지 재평가한다.

## 9.2 검토 항목
- false positive가 많은 규칙 정리
- 더 이상 의미 없는 규칙 제거
- 새로 필요한 보호 경로 추가
- 연구/제품 분리 정책 강화 필요성
- Agent 성능 기준 재조정
- benchmark set 확장 여부

## 9.3 인간 의사결정이 필요한 질문
- 지금 규칙이 개발 속도를 과도하게 저해하는가
- 유지보수 Agent의 자동 수정 범위를 확대할 수 있는가
- 아키텍처 예외를 제도화해야 하는가, 제거해야 하는가
- ownership 구조를 재조정해야 하는가

---

## 10. 권장 스케줄 예시

## 10.1 매 커밋
- formatter
- import ordering
- basic lint
- syntax check

## 10.2 매 PR
- static analysis
- boundary validation
- changed-path tests
- benchmark smoke subset

## 10.3 매일
- dead code scan
- flaky test scan
- daily governance report

## 10.4 매주
- dependency drift
- architecture drift
- complexity trend
- module health score

## 10.5 릴리즈 전
- full benchmark
- visual regression
- reproducibility
- release governance report

---

## 11. 병렬 Agent 환경에서의 실행 규칙

## 11.1 모든 작업 브랜치에 동일 정책 적용
브랜치별로 완화된 규칙을 두지 않는다. 단, research track은 제품 승격 전용 별도 게이트를 허용할 수 있다.

## 11.2 Agent별 역할 분리
- Feature Agent: 기능 구현
- Test Agent: 테스트 보강
- Maintenance Agent: 위생 및 규칙 검증
- Architecture Guard Agent: 의존성 및 경계 규칙 검증
- Judge Agent: 병합 적합성 판단

## 11.3 Judge가 보는 핵심 질문
- 기능 성능이 좋아졌는가
- 유지보수 비용을 증가시키지 않았는가
- 구조적 규칙 위반이 없는가
- 병합 후 mainline 건강도에 악영향이 없는가

---

## 12. 예외 처리 정책

다음 경우에 한해 예외를 허용할 수 있다.

- 긴급 장애 대응
- 릴리즈 차단 버그 핫픽스
- 외부 의존성 이슈로 인한 임시 우회

단, 예외 허용 시 반드시 남겨야 한다.

- 예외 사유
- 적용 범위
- 만료 시점
- 제거 담당자
- 후속 정리 일정

예외는 영구 규칙이 되어서는 안 된다.

---

## 13. KPI 예시

거버넌스가 실제로 작동하는지 보기 위한 운영 지표 예시는 다음과 같다.

- PR 단계 차단 비율
- merge 후 hotfix 발생률
- protected path 위반 건수
- unsafe autofix 발생 건수
- architecture violation 누적량
- flaky test 비율
- weekly module health score 추세
- revert / rollback 빈도

---

## 14. 결론

장기 프로젝트의 저장소 거버넌스는 선택적 장식이 아니라 품질 유지 장치다. 하네스 엔지니어링과 병렬 Agent 운영을 지속 가능하게 만들기 위해서는, 무엇을 언제 얼마나 강하게 검사할지 명확히 정해야 한다. 본 스케줄은 그 기준선을 제공한다.
