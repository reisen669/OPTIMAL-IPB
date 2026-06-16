# 02-03 ONNX Probe Results

**Date:** 2026-06-16
**Task:** 02-03 Task 1 — Pre-install Deepness packages + probe tree_tops_yolov9.onnx

---

## Deepness Python 3.12 Package Installation

**Target directory:** `C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\deepness\python3.12\`

**Python used:** `C:\Program Files\QGIS 3.44.2\apps\Python312\python.exe`

**Packages installed:**
| Package | Version | ABI |
|---------|---------|-----|
| opencv-python-headless | 4.9.0.80 | cp37-abi3-win_amd64 (stable ABI) |
| onnxruntime | 1.27.0 | cp312-cp312-win_amd64 (Python 3.12) |
| numpy | 2.4.6 | cp312-cp312-win_amd64 |
| flatbuffers | 25.12.19 | pure Python |
| protobuf | 7.35.1 | cp310-abi3-win_amd64 |
| packaging | 26.2 | pure Python |

**Verification:**
- `deepness/python3.12/cv2/__init__.py` — EXISTS
- `deepness/python3.12/onnxruntime/__init__.py` — EXISTS

**Note on pip exit code:** pip reported exit code 1 due to dependency conflicts in QGIS's global Python environment (numba, scipy, tensorflow — NOT in the --target dir). These are pre-existing conflicts unrelated to our install. Both cv2 and onnxruntime installed successfully into the target directory.

---

## tree_tops_yolov9.onnx — ONNX Metadata Probe

**Model path:** `models/tree_tops_yolov9.onnx`
**File size:** 203,131,890 bytes (~193.7 MB)

**Metadata (before patch):**
```
stride: 32
names: {0: 'tree'}
model_type: "Detector"
class_names: {"0": "Tree"}
resolution: 50
det_conf: 0.1
det_iou_thresh: 0.4
det_type: "YOLO_v9"
tiles_overlap: 25
```

**Input tensor:** `images: [1, 3, 640, 640]` (batch=1, RGB, 640x640 tiles)
**Output tensors:**
- `output0: [1, 5, 8400]` — primary YOLO output (4 bbox coords + 1 class score)
- `1732: [1, 5, 8400]` — auxiliary output (YOLOv9 dual head)

**Deepness compatibility assessment:**
| Key | Required | Present | Value | Compatible? |
|-----|----------|---------|-------|-------------|
| model_type | YES | YES | "Detector" | YES |
| det_type | YES | YES | "YOLO_v9" | YES |
| class_names | YES | YES | {"0": "Tree"} | YES |
| resolution | recommended | YES | 50 (cm/px) | YES |
| det_conf | optional | YES | 0.1 | YES (low threshold — good for resolution mismatch) |
| det_iou_thresh | optional | YES | 0.4 | YES |
| tiles_overlap | optional | YES | 25 | YES |
| tile_size | recommended | NO | — | MISSING — patched |

**Patches applied:**
- Added `tile_size: 640` (inferred from input tensor shape [1, 3, 640, 640])

**Metadata (after patch):**
```
stride: 32
names: {0: 'tree'}
model_type: "Detector"
class_names: {"0": "Tree"}
resolution: 50
det_conf: 0.1
det_iou_thresh: 0.4
det_type: "YOLO_v9"
tiles_overlap: 25
tile_size: 640
```

---

## Summary

- Deepness packages: INSTALLED (Python 3.12 ABI)
- ONNX model: PROBED, metadata valid, tile_size patched
- Resolution mismatch note: Model trained at 10 cm/px (resolution=50 means 50 cm/px in Deepness UI). Test raster is 0.5 m GSD — this matches the ONNX metadata. However the model's TRAINING GSD was 10 cm/px from the Deepness zoo description. The metadata `resolution=50` was already set by the model creator for 0.5 m inference use.
- det_conf=0.1 already in model — no change needed
- QGIS + Deepness ready for Task 2 (QGIS Detection run)
