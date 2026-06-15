# Phase 02: Palm Detection Ensemble — Research

**Researched:** 2026-06-15
**Domain:** QGIS palm/tree detection plugins, Deepness ONNX detection, YOLO model export
**Confidence:** HIGH (Deepness source code read directly; model zoo verified; env probed live)

---

## Summary

This research targets Plugin B for the two-detector ensemble. Plugin A is OPTIMAL-IPB (already confirmed). The primary Plugin B candidate is Deepness (v0.6.5, already installed at `plugins/deepness/`). The most relevant pre-trained model in Deepness's official zoo is "Tree-Tops Detection" (YOLOv9, 640px, 10 cm/px) — no palm-specific model exists in the zoo. The Roboflow community hosts several oil palm detection datasets with pre-trained YOLO weights that can be exported to ONNX.

Three critical facts discovered from reading Deepness source code directly:

1. **Deepness v0.6.5 detection output is geometry-only** — no score/confidence field is written to the output polygon layer. The `det.conf` value is used internally for NMS filtering only. The ensemble algorithm cannot read a score from Deepness output without a workaround (centroid extraction from polygons, with no numeric score available).

2. **Deepness on Windows uses `python` (system PATH) to install its packages**, which resolves to SuperMap Python 3.10 on this machine — not QGIS Python 3.12. The `python3.12/` install directory is currently empty; Deepness has not run its package installer yet.

3. **onnxruntime in user site-packages fails with a DLL error** unless the conda env DLL directories are pre-loaded. OPTIMAL-IPB's `__init__.py` already adds these via `os.add_dll_directory()`, so if OPTIMAL-IPB loads before Deepness in QGIS's plugin load order, onnxruntime will be importable by Deepness via the user site-packages path already in QGIS Python's `sys.path`.

**Primary recommendation:** Use Deepness with the Deepness zoo "Tree-Tops Detection" (YOLOv9 ONNX) as first attempt. Accept that the output has no score field — centroid extraction from bounding box polygons is sufficient for the ensemble geometry; set `score_b = NULL` or derive from bounding box area. If Tree-Tops detections are too sparse on 0.5 m GSD imagery (model trained at 10 cm/px), fall back to a Roboflow oil palm YOLO model re-exported to ONNX with Deepness metadata.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Raster tile splitting | Deepness internal | — | Deepness handles sliding window tiling automatically |
| ONNX inference | Deepness onnxruntime | qgis_gdal_env onnxruntime | Deepness uses its own or user-installed onnxruntime |
| Output layer (polygons) | Deepness | — | Deepness writes multipolygon QGIS memory layer |
| Centroid extraction for ensemble | PalmEnsembleAlgorithm | — | Must convert Deepness polygon centroids at merge time |
| Score field for ensemble | NOT available from Deepness | — | No score written; score_b will be NULL or derived |
| Model export to ONNX | SuperMap Python 3.10 + ultralytics | — | Only Python env with torch available |
| ONNX metadata patching | SuperMap Python 3.10 (onnx 1.17.0) | qgis_gdal_env (onnx 1.21.0) | Both have onnx package |

---

## Standard Stack

### Core (Deepness Plugin B path)
| Library | Version | Purpose | Source |
|---------|---------|---------|--------|
| Deepness plugin | 0.6.5 | QGIS detection plugin | Already installed at `plugins/deepness/` |
| onnxruntime | 1.24.4 | ONNX inference inside Deepness | In user site-packages + qgis_gdal_env |
| opencv-python-headless | 4.13.0 | Image preprocessing inside Deepness | In user site-packages (cv2) |

[VERIFIED: read `plugins/deepness/metadata.txt`, `python_requirements/requirements.txt`, and `packages_installer_dialog.py`]

### For ONNX Export (if needed)
| Library | Version | Purpose | Where Available |
|---------|---------|---------|-----------------|
| ultralytics | 8.4.67 (latest) | YOLOv8/v9/v11 training and ONNX export | NOT installed; pip-installable in SuperMap Python 3.10 |
| torch | 2.7.0+cu126 | PyTorch backend for ultralytics | SuperMap Python 3.10 at `C:\SuperMap\...\conda\python.exe` |
| onnx | 1.17.0 | ONNX model metadata patching | SuperMap Python 3.10 |
| onnx | 1.21.0 | ONNX model metadata patching | qgis_gdal_env |

