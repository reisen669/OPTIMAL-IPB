# Phase 6 Research — Phase 5 Shortlist Model Acquisition, ONNX Conversion, and Empirical Testing

**Generated:** 2026-06-19
**Phase:** 06-phase-5-shortlist-model-acquisition-onnx-conversion-and-emp
**Purpose:** Research implementation approach for acquiring, converting, and testing E1 CanopyRS and E2 VHRTrees models from Phase 5 shortlist.

---

## Executive Summary

Phase 6 focuses on two conditional candidates from the Phase 5 extended research:
1. **E2 VHRTrees (RSandAI)** — YOLOv8m, 50 cm/px, Turkey generic trees
2. **E1 CanopyRS (hugobaudchon)** — DINO+Swin-L / Faster R-CNN+R50, 3-10 cm/px, tropical rainforest

Both candidates have known blockers (E2: domain gap; E1: unconfirmed weight URL, unknown Python 3.12 compatibility). This phase validates whether these blockers can be overcome and documents empirical results.

---

## Candidate Analysis

### E2 VHRTrees (RSandAI)

**Repository:** https://github.com/RSandAI/VHRTrees
**Architecture:** YOLOv8m (Ultralytics)
**GSD:** 50 cm/px (confirmed from Frontiers paper)
**License:** Unspecified (academic open)

**Download Path:**
- Google Drive: https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view
- File: YOLOv8m .pt weights
- Accessibility: CONFIRMED — direct Google Drive link

**ONNX Export Path:**
```bash
# Standard Ultralytics export
from ultralytics import YOLO
model = YOLO("VHRTrees_yolov8m.pt")
model.export(format="onnx", opset=13)
```

**Python 3.12 Compatibility:**
- ✓ Ultralytics is pip-installable on Python 3.12
- ✓ No special C++ extensions required
- ✓ ONNX export uses standard PyTorch/torch.onnx path

**Test Targets:**
- `sample_data_qgis/canvas_0.5mpx.tif` (0.5 m/px = 50 cm/px — exact match)
- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_1.0mpx.tif` (Aceh 50cm candidate)

**Domain Gap Assessment:**
- Training data: Turkey satellite imagery, generic deciduous trees
- Target domain: SE Asia oil palm plantations
- Gap severity: HIGH — likely false positives on non-palm vegetation
- Expected outcome: Low palm-specific precision; may detect generic tree crowns
- Usefulness: Baseline for 50 cm/px tier; validates whether generic tree detection transfers

**Technical Risks:**
- Domain mismatch → poor palm detection
- No palm-specific training → precision expected <50%
- Useful as negative control / baseline for comparison

---

### E1 SelvaBox/CanopyRS (hugobaudchon)

**Repository:** https://github.com/hugobaudchon/CanopyRS
**Paper:** arXiv:2507.00170 (XPRIZE Rainforest)
**Architecture:** Multiple presets:
  - DINO + Swin-L 384 (primary)
  - Faster R-CNN + ResNet-50 (alternative)
  - DINO + ResNet-50 (alternative)

**GSD:** 3–10 cm/px (covers Perak 5cm, Rupat 8.8cm)
**License:** Apache-2.0

**Download Path:**
- GitHub Releases: https://github.com/hugobaudchon/CanopyRS/releases
- Accessibility: UNCONFIRMED — WebFetch failed; requires manual browser verification
- Paper states: "Our dataset, code, and pre-trained weights are made public"

**ONNX Export Path:**

**Option A: Faster R-CNN + R50 (preferred for export)**
```bash
# Standard torchvision export
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
model = fasterrcnn_resnet50_fpn(pretrained=False)
# Load CanopyRS checkpoint
checkpoint = torch.load("canopyrs_frcnn_r50.pth")
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 3, 1024, 1024)
torch.onnx.export(model, dummy_input, "canopyrs_frcnn_r50.onnx",
                  opset_version=13,
                  input_names=['images'],
                  output_names=['boxes', 'scores', 'labels'])
