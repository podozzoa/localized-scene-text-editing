# 벤치마크 매니페스트 템플릿

## 1. 문서 목적
이 문서는 이미지 현지화 서비스의 자동 실험, 자동 비교, 자동 승격 판단을 위해 사용하는 **benchmark manifest 표준**을 정의한다.

이 매니페스트는 다음 문제를 해결하기 위해 필요하다.

- 샘플마다 입력 형식이 달라져 실행 로직이 흔들리는 문제
- 실험 실행은 되었지만 무엇을 기대값으로 비교해야 하는지 불명확한 문제
- 병렬 Agent가 서로 다른 전제와 다른 샘플셋으로 작업해 결과를 비교할 수 없는 문제
- 서비스화 직전까지 가서도 “어떤 샘플에서 왜 망가졌는지” 추적이 어려운 문제

즉, 이 문서의 목표는 단순 데이터 목록이 아니라,
**하네스가 자동으로 읽고 실행하고 점수화하고 리포트까지 만들 수 있는 입력 계약**을 명확히 하는 것이다.

---

## 2. 매니페스트 설계 원칙

### Principle A. 샘플 하나가 실험 단위다
한 장의 포스터 또는 광고 이미지가 하나의 기본 샘플 단위다.
단, 한 이미지 안에 여러 텍스트 블록이 있을 수 있으므로 region 단위 메타데이터를 포함해야 한다.

### Principle B. 기대값은 “단 하나의 정답”이 아닐 수 있다
현지화 카피는 여러 acceptable candidate가 가능하다.
따라서 exact string 하나만 저장하지 말고, **허용 가능한 표현군**과 **길이 제약**, **금지 표현**도 함께 저장한다.

### Principle C. 자동 점수화에 필요한 정보만 강제한다
사람이 보기 좋게만 정리된 메모는 자동화에 도움이 되지 않는다.
반드시 실행과 점수화에 필요한 구조화 필드를 포함해야 한다.

### Principle D. 실험 분류 태그를 풍부하게 둔다
단순/복잡, headline-heavy, fine print, textured background 같은 태그가 있어야 regression 분석이 가능하다.

### Principle E. 사람이 만든 정답과 모델 생성 정답을 분리한다
reference text와 model suggestion은 구분해야 한다.
reference는 평가 기준이고, suggestion은 실험 보조 데이터다.

---

## 3. 저장 구조 권장안

```text
harness/
  datasets/
    poster_benchmark/
      manifest.json
      schema.json
      images/
        poster_001.png
        poster_002.jpg
      masks/
        poster_001_region_01.png
      overlays/
        poster_001_regions.png
      references/
        poster_001.ko_to_vi.json
        poster_001.ko_to_en.json
      splits/
        smoke.txt
        regression.txt
        critical.txt
        release.txt
```

설명:

- `manifest.json`: 전체 샘플 목록과 공통 메타데이터
- `schema.json`: 매니페스트 유효성 검사용 스키마
- `images/`: 입력 이미지 원본
- `masks/`: region 단위 편집 마스크 또는 검증용 마스크
- `overlays/`: 사람이 검토하기 쉬운 시각화 자료
- `references/`: locale pair별 기대 문구 및 제약
- `splits/`: smoke/regression/release 등 실행 세트 정의

---

## 4. 데이터셋 계층 구조

### 4.1 Dataset Level
데이터셋 전반의 메타정보를 포함한다.

필수 항목:
- dataset_id
- dataset_version
- owner
- created_at
- updated_at
- default_source_locale
- supported_target_locales
- license_or_usage_note

권장 항목:
- description
- dataset_policy
- human_review_status
- last_calibrated_score_version

### 4.2 Sample Level
이미지 하나에 대한 메타정보를 포함한다.

필수 항목:
- sample_id
- image_path
- source_locale
- target_locales
- categories
- difficulty
- regions
- evaluation_profile

권장 항목:
- aspect_ratio
- width
- height
- source_domain
- business_goal
- customer_visibility
- notes

### 4.3 Region Level
텍스트 블록 또는 편집 단위를 나타낸다.

필수 항목:
- region_id
- role
- polygon or bbox
- source_text
- target_constraints
- evaluation_weight

권장 항목:
- reading_order
- source_ocr_confidence
- importance
- style_hints
- mask_path
- forbidden_outcomes

---

## 5. 샘플 카테고리 체계
자동 분석과 회귀 탐지를 위해 아래 태그 체계를 권장한다.