[VERIFIED: live env probe — `"C:/SuperMap/supermap-iobjectspy-env-gpu-2025-win64/conda/python.exe"` has torch 2.7.0+cu126, onnx 1.17.0; ultralytics 8.4.67 is pip-installable there]

### Installation Commands

**To install ultralytics for ONNX export (use SuperMap Python, which already has torch):**
```powershell
& "C:\SuperMap\supermap-iobjectspy-env-gpu-2025-win64\conda\python.exe" -m pip install ultralytics
```

**To install Deepness packages if the QGIS dialog fails:**
```powershell
# Install cv2 and onnxruntime into Deepness's own dir using QGIS Python:
& "C:\Program Files\QGIS 3.44.2\apps\Python312\python.exe" -m pip install `
  --target "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\deepness\python3.12" `
  "opencv-python-headless>=4.5.5.64,<=4.9.0.80" "onnxruntime>=1.12.1,<=1.17.0"
```

---

## Deepness ONNX Model Format — Verified Technical Specification

### Input Tensor
- Shape: `(batch, 3, H, W)` where H=W=tile_size (e.g., 640)
- dtype: float32, values 0.0–1.0 (Deepness normalizes uint8 → float32 / 255.0)
- Batch size: 1 (static) or dynamic (string dim0)
- Channels: 3 (RGB) — Deepness strips extra channels automatically

[VERIFIED: `model_base.py` `preprocessing()` method — `normalize_values_to_01`, `transpose_nhwc_to_nchw`]

### Output Tensor — YOLO_ULTRALYTICS format (YOLOv8/v9/v11 Ultralytics export)
- 1 output tensor, shape: `(1, 4+num_classes, num_boxes)` e.g., `(1, 5, 8400)` for 1 class at 640px
- Layout (after transpose to `(num_boxes, 4+num_classes)`):
  - `[0:4]` = cx, cy, w, h (centre-xywh, pixel coords in tile)
  - `[4:]` = class probability per class (NO objectness score — it was removed in YOLOv8)
- Deepness applies: `np.max(x[4:]) >= confidence` filter, then NMS

[VERIFIED: `detector.py` `_postprocessing_YOLO_ULTRALYTICS()` — transposes `(1,0)`, filters on `max(x[4:])`, no objectness slot]

### Supported DetectorTypes (from `detection_parameters.py`)
| DetectorType | Use For | Output Layout |
|---|---|---|
| `YOLO_v5_or_v7_default` | YOLOv5 / YOLOv7 default export | `(1, num_boxes, 5+num_classes)`, objectness at `[:,4]` |
| `YOLO_v6` | YOLOv6 | `(1, num_boxes, 4+num_classes)`, confidence per class |
| `YOLO_v9` | YOLOv9 | same layout as Ultralytics but separate enum |
| `YOLO_Ultralytics` | YOLOv8 / YOLOv11 Ultralytics export | `(1, 4+num_classes, num_boxes)` — needs transpose |
| `YOLO_Ultralytics_segmentation` | YOLOv8-seg | 2 outputs — detection + proto masks |
| `YOLO_Ultralytics_obb` | YOLOv8-OBB | rotation included |

[VERIFIED: `detection_parameters.py` `DetectorType` enum and `detector.py` `postprocessing()`]

### Required ONNX Metadata Keys
All keys are JSON-serialized strings embedded in `model.metadata_props`:

