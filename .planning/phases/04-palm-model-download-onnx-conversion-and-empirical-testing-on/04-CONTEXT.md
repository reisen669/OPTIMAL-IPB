# Phase 4: Palm model download, ONNX conversion, and empirical testing on OAM rasters - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Commit all untracked Phase 4 work, verify every ONNX model loads correctly, and run each model on its compatible OAM raster(s). Document quantitative detection counts and a visual pass/fail check per model in `04-TEST-RESULTS.md`. Phase 4 is done when at least one VHR model produces plausible palm detections on Perak or Rupat.

**In scope:**
- Commit `optimal_ipb_algorithm.py` edge-clamping fix + log message cleanup (task 1)
- Commit untracked files: `mopad_algorithm.py`, `roboflow_algorithm.py`, `verify_onnx_models.py`, `download_missing.py`
- Run `verify_onnx_models.py` on all ONNX models — including Geoeye/Pleiades whose provenance is uncertain
- Run VHR models (B1 tree_tops, H1 YOLOv11, MOPAD) on Perak (5 cm/px) and Rupat (8.8 cm/px)
- Run MR models (B2 Google, B3 Geoeye, B4 Pleiades) on Aceh (50 cm/px)
- Run Roboflow algorithm on Perak + Rupat (API key already set in QGIS global var `roboflow_api_key`)
- Document all results in `04-TEST-RESULTS.md` with detection counts, threshold, and visual pass/fail
- Visual inspection of best candidates in QGIS

**Out of scope:**
- Registering mopad_algorithm.py or roboflow_algorithm.py in optimal_ipb_provider.py (deferred)
- Downloading new candidates (detectree2 N1, deepforest N2) — Phase 4 uses what's already on disk
- Training or fine-tuning
- Performance optimization

</domain>

<decisions>
## Implementation Decisions

### Phase Scope
- **D-01:** Phase 4 = commit + verify + test what's already built. No new model downloads. The goal statement for ROADMAP should be updated to: "Commit and verify all existing palm detection models; run empirical tests on OAM rasters; document results in 04-TEST-RESULTS.md."
- **D-02:** Geoeye-Resnet101.onnx and Pleiades-Resnet101.onnx are present in `models/` but their provenance is uncertain (MODEL_CONVERSION_STATUS.md said conversion failed; source of current files unknown). Run `verify_onnx_models.py` first. If verification fails, exclude them from testing and note in results. Do not block Phase 4 on their status.
- **D-03:** MOPAD model (`models/mopad/MOPAD_epoch_24.onnx`, 242 MB) is downloaded and considered valid. Include as a first-class VHR candidate alongside B1 and H1.
- **D-04:** Light requirements (5 IDs): MOD-01 through MOD-05 (see below).

### Provider Integration
- **D-05:** `mopad_algorithm.py` and `roboflow_algorithm.py` stay as standalone scripts — NOT registered in `optimal_ipb_provider.py`. Phase 4 uses them directly for testing only. Provider integration is a future phase.
- **D-06:** `optimal_ipb_algorithm.py` edge-clamping + log message changes are committed as Phase 4 task 1 (first commit of the phase).
- **D-07:** All new files stay at their current locations (plugin root for `.py` scripts; `models/mopad/` for MOPAD ONNX). No reorganization.

### Empirical Testing Protocol
- **D-08:** Testing output = both quantitative (detection count + confidence distribution at default threshold) AND visual (load output layer in QGIS, confirm points/boxes fall on palm crowns or note failure).
- **D-09:** Test matrix follows Phase 3 GSD compatibility:
  - VHR (≤15 cm/px): B1 tree_tops + H1 YOLOv11 + MOPAD → Perak 5cm + Rupat 8.8cm
  - MR (50 cm/px): B2 Google + B3 Geoeye + B4 Pleiades → Aceh 50cm
  - API: Roboflow UiTM → Perak 5cm + Rupat 8.8cm
- **D-10:** Results live in `.planning/phases/04-palm-model-download-onnx-conversion-and-empirical-testing-on/04-TEST-RESULTS.md`. One table: model | raster | detection count | threshold | visual pass/fail | notes.
- **D-11:** Phase 4 success criterion: at least one VHR model (B1, H1, or MOPAD) produces visually plausible palm detections on Perak or Rupat.