### 5.1 레이아웃 태그
- `single_headline`
- `headline_subcopy`
- `dense_multiblock`
- `fineprint_heavy`
- `cta_prominent`
- `table_like_text`

### 5.2 시각 난이도 태그
- `flat_background`
- `textured_background`
- `gradient_background`
- `photo_background`
- `low_contrast_text`
- `stroke_shadow_text`
- `curved_text`
- `rotated_text`
- `small_text`

### 5.3 비즈니스 태그
- `promotion`
- `product_ad`
- `event_banner`
- `retail_leaflet`
- `medical_marketing`
- `social_creative`

### 5.4 리스크 태그
- `brand_sensitive`
- `legal_disclaimer_present`
- `currency_present`
- `date_time_present`
- `contact_info_present`
- `qr_or_barcode_near_text`

---

## 6. 평가 프로파일 설계
모든 샘플이 같은 가중치로 평가되면 안 된다.
예를 들어 headline 위주의 샘플은 레이아웃과 copy naturalness가 중요하고,
fine print 샘플은 OCR 재인식과 clipping이 더 중요하다.

따라서 샘플마다 `evaluation_profile` 을 둔다.

예시 프로파일:

- `headline_focus`
- `fineprint_focus`
- `design_preservation_focus`
- `copy_naturalness_focus`
- `release_gate_strict`

프로파일별 가중치 예시:

```json
{
  "headline_focus": {
    "target_text_match": 0.20,
    "layout_fitness": 0.25,
    "style_similarity": 0.20,
    "background_cleanliness": 0.15,
    "copy_acceptability": 0.20
  },
  "fineprint_focus": {
    "target_text_match": 0.35,
    "layout_fitness": 0.25,
    "style_similarity": 0.10,
    "background_cleanliness": 0.15,
    "copy_acceptability": 0.15
  }
}
```

---

## 7. 필수 필드 명세
아래는 권장 JSON 구조다.

```json
{
  "dataset_id": "poster_benchmark",
  "dataset_version": "2026.04.10",
  "owner": "rykim",
  "default_source_locale": "ko-KR",
  "supported_target_locales": ["en-US", "vi-VN", "ja-JP"],
  "samples": [
    {
      "sample_id": "poster_001",
      "image_path": "images/poster_001.png",
      "source_locale": "ko-KR",
      "target_locales": ["vi-VN", "en-US"],
      "categories": ["headline_subcopy", "photo_background", "cta_prominent"],
      "difficulty": "medium",
      "evaluation_profile": "release_gate_strict",
      "regions": [
        {
          "region_id": "r01",
          "role": "headline",
          "polygon": [[120, 80], [980, 80], [980, 260], [120, 260]],
          "source_text": "단 3일, 역대급 할인",
          "target_constraints": {
            "max_lines": 2,
            "max_chars_preferred": 22,
            "allow_rewrite": true,
            "must_include": [],
            "forbidden_terms": []
          },
          "evaluation_weight": 1.5,
          "importance": "high",
          "style_hints": {
            "alignment": "center",
            "preserve_emphasis": true,
            "preserve_case_pattern": false
          }
        },
        {
          "region_id": "r02",
          "role": "cta",
          "bbox": [410, 520, 290, 84],
          "source_text": "지금 구매하기",
          "target_constraints": {
            "max_lines": 1,
            "max_chars_preferred": 14,
            "allow_rewrite": true,
            "must_include": [],
            "forbidden_terms": ["클릭"]
          },
          "evaluation_weight": 1.3,
          "importance": "high"
        }
      ],
      "reference_targets": {
        "vi-VN": {
          "acceptable_variants": {
            "r01": [
              "Ưu đãi lớn chỉ trong 3 ngày",
              "Giảm giá cực sốc chỉ 3 ngày"
            ],
            "r02": [
              "Mua ngay",
              "Đặt mua ngay"
            ]
          }
        }
      }
    }
  ]
}
```

---

## 8. 필드별 의미와 운영 규칙

### `sample_id`
- 데이터셋 내에서 유일해야 한다.
- 파일명과 동일할 필요는 없지만, 동일하게 맞추는 것이 운영상 편하다.

### `source_locale`
- OCR 결과 원문의 기준 언어다.
- 실제 이미지가 다국어 혼합인 경우 주 언어를 적고, region 별 override를 허용한다.

### `target_locales`
- 이 샘플이 공식 벤치마크 대상으로 삼는 타겟 언어 목록이다.
- 병렬 Agent 비교 시 locale pair가 반드시 같아야 한다.

