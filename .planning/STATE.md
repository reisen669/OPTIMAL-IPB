---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: phase_complete
last_updated: "2026-06-24T00:00:00.000Z"
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 25
  completed_plans: 16
  percent: 64
---

# Project State — optimal-ipb

## Status

Phase 1 COMPLETE — All 3 plans done. Plugin fully migrated to onnxruntime on Python 3.12.
Phase 3 COMPLETE — 03-01-PLAN.md executed. 03-CANDIDATE-REPORT.md produced (10 candidates, Phase 4 shortlist).
Phase 5 COMPLETE — All 5 plans done. 05-EXTENDED-REPORT.md produced (E1 CanopyRS, E2 VHRTrees shortlist).
Phase 6 COMPLETE — 4 plans. 06-TEST-RESULTS.md produced: E2 pipeline validated (COCO base, VERY HIGH gap), E1 definitively blocked (no weights, SAM 3, Linux/Py3.10/CUDA). Phase 7 recommendation: QGIS Toolbox integration of VHRTrees ONNX.

## Current Phase

Phase 6: Phase 5 shortlist model acquisition, ONNX conversion, and empirical testing — COMPLETE

## Current Plan

None — Phase 6 complete. Next: Phase 7 (QGIS Processing Toolbox integration)

## Completed Work (pre-planning session)

- __init__.py: qgis_gdal_env conda env injected via sys.path + os.add_dll_directory
- compute_overlap.cp312-win_amd64.pyd: compiled with MSVC 14.50 + Cython 3.2.5 (numpy 1.26.4)
- Google-Resnet101.onnx (211 MB): converted from .h5 via tf_keras + tf2onnx 1.17.0, opset 13
- qgis_gdal_env: requests + pillow installed to unblock TF import and model build
- Git repo initialized

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use qgis_gdal_env for all deps | Avoids modifying QGIS's bundled Python |
| sys.path injection in __init__.py | Standard QGIS plugin pattern for external deps |
| ONNX for inference | Eliminates heavy TF runtime from QGIS; onnxruntime is lightweight |
| tf_keras for conversion only | Keras 2 compat layer; not needed at runtime after ONNX |
| MSVC 14.50 for Cython build | Available at C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools |
| conda defaults channel for onnxruntime | Installed onnxruntime 1.24.4 via conda defaults; no conda-forge pin needed; no solver conflicts |
| Map ONNX outputs by name not index | filtered_detections/1/2 mapped via output_names.index() for robustness against model re-exports |
| range(len(image_boxes)) for iteration | Fixes IndexError where raw indices values exceeded re-indexed image_boxes length |
| parameterAsEnum for TYPE | Returns int (0/1/2) matching geometry comparisons; parameterAsDouble returned float |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use qgis_gdal_env for all deps | Avoids modifying QGIS's bundled Python |
| sys.path injection in __init__.py | Standard QGIS plugin pattern for external deps |
| ONNX for inference | Eliminates heavy TF runtime from QGIS; onnxruntime is lightweight |
| tf_keras for conversion only | Keras 2 compat layer; not needed at runtime after ONNX |
| MSVC 14.50 for Cython build | Available at C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools |
| conda defaults channel for onnxruntime | Installed onnxruntime 1.24.4 via conda defaults; no conda-forge pin needed; no solver conflicts |
| Map ONNX outputs by name not index | filtered_detections/1/2 mapped via output_names.index() for robustness against model re-exports |
| range(len(image_boxes)) for iteration | Fixes IndexError where raw indices values exceeded re-indexed image_boxes length |
| parameterAsEnum for TYPE | Returns int (0/1/2) matching geometry comparisons; parameterAsDouble returned float |
| No palm-specific ONNX publicly downloadable | All probed sources (Deepness, HuggingFace, Roboflow, GitHub, Zenodo) provide .pt weights only or 403 responses; export via ultralytics is the path forward |
| Path A for resolution mismatch | Use fine-GSD OAM TIF (Perak 5 cm/px) with existing tree_tops_yolov9.onnx instead of seeking new model |
| Base YOLOv8m COCO as VHRTrees substitute (06-01) | Google Drive file 1DO785NH13fEleCrQeLQb9L7SSyb1tEiT requires Google auth; automated download returns 401; base model validates inference pipeline |
| onnxruntime 1.20.0 over 1.17.0 (06-01) | numpy 2.5.0 in conda env incompatible with onnxruntime 1.17.0 pybind11; upgraded to 1.20.0 |
| E1 CanopyRS skipped in Phase 6 (06-02) | GitHub Releases = source archives only (no weights); package requires SAM 3 (gated HF), Linux, Python 3.10, CUDA 12.6 — all incompatible |
| Phase 6 outcome: MINIMUM VIABLE SUCCESS (06-04) | 4/5 success criteria met; E2 pipeline validated (COCO base); E1 definitively blocked; domain gap documented; Phase 7 recommendation: QGIS Toolbox VHRTreesAlgorithm |

## Completed Plans

| Plan | Name | Commit | Date |
|------|------|--------|------|
| 01-01 | Install onnxruntime into qgis_gdal_env | 9ca9d53 | 2026-06-12 |
| 01-02 | Replace tf_keras inference with onnxruntime | f8ace04 | 2026-06-12 |
| 01-03 | Delete cp37 .pyd artifact (PLUG-06) | filesystem-only | 2026-06-12 |
| 02-04 | Model and GeoTIFF acquisition (Wave 4) | 7ece01c, 78103b2 | 2026-06-16 |
| 06-01 | E2 VHRTrees YOLOv8m ONNX export and inference test | 2447cbf, 9f3482a, c22ea00 | 2026-06-24 |
| 06-02 | E1 CanopyRS weight verification — BLOCKED | 429e139, 25371c0 | 2026-06-24 |
| 06-03 | E1 CanopyRS ONNX export attempt — SKIPPED (gate pass-through) | ea5ff4d, 46fc70e | 2026-06-24 |
| 06-04 | Results finalization — 06-TEST-RESULTS.md + ROADMAP update | ffcf2ac, cf26ad6 | 2026-06-24 |

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files Changed |
|-------|------|----------|-------|---------------|
| 01 | 01 | ~5 min | 1/1 | 0 (env-only) |
| 01 | 02 | ~10 min | 2/2 | 1 |
| 01 | 03 | ~3 min | 1/1 | 1 (deletion) |
| 02 | 04 | ~45 min | 3/3 | 4 (3 TIF + SOURCES.md) |
| 06 | 01 | ~45 min | 3/3 | 5 (onnx + pt + 3 scripts) |
| 06 | 02 | ~10 min | 2/2 | 1 (download_missing.py blocker comment) |
| 06 | 03 | ~5 min | 2/2 | 3 (inspect_e1_checkpoint.py, export_e1_onnx.py, test_inference_e1.py) |
| 06 | 04 | ~15 min | 2/2 | 2 (06-TEST-RESULTS.md, ROADMAP.md) |

## Accumulated Context

### Roadmap Evolution

- Phase 3 added: Research palm counting/detection models for aerial/satellite imagery — brainstorm candidate projects with pretrained checkpoints; document GSD per model
- Phase 4 added: Palm model download, ONNX conversion, and empirical testing on OAM rasters

---
*Last updated: 2026-06-24 — Phase 6 COMPLETE: 06-04 done; 06-TEST-RESULTS.md produced; ROADMAP updated; Phase 7 recommendation: QGIS Processing Toolbox VHRTreesAlgorithm*
