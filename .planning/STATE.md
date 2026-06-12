# Project State — optimal-ipb

## Status
Phase 1 in progress — Plan 01-02 complete. Phase 1 core migration done.

## Current Phase
Phase 1: QGIS 3.12 Compatibility & ONNX Inference

## Current Plan
01-02-PLAN.md — COMPLETE. Plugin now uses onnxruntime for inference with no tensorflow dependency.

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

## Completed Plans
| Plan | Name | Commit | Date |
|------|------|--------|------|
| 01-01 | Install onnxruntime into qgis_gdal_env | 9ca9d53 | 2026-06-12 |
| 01-02 | Replace tf_keras inference with onnxruntime | f8ace04 | 2026-06-12 |

## Performance Metrics
| Phase | Plan | Duration | Tasks | Files Changed |
|-------|------|----------|-------|---------------|
| 01 | 01 | ~5 min | 1/1 | 0 (env-only) |
| 01 | 02 | ~10 min | 2/2 | 1 |

---
*Last updated: 2026-06-12*