### `role`
권장 role 목록:
- `headline`
- `subheadline`
- `body`
- `cta`
- `price`
- `disclaimer`
- `tagline`
- `label`

role을 넣는 이유:
- 카피 rewriting 정책이 달라진다.
- 줄 수 제한과 길이 제한이 달라진다.
- 평가 가중치도 달라진다.

### `target_constraints`
자동 현지화에서 가장 중요한 필드 중 하나다.
최소한 아래를 권장한다.

- `max_lines`
- `max_chars_preferred`
- `allow_rewrite`
- `must_include`
- `forbidden_terms`
- `tone`
- `brevity_priority`
- `brand_term_policy`

### `evaluation_weight`
값이 높을수록 해당 region 실패가 전체 점수에 더 크게 반영된다.
권장 범위는 `0.5 ~ 2.0` 이다.

### `style_hints`
초기에는 완전 자동 추정이 어려우므로 사람이 간단히 넣어줄 수 있다.
예시:
- center aligned
- uppercase feel
- tight tracking
- strong emphasis
- high contrast

---

## 9. 스플릿 설계
하네스 자동화에서는 벤치마크 전체를 매번 돌리면 느리다.
따라서 목적에 따라 split을 나눈다.

### 9.1 Smoke Split
목적:
- 코드 크래시, I/O 실패, 필수 산출물 누락 확인

권장 크기:
- 5 ~ 20 샘플

포함 조건:
- 서로 다른 레이아웃 유형을 최소 1개씩 포함

### 9.2 Regression Split
목적:
- 최근 자주 깨졌던 케이스 재검증

권장 크기:
- 20 ~ 100 샘플

포함 조건:
- 과거 severe failure 케이스 우선

### 9.3 Critical Split
목적:
- 데모/고객 영향도가 큰 샘플군 보호

권장 크기:
- 10 ~ 30 샘플

포함 조건:
- 대표 고객 시나리오
- 브랜드 민감 샘플
- fine print / price / CTA 중요 샘플

### 9.4 Release Split
목적:
- 릴리스 직전 최종 승격 판단

권장 크기:
- 전체 공식 벤치마크

---

## 10. 기대값 작성 기준
현지화는 단순 번역이 아니라서 exact match만으로 평가하면 오판이 많다.
그래서 아래 3계층 구조를 권장한다.

### Tier 1. Strict Reference
정확히 맞아야 하는 항목
예:
- 숫자
- 가격
- 날짜
- 브랜드명
- 연락처
- 법적 고지 핵심 표현

### Tier 2. Acceptable Variant
여러 표현이 가능하지만 의미상 허용되는 항목
예:
- CTA
- headline marketing copy
- subcopy 일부 표현

### Tier 3. Soft Guidance
정답으로 강제하지는 않지만 품질 판단에 참고하는 항목
예:
- 더 짧은 표현 선호
- 구어체보다는 광고문구 선호
- locale cultural fit

---

## 11. 자동 점수화 연결 포인트
매니페스트는 다음 scoring 모듈과 연결되도록 설계해야 한다.

### OCR Score
활용 필드:
- `source_text`
- `acceptable_variants`
- `must_include`
- `forbidden_terms`

### Layout Score
활용 필드:
- `polygon` 또는 `bbox`
- `max_lines`
- `max_chars_preferred`
- `role`

### Style Score
활용 필드:
- `style_hints`
- `importance`
- `preserve_emphasis`

### Copy Score
활용 필드:
- `allow_rewrite`
- `tone`
- `acceptable_variants`
- `forbidden_terms`

---

## 12. 운영용 권장 상태 필드
데이터셋도 제품처럼 상태 관리가 필요하다.
샘플 수준에서 아래 상태값을 둘 수 있다.

- `draft`
- `reviewed`
- `golden`
- `deprecated`
- `quarantined`

의미:
- `draft`: 막 추가되어 아직 공식 비교 대상 아님
- `reviewed`: 사람이 검토했으나 아직 골든 샘플은 아님
- `golden`: release gate에 들어가는 핵심 샘플
- `deprecated`: 더 이상 유지하지 않음
- `quarantined`: 데이터 이상 또는 기준 재검토 필요

---

## 13. 권장 검수 프로세스

### Step 1. 샘플 수집
- 실제 포스터/배너를 수집한다.
- 라이선스/사용 허용 여부를 확인한다.

### Step 2. Region 주석화
- headline, body, CTA, disclaimer를 나눈다.
- bbox 또는 polygon을 저장한다.

