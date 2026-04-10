# 이미지 현지화 서비스 목표 및 요구사항 정리

## 1. 프로젝트 최종 목표
현재의 OCR/번역/인페인팅/재렌더링 기반 MVP를 출발점으로 삼아,
**원본 포스터의 디자인과 레이아웃을 최대한 보존하면서도 자연스러운 현지화 결과를 생성하는 서비스**를 구축하고 배포하는 것이 최종 목표다.

여기서 말하는 “제대로 된 서비스”는 단순 번역기가 아니라 다음을 만족해야 한다.

- 이미지 내부 원문 텍스트를 검출하고 인식할 수 있어야 한다.
- 타겟 국가/언어에 맞는 문구로 자연스럽게 재작성할 수 있어야 한다.
- 배경 손상, 글자 뜸, 정렬 깨짐, 스타일 붕괴를 최소화해야 한다.
- 결과 품질을 주관이 아니라 **측정 가능한 기준**으로 검증해야 한다.
- 반복 실험과 회귀 검증이 가능해야 한다.
- 결국 서비스/API/배치 형태로 배포 가능한 구조여야 한다.

---

## 2. 현재 상태에 대한 해석
업로드된 현재 프로젝트는 이미 다음 구조를 포함하고 있다.

- `OCR -> localization -> inpaint -> render -> validate` 파이프라인
- PaddleOCR 기반 OCR 어댑터
- style estimator / renderer / inpainter 모듈 분리
- quality gate
- STE 실험용 export (`docs/ste_experiment_design.md`, `usecases/ste_dataset.py`)

즉, 지금 필요한 것은 “무에서 유를 만드는 설계”가 아니라,
**현재 MVP를 흔들리지 않는 개발 시스템으로 바꾸는 하네스 엔지니어링과 운영 루프의 정립**이다.

---

## 3. 핵심 문제 정의
현재 결과물이 흔들리는 원인은 기능 부족 하나만이 아니라, 아래 문제가 동시에 섞여 있을 가능성이 높다.

### 3.1 문제 유형
1. **입력 품질 불안정**
   - OCR 오검출/오인식
   - polygon/bbox 품질 불안정
   - small text, curved text, rotated text 대응 부족

2. **후처리 품질 불안정**
   - inpainting 잔상
   - 렌더링 위치 오차
   - overflow / multiline 처리 미흡
   - 폰트/컬러/스트로크/그림자 재현 부족

3. **문구 생성 품질 불안정**
   - literal translation 문제
   - 마케팅 문맥 불일치
   - 지역 언어 관습 반영 부족

4. **평가 체계 부족**
   - 무엇이 개선인지 정량 기준이 약함
   - 이전 대비 좋아졌는지 회귀 여부 확인 어려움
   - 포스터 타입별 benchmark 부재

5. **실험 운영 방식 부족**
   - 기능 추가는 되지만 재현 가능한 실험 체계가 약함
   - 병렬 실험 결과가 같은 기준으로 비교되지 않음
   - agent 별 역할/입출력 계약이 흐림

---

## 4. 제품 수준 목표
서비스가 목표 수준에 도달했다고 보기 위한 상위 제품 목표는 다음과 같다.

### 4.1 기능 목표
- 포스터/배너/광고 이미지 입력
- 원문 텍스트 영역 자동 검출
- 타겟 언어 및 시장 선택
- 번역 + 현지화 카피 생성
- 원본 디자인 훼손 최소화 편집
- 결과 이미지와 디버그 산출물 저장
- 비교 결과 리포트 생성

### 4.2 품질 목표
- 텍스트 영역 경계 외 손상 최소화
- 편집 흔적 최소화
- 재렌더링 텍스트 가독성 확보
- OCR 재검출 기준으로 타겟 문구 재인식 가능
- 동일 입력에 대해 반복 가능한 결과 확보

### 4.3 엔지니어링 목표
- 각 단계가 독립 실험 가능해야 한다.
- baseline 과 candidate 를 항상 비교할 수 있어야 한다.
- 병렬 agent 가 서로 다른 개선안을 동시에 실험할 수 있어야 한다.
- 결과가 좋아진 경우에만 mainline 으로 합류해야 한다.

---

## 5. 요구사항 분류

## 5.1 기능 요구사항
### FR-01. OCR 검출/인식
- 다양한 포스터 텍스트를 검출/인식해야 한다.
- 회전, 다중 행, small text, 장식 텍스트에 대한 대응이 필요하다.

