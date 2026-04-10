# STE Experiment Design

## Goal
현재 MVP 파이프라인은 `OCR -> localization -> inpaint -> render -> validate` 구조다. 이 방식은 빠르게 동작하지만, 광고 포스터 수준에서는 아래 한계가 반복된다.

- 원문 잔상 제거가 완전하지 않다.
- 원본 타이포 질감과 미세 정렬이 무너진다.
- 작은 카피와 복잡 배경에서 렌더링 티가 난다.
- OCR 오류가 후단 전체 품질을 끌고 내려간다.

따라서 기존 파이프라인은 유지하되, 그 위에 `STE(Scene Text Editing) 실험 경로`를 추가한다.

## Principles
1. 기존 파이프라인은 깨지지 않아야 한다.
2. 특정 포스터/문구 하드코딩 없이 일반화 가능한 구조만 추가한다.
3. STE 실험은 현재 파이프라인과 같은 입력/영역/목표 문구를 공유해야 한다.
4. 비교 가능성을 위해 crop, mask, target text, style estimate를 모두 기록한다.

## Current Baseline
현재 baseline은 다음 순서를 유지한다.

1. detect
2. recognize
3. rewrite
4. restore
5. render
6. validate

이 baseline은 계속 품질 기준선으로 남긴다.

## Added STE Track
이번 단계에서 추가하는 것은 `STE dataset export`다.

### Export Inputs
각 편집 가능 영역마다 아래 아티팩트를 만든다.

- 원본 crop
- 복원(restored) crop
- 영역 mask crop
- source text
- target text
- candidate texts
- role classification
- bbox / polygon
- style estimate

### Export Outputs
이미지 1장당 아래 구조를 생성한다.

```text
outputs/<job_name>/ste_dataset/
  ├─ source_image.jpg
  ├─ restored_image.jpg
  ├─ full_mask.png
  ├─ ste_manifest.json
  ├─ README.md
  └─ regions/
     ├─ region_01_source.png
     ├─ region_01_restored.png
     ├─ region_01_mask.png
     └─ ...
```

### Manifest Schema
`ste_manifest.json`은 다음 정보를 담는다.

- 입력 이미지 경로
- 복원 이미지 경로
- 전체 이미지 아티팩트 경로
- 영역별 인덱스
- 영역 id
- role
- source text
- target text
- candidate texts
- region bbox
- crop bbox
- polygon
- OCR confidence
- style profile
- 각 crop/mask 파일 경로

## Why This Step First
바로 AnyText2나 diffusion 기반 STE를 붙이기 전에, 공통 입력 포맷을 먼저 고정해야 한다. 그래야 아래 비교가 가능해진다.

- 현재 renderer baseline vs STE backbone
- role별 품질 차이
- mask 품질이 편집 결과에 주는 영향
- OCR/rewriter 단계가 후단 편집 품질에 주는 영향

## Immediate Follow-up
다음 단계는 이 export를 기반으로 한다.

1. crop/mask/target text를 읽는 `STE adapter` 추가
2. 외부 STE 모델 결과를 동일 job 폴더에 저장
3. OCR 재인식 + 시각 잔상 점수로 baseline과 비교
4. headline/caption/fineprint 별로 어떤 방식이 더 유리한지 실험

## Scope of This Change
이번 변경은 아래까지만 구현한다.

- 엔진 준비 단계 분리
- STE dataset export 추가
- CLI 옵션 연결
- README/설계 문서 기록

직접적인 diffusion/AnyText2 연동은 아직 하지 않는다.