### Step 3. 타겟 기대값 작성
- strict reference와 acceptable variant를 분리해 작성한다.

### Step 4. 난이도/카테고리 태깅
- regression 분석 가능한 수준으로 태그를 붙인다.

### Step 5. 샘플 승격
- reviewed -> golden 여부 판단

---

## 14. JSON Schema 최소 요구 예시
아래는 완전한 스키마는 아니지만 최소 수준의 검증 골격이다.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["dataset_id", "dataset_version", "samples"],
  "properties": {
    "dataset_id": { "type": "string" },
    "dataset_version": { "type": "string" },
    "samples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "sample_id",
          "image_path",
          "source_locale",
          "categories",
          "difficulty",
          "evaluation_profile",
          "regions"
        ]
      }
    }
  }
}
```

---

## 15. 실제 운영에서 자주 생기는 실패와 방지책

### 실패 1. acceptable variant가 너무 많아 점수 기준이 느슨해짐
대응:
- role별 허용 범위를 다르게 둔다.
- headline만 다변형 허용, legal/disclaimer는 strict 유지

### 실패 2. bbox만 있고 polygon이 없어 mask 품질 검증이 부정확함
대응:
- 최소한 critical set은 polygon까지 관리

### 실패 3. 샘플 태그가 빈약해 regression 원인 분석 불가
대응:
- 시각 난이도 태그를 강제 필드로 둔다.

### 실패 4. 사람이 reference를 너무 길게 써서 레이아웃에 절대 안 들어감
대응:
- `max_chars_preferred`, `max_lines` 검증으로 작성 단계부터 차단

### 실패 5. locale pair별 reference가 불균형
대응:
- 공식 release gate 대상 locale만 먼저 골든화
- 나머지는 draft 상태 유지

---

## 16. 추천 초기 운영안
현재 프로젝트 기준으로는 아래처럼 시작하는 것이 현실적이다.

### 초기 수량
- smoke: 10장
- regression: 30장
- critical: 15장
- release: 60장 내외

### 우선 locale
- `ko-KR -> en-US`
- `ko-KR -> vi-VN`

### 우선 role
- headline
- subcopy
- cta
- disclaimer

### 우선 평가 항목
- target text match
- overflow/clipping
- background artifact
- basic style similarity

---

## 17. 바로 붙여넣어 쓸 수 있는 샘플 템플릿

```json
{
  "sample_id": "poster_template_001",
  "image_path": "images/poster_template_001.png",
  "source_locale": "ko-KR",
  "target_locales": ["en-US", "vi-VN"],
  "categories": ["headline_subcopy", "photo_background", "cta_prominent"],
  "difficulty": "medium",
  "status": "reviewed",
  "evaluation_profile": "headline_focus",
  "business_goal": "promo_conversion",
  "regions": [
    {
      "region_id": "r01",
      "role": "headline",
      "bbox": [100, 120, 860, 180],
      "source_text": "봄맞이 특별 할인",
      "target_constraints": {
        "max_lines": 2,
        "max_chars_preferred": 18,
        "allow_rewrite": true,
        "must_include": [],
        "forbidden_terms": [],
        "tone": "promotional",
        "brevity_priority": "high"
      },
      "evaluation_weight": 1.5,
      "importance": "high",
      "style_hints": {
        "alignment": "center",
        "preserve_emphasis": true
      }
    }
  ],
  "reference_targets": {
    "en-US": {
      "acceptable_variants": {
        "r01": ["Spring Special Sale", "Special Spring Savings"]
      }
    },
    "vi-VN": {
      "acceptable_variants": {
        "r01": ["Ưu đãi đặc biệt mùa xuân", "Khuyến mãi đặc biệt mùa xuân"]
      }
    }
  }
}
```

---

## 18. 결론
이 매니페스트는 단순 데이터 파일이 아니라,
**실험 자동화, 병렬 Agent 비교, 회귀 탐지, 릴리스 게이트 판정의 출발점**이다.

벤치마크 품질이 낮으면 하네스 전체가 흔들린다.
따라서 구현보다 먼저,
- 샘플 구조
- 기대값 정책
- split 전략
- 태그 체계
를 고정하는 것이 중요하다.

다음 단계에서는 이 매니페스트를 기준으로,
1. Agent 입출력 계약 템플릿
2. run_result / score_result schema
3. merge gate 체크리스트
를 연결해야 전체 자동화가 닫힌다.
