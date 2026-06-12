# Project State — optimal-ipb

## Status
Phase 1 in planning.

## Current Phase
Phase 1: QGIS 3.12 Compatibility & ONNX Inference

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

---
*Last updated: 2026-06-12*