| Key | Required | Value | Notes |
|-----|----------|-------|-------|
| `model_type` | YES | `"Detector"` | Deepness uses this to auto-detect model class |
| `det_type` | YES | `"YOLO_Ultralytics"` (for YOLOv8) | Sets postprocessing branch |
| `class_names` | YES (for named output layers) | `{"0": "palm"}` | JSON dict int-key→name |
| `resolution` | recommended | `50` (cm/px for 0.5 m GSD) | Auto-fills resolution field in UI |
| `tile_size` | recommended | `640` | Auto-fills tile size in UI |
| `tiles_overlap` | recommended | `20` | % overlap between tiles |
| `det_conf` | optional | `0.25` | Pre-fills confidence threshold |
| `det_iou_thresh` | optional | `0.45` | Pre-fills IoU threshold |
| `standardization_mean` | optional | `[0.0, 0.0, 0.0]` | Mean for per-channel normalization (0 = skip) |
| `standardization_std` | optional | `[1.0, 1.0, 1.0]` | Std for per-channel normalization (1.0 = skip) |

[VERIFIED: `model_base.py` `get_outputs_channel_names()`, `get_metadata_model_type()`, `get_detector_type()`, and official Deepness docs at `qgis-plugin-deepness.readthedocs.io`]

### Output Vector Layer
- Layer type: `multipolygon` (memory layer)
- Layer name: value of `class_names[0]` (e.g., `"palm"`) — one layer per class
- Attributes: **NONE** — geometry only in Deepness v0.6.5
- The `det.conf` confidence is used for NMS only, not written to the output feature

[VERIFIED: `map_processor_detection.py` `_create_vlayer_for_output_bounding_boxes()` — `QgsFeature()` is created with geometry only, no `setAttributes()`, no `QgsField` definitions]

**Score field implication:** The ensemble algorithm cannot read a `score_b` from Deepness output. The `PalmEnsembleAlgorithm` must handle `score_b = NULL` for Deepness-sourced polygons. The centroid is derived from polygon bounding box center; set `score_b = NULL` in the ensemble output.

---

## Available Pre-Trained Models