### Roboflow Algorithm
- **D-12:** `roboflow_algorithm.py` is in scope for Phase 4 — commit and test. API key is already set in QGIS global variable `roboflow_api_key`. Test on Perak + Rupat; document results alongside ONNX models in `04-TEST-RESULTS.md`.

### Requirements (Light)
- **MOD-01:** All untracked Phase 4 files committed (`optimal_ipb_algorithm.py`, `mopad_algorithm.py`, `roboflow_algorithm.py`, `verify_onnx_models.py`, `download_missing.py`, model files in git-lfs or .gitignore as appropriate)
- **MOD-02:** All ONNX models verified with `verify_onnx_models.py` — pass/fail recorded; failures noted before proceeding to tests
- **MOD-03:** VHR models (B1, H1, MOPAD) run on Perak + Rupat; detection counts + visual check recorded in `04-TEST-RESULTS.md`
- **MOD-04:** MR models (B2/B3/B4 — if verified) run on Aceh; detection counts + visual check recorded
- **MOD-05:** Roboflow algorithm run on Perak + Rupat; results recorded; API key usage confirmed working

### Claude's Discretion
- Wave structure and ordering of commits within Phase 4
- Exact column layout and formatting of `04-TEST-RESULTS.md`
- Score threshold values used for each model (use defaults from each algorithm's code)
- Whether to use a Python script or QGIS Processing Toolbox runner for model testing (whichever is faster)
- git-lfs vs .gitignore strategy for large ONNX files (MOD-01 note: models/ files are typically excluded from git due to size; confirm approach)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 3 outputs — primary inputs for Phase 4
- `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md` — full model catalog, GSD compatibility matrix, recommended shortlist, and Key Integration Constraints section (detectree2/DeepForest caveats still apply if those are added later)
- `.planning/phases/02-palm-ensemble/02-04-SOURCES.md` — Phase 2 source probe baseline

### Plugin code to modify / commit
- `optimal_ipb_algorithm.py` — modified (edge clamping + log fix), uncommitted — commit as task 1
- `mopad_algorithm.py` — MOPAD Faster R-CNN 1024×1024 tile inference, untracked
- `roboflow_algorithm.py` — UiTM Roboflow API algorithm, untracked
- `verify_onnx_models.py` — model verification script, untracked
- `download_missing.py` — imagery download helper, untracked
- `optimal_ipb_provider.py` — NOT modified in Phase 4; mopad/roboflow algorithms not registered here

### Model status
- `models/MODEL_CONVERSION_STATUS.md` — conversion history; notes Geoeye/Pleiades as uncertain

### Test imagery (OAM rasters)
- `tif_online_samples/oam_perak_01E2b_0.05mpx.tif` — 5 cm/px, Perak Malaysia (VHR test raster)
- `tif_online_samples/oam_rupat_indonesia_0.088mpx.tif` — 8.8 cm/px, Rupat Riau Indonesia (VHR test raster)
- `tif_online_samples/oam_leuhan_aceh_0.5mpx.tif` — 50 cm/px, Aceh Barat Indonesia (MR test raster)

### Planning context
- `.planning/codebase/ARCHITECTURE.md` — plugin layer architecture and inference path
- `.planning/ROADMAP.md` — Phase 4 entry (goal needs updating to match decisions above)

</canonical_refs>

<code_context>
## Existing Code Insights

### Model Files on Disk (untracked — need git strategy)
- `models/tree_tops_yolov9.onnx` (203 MB) — B1 baseline, Deepness-compatible, already tested in Phase 2
- `models/tribber93_yolov11_palm.onnx` (37.9 MB) — H1, downloaded + converted from HuggingFace
- `models/mopad/MOPAD_epoch_24.onnx` (242 MB) — MOPAD Faster R-CNN, Baidu Wangpan download
- `models/mopad/MOPAD_epoch_24.pth` (484 MB) — MOPAD PyTorch weights (source for ONNX conversion)
- `models/Google-Resnet101.onnx` (211 MB) — B2, verified working (opset 13)
- `models/Geoeye-Resnet101.onnx` (221 MB) — B3, uncertain provenance — verify first
- `models/Pleiades-Resnet101.onnx` (221 MB) — B4, uncertain provenance — verify first

### Algorithm Structure
- `mopad_algorithm.py` uses `_TILE_SIZE = 1024`, `_STEP = 900` (124 px overlap). Model at `models/mopad/MOPAD_epoch_24.onnx`. Class names: Dead/Healthy/Grass/Small/Yellow (class 2 Grass excluded from palm output by default).
- `roboflow_algorithm.py` reads API key from QGIS global var `roboflow_api_key`; calls `oil-palm-aerial-detection/1` model; resolution-aware (tiles resampled to 10 cm/px before sending).
- `verify_onnx_models.py` iterates `models/*.onnx` (not `models/mopad/*.onnx` — planner should confirm MOPAD is covered or add a path for it).

### Integration Points
- `optimal_ipb_algorithm.py:detect_palm()` — modified with edge clamping; scores accumulation also fixed (only keeps `kept_scores` instead of full scores array)
- All three algorithms (optimal_ipb, mopad, roboflow) use `helpers.py:pixel2coord()` and `helpers.py:map_uint16_to_uint8()`
- QGIS global variable `roboflow_api_key` must be set before Roboflow tests run

</code_context>

<specifics>
## Specific Ideas

### Test matrix (explicit)
| Model | Type | Raster(s) | Expected |
|-------|------|-----------|----------|
| B1 tree_tops_yolov9.onnx | ONNX/Deepness | Perak 5cm, Rupat 8.8cm | Baseline — should detect tree crowns |
| H1 tribber93_yolov11_palm.onnx | ONNX/YOLOv11 | Perak 5cm, Rupat 8.8cm | Palm-specific — expect higher precision |
| MOPAD (mopad_algorithm.py) | ONNX/Faster-RCNN | Perak 5cm, Rupat 8.8cm | 5-class palm health output |
| B2 Google-Resnet101.onnx | ONNX/RetinaNet | Aceh 50cm | Baseline MR |
| B3 Geoeye-Resnet101.onnx | ONNX/RetinaNet | Aceh 50cm | Only if verify passes |
| B4 Pleiades-Resnet101.onnx | ONNX/RetinaNet | Aceh 50cm | Only if verify passes |
| Roboflow UiTM | API (oil-palm-aerial-detection/1) | Perak 5cm, Rupat 8.8cm | API key in QGIS global var |

### verify_onnx_models.py note
Current script only scans `models/*.onnx` — MOPAD lives at `models/mopad/MOPAD_epoch_24.onnx`. Planner should check if MOPAD path needs to be added (either modify the script or run it manually with the mopad path).

### ROADMAP goal update
Phase 4 goal in ROADMAP.md should be updated to:
> "Commit and verify all existing palm detection models (ONNX + Roboflow API); run empirical tests on OAM rasters; document quantitative + visual results in 04-TEST-RESULTS.md."

</specifics>

<deferred>
## Deferred Ideas

- **Provider integration for MOPAD + Roboflow** — registering mopad_algorithm.py and roboflow_algorithm.py in optimal_ipb_provider.py so they appear in QGIS Processing Toolbox. This is the natural next phase after Phase 4 confirms results.
- **detectree2 (N1)** — Sabah Malaysia-trained Detectron2 model, strongest geographic domain match. Deferred because it requires a separate inference path (not onnxruntime) and Detectron2 installation. Phase 4 focuses on what's already on disk.
- **deepforest (N2)** — weecology/deepforest-tree, requires `pip install deepforest`. US NEON training data — significant domain gap. Skip unless VHR candidates all fail.
- **MADAN (N4)** — cross-regional domain adaptation, Google Drive/Baidu Wangpan access unconfirmed. Skip.
- **Confidence threshold tuning** — Phase 4 uses defaults. If testing shows useful detections at non-default thresholds, add a follow-up phase for calibration.
- **Git-LFS for large ONNX files** — model files range from 37 MB to 242 MB. If committing them to git creates problems, set up git-lfs or add to .gitignore with a companion download script. Planner decides.

</deferred>

---

*Phase: 04-palm-model-download-onnx-conversion-and-empirical-testing-on*
*Context gathered: 2026-06-18*