### FR-02. 현지화 문구 생성
- 단순 직역이 아닌 광고 문맥에 맞는 재작성 기능이 필요하다.
- headline / subcopy / CTA / fine print 등 역할별 rewriting 정책이 필요하다.

### FR-03. 배경 복원
- 텍스트 제거 후 배경 질감이 자연스러워야 한다.
- bbox erase 수준을 넘는 mask 기반 복원이 필요하다.

### FR-04. 스타일 보존 렌더링
- 원본 레이아웃, 정렬, 색상, 두께, 그림자, 줄바꿈을 가능한 한 보존해야 한다.
- 공간 제약 내 자동 축소/줄바꿈/정렬 보정이 필요하다.

### FR-05. 품질 검증
- OCR 재인식, overflow, alignment, artifact, mask leakage 등을 자동 검증해야 한다.
- 결과물마다 quality report 가 생성되어야 한다.

### FR-06. 실험 추적
- 각 실험의 입력, 설정, 중간 산출물, 최종 결과, 점수를 저장해야 한다.
- baseline / candidate 간 비교가 가능해야 한다.

### FR-07. 서비스화
- CLI 수준을 넘어 향후 API 또는 batch worker 로 확장 가능해야 한다.
- inference orchestration 과 asset storage 구조가 분리되어야 한다.

---

## 5.2 비기능 요구사항
### NFR-01. 재현성
- 같은 입력, 같은 설정이면 동일하거나 허용 가능한 오차 범위 내 동일 결과가 나와야 한다.

### NFR-02. 관측 가능성
- 실패 원인이 OCR인지, 번역인지, 인페인팅인지, 렌더링인지 추적 가능해야 한다.

### NFR-03. 확장성
- 기존 baseline pipeline 과 향후 STE backbone(AnyText 계열 등)을 공존시켜야 한다.

### NFR-04. 모듈성
- OCR / localization / inpainting / rendering / validation 을 계약 기반으로 교체 가능해야 한다.

### NFR-05. 회귀 방지
- 특정 개선이 전체 품질을 악화시키지 않도록 regression harness 가 필요하다.

### NFR-06. 배포 가능성
- 환경 의존성을 통제하고, 모델/폰트/설정 버전을 명시할 수 있어야 한다.

---

## 6. 검증 기준
하네스 엔지니어링에서 최소한 아래 축을 점수화해야 한다.

### 6.1 OCR 축
- source OCR detection recall
- source OCR recognition confidence
- final OCR target-text match rate

### 6.2 시각 품질 축
- mask leakage score
- background artifact score
- edge halo score
- alignment deviation
- overflow / clipping 여부

### 6.3 스타일 유사도 축
- text color similarity
- font size / weight approximation
- shadow / stroke preservation
- layout similarity

### 6.4 제품 적합성 축
- localized copy acceptability
- CTA naturalness
- headline brevity fit
- locale appropriateness

### 6.5 운영 축
- pipeline success/failure rate
- stage latency
- batch throughput

---

## 7. 단계별 목표 로드맵

### Phase 1. 기준선 고정
- 현재 MVP baseline을 공식 기준선으로 확정
- 대표 테스트셋 수집
- 산출물/점수 포맷 표준화
- pass/fail 게이트 정의

### Phase 2. 하네스 구축
- 실행 harness, scoring harness, regression harness 구축
- agent 별 작업 계약 정의
- 실험 결과 자동 비교 리포트 생성

### Phase 3. 품질 개선 루프
- OCR / inpainting / renderer / copywriting 각각 병렬 개선
- best-of-breed 후보를 baseline과 비교
- 개선안만 단계적으로 병합

### Phase 4. STE 통합
- STE 전용 adapter 도입
- crop/mask/target text 기반 실험 수행
- baseline renderer vs STE 모델 정량 비교

### Phase 5. 서비스화
- API / worker / storage / job tracking 분리
- 배포 파이프라인 구축
- 운영용 품질 게이트 연결

---

## 8. 지금 당장 문서화해야 할 결정 사항
1. baseline pipeline 을 무엇으로 고정할지
2. 대표 테스트셋을 어떻게 나눌지
   - clean poster
   - noisy poster
   - dense typography
   - complex background
   - multilingual mix
3. score schema 를 어떻게 정의할지
4. agent 역할을 어떻게 분리할지
5. merge 기준을 무엇으로 둘지

이 다섯 가지가 먼저 고정되어야 이후의 병렬 agent 와 랄프 위검 루프가 흔들리지 않는다.