### Option 1: Deepness Zoo — Tree-Tops Detection (RECOMMENDED FOR FIRST ATTEMPT)
| Property | Value |
|----------|-------|
| Architecture | YOLOv9 |
| Input size | 640 px |
| Training resolution | 10 cm/px (vs 50 cm/px test raster) |
| Domain | Aerial tree-top detection, mixed public datasets |
| Download | `https://chmura.put.poznan.pl/s/A9zdp4mKAATEAGu` |
| DetectorType | `YOLO_v9` |
| Metadata embedded? | YES (it's from Deepness zoo, should have `model_type`, `det_type`, `class_names`) |

**Resolution mismatch risk:** Model trained at 10 cm/px; test raster is 50 cm/px — trees appear 5x smaller than training. Crown diameter at 0.5 m GSD is ~10–15 px; model was trained on crowns ~50–75 px. Detections may be sparse or fail entirely.

[CITED: `https://qgis-plugin-deepness.readthedocs.io/en/latest/main/main_model_zoo.html`]

### Option 2: Roboflow Oil Palm Aerial Detection (UiTM)
| Property | Value |
|----------|-------|
| Dataset | `universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection` |
| Images | 8,532 aerial RGB palm images |
| Architecture | YOLOv8 (latest Roboflow model version) |
| Training resolution | Aerial (UAV/satellite, resolution unspecified) |
| ONNX export | YES — via `ultralytics` after downloading weights |
| License | Roboflow public dataset terms |

[VERIFIED: WebSearch result — site:universe.roboflow.com UiTM oil palm aerial, 8532 images]
[ASSUMED: exact GSD and training altitude not confirmed — Roboflow pages returned 403]

### Option 3: Roboflow Oil Palm Tree Crown Detection (Personal Utility)
| Property | Value |
|----------|-------|
| Dataset | `universe.roboflow.com/personal-utility/oil-palm-tree-crown-detection-from-aerial-image-ljham` |
| Architecture | YOLOv11n (yolov11n) |
| Classes | 7 classes |
| Published | January 2025 |
| Training resolution | Aerial, not confirmed |

[CITED: WebSearch — `universe.roboflow.com/personal-utility/oil-palm-tree-crown-detection...`]
[ASSUMED: exact GSD and download format not confirmed — Roboflow pages returned 403]

### Option 4: Roboflow Oil Palm Detection (Manfred Michael)
| Property | Value |
|----------|-------|
| Dataset | `universe.roboflow.com/manfred-michael/oil-palm-detection/dataset/6` |
| Images | 4,063 images |
| YOLO versions | YOLOv5, v7, v8, v9, v11 available |
| Published | 2024 |

[CITED: WebSearch — `universe.roboflow.com/manfred-michael/oil-palm-detection`]
[ASSUMED: exact GSD, license, download instructions not confirmed]

---

## ONNX Export Workflow (if Roboflow model needed)

### Step 1: Install ultralytics in SuperMap Python
```powershell
& "C:\SuperMap\supermap-iobjectspy-env-gpu-2025-win64\conda\python.exe" -m pip install ultralytics
```

### Step 2: Export to ONNX
```python
# Run with SuperMap Python 3.10 (has torch 2.7.0+cu126)
from ultralytics import YOLO
model = YOLO("path/to/downloaded_weights.pt")
model.export(format="onnx", imgsz=640, opset=12, simplify=True, dynamic=False)
# Creates: path/to/downloaded_weights.onnx
```

### Step 3: Patch ONNX metadata for Deepness
```python
# Run with qgis_gdal_env (onnx 1.21.0) or SuperMap Python (onnx 1.17.0)
import json, onnx
model = onnx.load("path/to/model.onnx")

meta_to_add = {
    "model_type": "Detector",
    "det_type": "YOLO_Ultralytics",
    "class_names": {"0": "palm"},
    "resolution": 50,        # cm/px — match test raster GSD
    "tile_size": 640,
    "tiles_overlap": 20,
    "det_conf": 0.25,
    "det_iou_thresh": 0.45,
}

for key, value in meta_to_add.items():
    m = model.metadata_props.add()
    m.key = key
    m.value = json.dumps(value)

onnx.save(model, "path/to/model_deepness.onnx")
```

[VERIFIED: `model_base.py` reads exactly these key names; metadata format from official Deepness docs]

### Step 4: Load in Deepness
1. Open QGIS → Deepness dock widget
2. Model file: browse to `model_deepness.onnx`
3. Task type: Detection
4. Detector type: `YOLO_Ultralytics`
5. Confidence: 0.25 (low threshold — palm detection on non-ideal resolution)
6. IoU threshold: 0.45
7. Resolution: 0.5 m/px (50 cm/px) — must match raster
8. Run on `imagery_0.5mpx.tif`

---

## Deepness Package Installation — Windows-Specific Risk

**Problem:** On Windows, `packages_installer_dialog.py` line 91 sets `PYTHON_EXECUTABLE_PATH = 'python'`. On this machine, `where python` resolves to `C:\SuperMap\...\conda\python.exe` (Python 3.10), not QGIS Python 3.12.

**Effect:** If the Deepness installer dialog triggers, it installs cv2/onnxruntime wheels built for Python 3.10 into the `python3.12/` target dir. These would be the wrong ABI.

**Current state:** `plugins/deepness/python3.12/` is empty — Deepness packages have NOT been installed yet.

**Workaround available:**
- cv2 is already available in QGIS Python's sys.path via `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages\cv2` (opencv-python 4.13.0, Python 3.12 wheel) [VERIFIED: live probe]
- onnxruntime 1.24.4 is in `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages\onnxruntime` but fails DLL import WITHOUT the conda env DLL dirs pre-loaded [VERIFIED: live test]
- OPTIMAL-IPB `__init__.py` calls `os.add_dll_directory()` which makes onnxruntime importable once OPTIMAL-IPB loads first

**Recommended plan action:** Pre-install Deepness packages manually with QGIS Python before opening QGIS:
```powershell
& "C:\Program Files\QGIS 3.44.2\apps\Python312\python.exe" -m pip install `
  --target "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\deepness\python3.12" `
  "opencv-python-headless>=4.5.5.64,<=4.9.0.80" "onnxruntime>=1.12.1"
```
This installs Python 3.12 wheels into the correct target directory, bypassing the buggy Windows installer.

[VERIFIED: Deepness source code; live probe of Python environments; confirmed `python3.12/` is empty]

---

## Architecture Patterns

### Data Flow: Plugin B (Deepness) Detection

```
imagery_0.5mpx.tif (1284x956 px, 0.5 m GSD)
        |
        v
Deepness Dock Widget
  - Model: tree_tops_yolov9.onnx (or palm_yolov8.onnx)
  - Detector type: YOLO_v9 (or YOLO_Ultralytics)
  - Resolution: 0.5 m/px
  - Tile size: 640 px
  - Overlap: 20%
        |
        v (sliding window: ~16 tiles at 20% overlap)
ONNX inference via onnxruntime
  Input:  (1, 3, 640, 640) float32
  Output: (1, 5, 8400) float32   [for 1-class YOLO_ULTRALYTICS]
        |
        v
postprocessing: confidence filter + NMS
        |
        v
multipolygon QGIS memory layer ("palm")
  - Geometry: bounding box polygons in raster CRS
  - Attributes: NONE (geometry only)
        |
        v (in PalmEnsembleAlgorithm)
centroid extraction: QgsGeometry.centroid()
  - score_b = NULL (no confidence field)
```

### Centroid Extraction in Ensemble
Since Deepness outputs polygons (not points), the ensemble must extract centroids:
```python
# In PalmEnsembleAlgorithm, when processing Layer B (Deepness output):
for feat in layer_b.getFeatures():
    centroid = feat.geometry().centroid()  # works on polygon too
    # score_b = NULL — no attribute
```

[VERIFIED: Deepness outputs `multipolygon` geometry (`map_processor_detection.py` line 178: `vlayer = QgsVectorLayer("multipolygon", ...)`)]

---

## Common Pitfalls

### Pitfall 1: Resolution mismatch between model and raster
**What goes wrong:** Tree-Tops Detection is trained at 10 cm/px. Test raster is 50 cm/px. Deepness will process tiles from a 5x lower-resolution raster than training. Tree crowns that were 50–75 px in training appear as 10–15 px objects. Detection recall drops severely.
**How to avoid:** Lower confidence threshold to 0.1–0.15 when testing. If still zero detections, switch to a palm model trained at closer GSD (~0.5–1 m).
**Warning signs:** Detection count = 0 in the result message panel.

### Pitfall 2: Deepness installer uses wrong Python on Windows
**What goes wrong:** First launch triggers installer dialog; it calls `python` which is SuperMap Python 3.10, installs Python 3.10 wheels into `python3.12/` dir. cv2 3.10 wheel crashes on import.
**How to avoid:** Pre-install packages with QGIS Python 3.12 before first QGIS launch, OR dismiss the installer dialog (onnxruntime already accessible via user site-packages if DLL dirs are loaded first).
**Warning signs:** `ImportError` for cv2 or onnxruntime in QGIS Log Messages after Deepness loads.

### Pitfall 3: onnxruntime DLL load failure without DLL directories
**What goes wrong:** `onnxruntime_pybind11_state.pyd` cannot find conda-installed DLLs. Import fails at QGIS startup if OPTIMAL-IPB has not already added DLL dirs.
**How to avoid:** Ensure OPTIMAL-IPB loads before Deepness (alphabetical order: `deepness` < `optimal-ipb` — so Deepness loads FIRST). This means the DLL fix order is wrong if relying on load order.
**Actual fix:** Pre-install onnxruntime into `python3.12/` dir using QGIS Python; it will then find its own DLLs.

### Pitfall 4: Deepness writes polygon output; ensemble expects points
**What goes wrong:** PalmEnsembleAlgorithm accepts point layers, but Deepness produces polygons. Direct use will fail geometry comparison.
**How to avoid:** In the ensemble algorithm, detect geometry type and call `.centroid()` if input layer is polygon. OR: use QGIS "Centroids" tool to convert Deepness output before ensemble. Document this in the ensemble plan.

### Pitfall 5: Missing ONNX metadata — Deepness cannot auto-detect model type
**What goes wrong:** If loading a Roboflow model without metadata, Deepness shows all fields as blank and model type as unknown. User must manually set all fields.
**How to avoid:** Always patch ONNX metadata (Step 3 in export workflow above) before loading into Deepness.

### Pitfall 6: class_names key format — must be string keys
**What goes wrong:** `json.dumps({0: "palm"})` produces `{"0": "palm"}` which is fine. But `ast.literal_eval` fallback in Deepness expects dict with int keys. Use standard `json.dumps`.
**How to avoid:** Use `json.dumps({"0": "palm"})` exactly as shown in the metadata patch script.

[VERIFIED: `model_base.py` `get_outputs_channel_names()` — tries `json.loads` first, then `ast.literal_eval` fallback]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sliding window tiling | Custom tile iterator | Deepness built-in | Handles overlap, CRS projection, mask areas |
| NMS post-processing | Custom NMS | Deepness `non_max_suppression_fast()` | Already handles cross-tile duplicates via KD-tree |
| ONNX model loading | onnxruntime.InferenceSession manually | Deepness `ModelBase` wraps it | Handles providers (CUDA/CPU fallback) |
| YOLO ONNX export | Manual weight manipulation | `model.export(format="onnx")` from ultralytics | Handles opset, graph simplification, dynamic axes |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Deepness plugin | Plugin B | YES | 0.6.5 at `plugins/deepness/` | — |
| onnxruntime | Deepness inference | YES (with caveats) | 1.24.4 in user+qgis_gdal_env | Pre-install in python3.12/ dir |
| cv2 | Deepness preprocessing | YES | 4.13.0 in user site-packages | Pre-install in python3.12/ dir |
| ultralytics | ONNX export of Roboflow model | NO | 8.4.67 (pip-installable) | Install in SuperMap Python 3.10 |
| torch | ultralytics dependency | YES (SuperMap Python 3.10 only) | 2.7.0+cu126 | — |
| onnx | Metadata patching | YES | 1.21.0 (qgis_gdal_env), 1.17.0 (SuperMap) | — |
| Tree-Tops ONNX model | Deepness Plugin B | NO (not downloaded yet) | — | Download from Deepness zoo |

**Missing dependencies with no fallback:**
- Tree-Tops ONNX model file (must download before testing)

**Missing dependencies with fallback:**
- ultralytics (install in SuperMap Python if Roboflow model path needed)
- Deepness python3.12 packages (pre-install with QGIS Python to avoid Windows installer bug)

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| YOLOv5 (1 output tensor `[1, N, 85]`) | YOLOv8/v9/v11 Ultralytics (`[1, 84, N]`, no objectness) | Deepness has separate DetectorType for each — must match |
| Manual metadata addition | Deepness reads from ONNX `model.metadata_props` automatically | Must patch metadata before loading |
| Deepness 0.5.x required separate install | Deepness 0.6.x bundles installer dialog (Windows bug: uses PATH python) | Must pre-install or accept dialog + DLL workaround |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Roboflow UiTM model (8532 images) trained on aerial imagery suitable for ~0.5 m GSD | Available Models → Option 2 | Model may be UAV at much higher GSD; detections may be poor |
| A2 | Roboflow models have downloadable `.pt` weights (not API-only) | ONNX Export Workflow | If weights are API-only, export is not possible; must train from dataset |
| A3 | Deepness zoo Tree-Tops model `.onnx` file already contains valid Deepness metadata | Models → Option 1 | If metadata missing, must patch it manually before loading |
| A4 | Deepness plugin loads correctly in QGIS 3.44 once packages are installed | Environment | Plugin 0.6.5 may have incompatibility with QGIS 3.44.2 (newer than 3.22 minimum) |
| A5 | Centroid extraction from Deepness bounding box polygons is sufficient for ensemble matching | Data Flow | If Deepness polygons are very large or irregular, centroid offset may exceed 10 m threshold |

---

## Open Questions (RESOLVED)

1. **Does the Deepness Tree-Tops model produce any detections at 50 cm/px?**
   - What we know: model trained at 10 cm/px (5x finer than test raster)
   - What's unclear: whether the model still fires on palm-sized objects at 50 cm/px resolution
   - RESOLVED: 02-03-PLAN.md Task 2 tests this at confidence=0.10; Task 3 is the explicit Roboflow fallback if zero detections result.

2. **Are Roboflow YOLO palm model weights (.pt files) publicly downloadable without API key?**
   - What we know: Roboflow Universe hosts pre-trained models; some are API-only
   - What's unclear: whether `.pt` download is free/public for the specific palm datasets
   - RESOLVED: 02-03-PLAN.md Task 3 Sub-task B provides the Manfred Michael GitHub alternative (no API key required) and dataset-annotation YOLOv8n training as a last resort.

3. **Does Deepness polygon output always have geometry_type=multipolygon or sometimes polygon?**
   - What we know: source code uses `QgsVectorLayer("multipolygon", ...)` — the layer type
   - What's unclear: whether single-ring features are stored as Polygon or MultiPolygon parts
   - RESOLVED: 02-03-PLAN.md Task 2 Step 5 uses `feat.geometry().centroid()` which is valid for both Polygon and MultiPolygon geometry types.

4. **Will the Deepness installer dialog appear when QGIS first opens with Deepness enabled?**
   - What we know: `python3.12/` dir is empty; `are_packages_importable()` will fail; dialog will show
   - RESOLVED: 02-03-PLAN.md Task 1 pre-installs cv2 + onnxruntime into `deepness/python3.12/` via QGIS Python 3.12 before first QGIS launch, bypassing the installer dialog entirely.

---

## Sources

### Primary (HIGH confidence)
- `plugins/deepness/processing/models/detector.py` — postprocessing methods for all YOLO types
- `plugins/deepness/processing/map_processor/map_processor_detection.py` — output layer creation (confirmed: no score field)
- `plugins/deepness/processing/models/model_base.py` — ONNX loading, metadata reading, preprocessing
- `plugins/deepness/common/processing_parameters/detection_parameters.py` — DetectorType enum
- `plugins/deepness/dialogs/packages_installer/packages_installer_dialog.py` — Windows installer bug (PATH python)
- `plugins/deepness/python_requirements/requirements.txt` — required packages
- `plugins/deepness/metadata.txt` — version 0.6.5 confirmed
- Live env probes: Python versions, torch/onnxruntime/cv2 availability verified with direct interpreter calls

### Secondary (MEDIUM confidence)
- `https://qgis-plugin-deepness.readthedocs.io/en/latest/creators/creators_add_metadata_to_model.html` — metadata key names and values
- `https://qgis-plugin-deepness.readthedocs.io/en/latest/main/main_model_zoo.html` — model zoo listing including Tree-Tops Detection
- `https://github.com/PUTvision/qgis-plugin-deepness/releases/tag/0.6.5` — release notes (minimal)
- WebSearch: YOLOv8 ONNX output tensor shape `(1, 84, 8400)` confirmed by multiple sources

### Tertiary (LOW confidence — needs validation)
- Roboflow Universe oil palm datasets (UiTM 8532 images, Manfred Michael 4063 images, Personal Utility YOLOv11n) — pages returned 403; details from WebSearch snippets only
- Training GSD of Roboflow palm models — unverified

---

## Metadata

**Confidence breakdown:**
- Deepness source code analysis: HIGH — read directly from installed plugin
- Deepness model format (ONNX tensor shapes, metadata keys): HIGH — verified from source + docs
- Score field absence: HIGH — confirmed from source code; `_create_vlayer_for_output_bounding_boxes` writes no attributes
- Available pre-trained models: MEDIUM — zoo confirmed, Roboflow details LOW
- Environment availability: HIGH — probed live with Python interpreters
- ONNX export workflow: HIGH for ultralytics command; MEDIUM for SuperMap Python compatibility

**Research date:** 2026-06-15
**Valid until:** 2026-09-15 (Deepness updates infrequently; ultralytics more active — re-verify if > 30 days)