```

**Option B: DINO + Swin-L 384 (complex)**
- Requires transformers library
- Swin-L needs custom ONNX export logic
- May require specific torch version
- Higher complexity → lower Phase 6 priority

**Python 3.12 Compatibility:**
- Faster R-CNN + R50: ✓ Standard torchvision, compatible
- DINO + Swin-L: UNKNOWN — depends on transformers version, custom ops
- canopyrs package: UNKNOWN — dependency list needs verification

**Test Targets:**
- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.05mpx.tif` (Perak 5cm — not yet downloaded, need to verify)
- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.088mpx.tif` (Rupat 8.8cm — need to verify)

**Domain Gap Assessment:**
- Training data: Tropical rainforest (3 countries, XPRIZE Rainforest context)
- Target domain: SE Asia oil palm plantations
- Gap severity: MEDIUM — tropical trees similar to palm crowns; lacks plantation row geometry
- Expected outcome: Better than E2 for palm detection; moderate precision possible
- Usefulness: Best available VHR candidate for 3-10 cm/px tier

**Technical Risks:**
- Weight URL inaccessible → phase blocked for E1
- canopyrs package has incompatible dependencies → fallback to manual inference script
- DINO+Swin-L export fails → use Faster R-CNN+R50 preset instead
- No existing OAM rasters at 5cm/8.8cm → need to source or use closest available

---

## Implementation Strategy

### Wave 1: E2 VHRTrees (Lower Risk)

**Plan 06-01:**
1. Download YOLOv8m .pt from Google Drive
2. Install ultralytics in qgis_gdal_env (if not present)
3. Export to ONNX via `yolo export format=onnx`
4. Test inference on canvas_0.5mpx.tif
5. Test inference on Aceh 50cm raster
6. Document detection results (bbox count, confidence distribution, visual inspection)
7. Assess domain gap impact (false positives on non-palm features)

**Success Criteria:**
- ONNX file created and runs without error
- Inference produces bbox output on both test rasters
- Domain gap documented (precision estimate or qualitative assessment)

### Wave 1: E1 CanopyRS URL Verification (Parallel)

**Plan 06-02:**
1. Manual browser check: visit GitHub Releases page
2. If weights accessible: download Faster R-CNN+R50 checkpoint
3. Install canopyrs package (or verify dependencies)
4. Test Python 3.12 compatibility (import test)
5. If import fails: document blocker, skip E1 empirical testing
6. If import succeeds: proceed to Wave 2

**Success Criteria:**
- Weight accessibility confirmed (or blocker documented)
- Python 3.12 compatibility verified (or blocker documented)

### Wave 2: E1 CanopyRS ONNX Export (Conditional)

**Plan 06-03 (gate: 06-02 success):**
1. Attempt Faster R-CNN+R50 ONNX export
2. If export succeeds: test on Perak/Rupat rasters
3. If export fails: document export blocker, try DINO+Swin-L preset
4. Document detection results (bbox count, confidence, visual inspection)
5. Compare domain gap vs E2 (tropical rainforest vs Turkey generic trees)

**Success Criteria:**
- ONNX file created (or export blocker documented)
- Inference produces bbox output (if export succeeds)
- Domain gap comparison documented

### Wave 3: Results Finalization

**Plan 06-04:**
1. Write 06-TEST-RESULTS.md
2. Document E2 results: detection counts, confidence distribution, false positive assessment
3. Document E1 results: weight accessibility status, export success/failure, inference results (if applicable)
4. Domain gap assessment: compare E2 (Turkey generic) vs E1 (tropical rainforest) for SE Asia palm
5. Update ROADMAP.md with Phase 6 completion status
6. Recommend Phase 7 actions (if E1/E2 show promise or if new blockers found)

---

## Technical Dependencies

### Required Packages (E2 VHRTrees)
- `ultralytics` — YOLOv8 inference and ONNX export
- `onnxruntime` — already installed in qgis_gdal_env
- `opencv-python` — image preprocessing (already in qgis_gdal_env)
- `torch` — backend for YOLOv8 (need to verify version compatibility)

### Required Packages (E1 CanopyRS)
- `canopyrs` — official package (or manual inference script)
- `torchvision` — Faster R-CNN + R50 backbone
- `transformers` — if using DINO + Swin-L preset
- `torch` — backend (version depends on canopyrs requirements)

### Environment Validation
```bash
# Check qgis_gdal_env packages
conda activate qgis_gdal_env
pip list | grep -E "ultralytics|torch|torchvision|transformers"
```

---

## Validation Architecture

### Dimension 1: Functional Correctness
- E2 ONNX file loads without error
- E1 weight download succeeds (or blocker documented)
- Inference produces bbox output with expected schema

### Dimension 2: Input/Output Contracts
- Input: GeoTIFF raster (single-band or RGB)
- Output: bbox array with format [x_min, y_min, x_max, y_max, confidence, class]
- CRS: Input raster CRS preserved in output

### Dimension 3: Error Handling
- Missing weight file: clear error message
- Incompatible raster format: graceful failure with log message
- ONNX export failure: fallback to alternative architecture preset

### Dimension 4: Performance
- Inference time: <30 seconds for 1024x1024 tile
- Memory usage: <4GB GPU VRAM (if available) or <8GB system RAM

### Dimension 5: Integration
- ONNX file compatible with optimal_ipb_algorithm.py inference path
- No modifications to existing plugin architecture required

### Dimension 6: Documentation
- 06-TEST-RESULTS.md includes:
  - Model download URLs and accessibility status
  - ONNX export commands and outputs
  - Detection results per test raster
  - Domain gap assessment (qualitative or quantitative)
  - Recommendation for Phase 7

### Dimension 7: Reproducibility
- All download URLs documented
- ONNX export commands documented
- Python environment requirements documented
- Random seed fixed for reproducible inference (if applicable)

### Dimension 8: Goal Achievement
- VHR-01: E2 ONNX created → measurable (file exists, loads in onnxruntime)
- VHR-02: E1 URL verified → measurable (manual browser check documented)
- VHR-03: E1 Python 3.12 compatibility tested → measurable (import test documented)
- VHR-04: E1 ONNX export attempted → measurable (export log documented)
- VHR-05: E2 tested on Canvas/Aceh → measurable (inference results documented)
- VHR-06: E1 tested on Perak/Rupat → measurable (inference results documented, conditional)
- VHR-07: 06-TEST-RESULTS.md produced → measurable (file exists with required sections)

---

## Known Blockers and Mitigations

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| E1 weight URL unconfirmed | HIGH | Manual browser verification in 06-02; if inaccessible, document blocker and proceed with E2-only results |
| E1 canopyrs package incompatible with Python 3.12 | MEDIUM | Try manual inference script without canopyrs dependency; if fails, document blocker |
| E1 DINO+Swin-L ONNX export fails | MEDIUM | Use Faster R-CNN+R50 preset instead; if both fail, document export blocker |
| No Perak/Rupat 5cm/8.8cm rasters in sample_data_qgis | MEDIUM | Use closest available GSD rasters; document resolution mismatch |
| E2 domain gap produces poor palm detection | EXPECTED | Document as baseline result; validate whether generic tree detection is useful |
| Google Drive download fails (rate limit, link rot) | LOW | Try alternative download methods; if fails, document blocker |

---

## Success Criteria Summary

**Minimum Viable Success:**
- E2 VHRTrees ONNX created and tested on Canvas/Aceh
- 06-TEST-RESULTS.md documents E2 results and domain gap assessment
- E1 weight accessibility status confirmed (even if inaccessible)

**Full Success:**
- E2 VHRTrees tested on Canvas/Aceh with documented results
- E1 CanopyRS weight downloaded and tested for Python 3.12 compatibility
- E1 CanopyRS ONNX export attempted (success or failure documented)
- If E1 ONNX succeeds: tested on Perak/Rupat rasters
- Domain gap comparison between E2 and E1 documented
- 06-TEST-RESULTS.md includes all above plus Phase 7 recommendations

---

## Recommendations for Planning

1. **Prioritize E2 VHRTrees first** — lower technical risk, confirmed download path
2. **Parallelize E1 URL verification** — manual browser check can happen while E2 download completes
3. **Gate E1 empirical testing on successful URL verification** — don't commit to E1 testing if weights inaccessible
4. **Use Faster R-CNN+R50 preset for E1 ONNX export** — simpler than DINO+Swin-L, higher success probability
5. **Document blockers clearly** — Phase 6 is exploratory; negative results are valuable
6. **Compare domain gaps systematically** — E2 (Turkey generic) vs E1 (tropical rainforest) assessment informs Phase 7 model selection

---

**Research Complete — Ready for Planning**
