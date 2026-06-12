# Project State — optimal-ipb

## Status
Phase 1 in progress — Plan 01-01 complete, advancing to Plan 01-02.

## Current Phase
Phase 1: QGIS 3.12 Compatibility & ONNX Inference

## Current Plan
01-02-PLAN.md — Replace tf_keras inference with onnxruntime, fix detect_palm() bugs, update model selector

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

## Completed Plans
| Plan | Name | Commit | Date |
|------|------|--------|------|
| 01-01 | Install onnxruntime into qgis_gdal_env | 9ca9d53 | 2026-06-12 |

## Performance Metrics
| Phase | Plan | Duration | Tasks | Files Changed |
|-------|------|----------|-------|---------------|
| 01 | 01 | ~5 min | 1/1 | 0 (env-only) |

---
*Last updated: 2026-06-12*
