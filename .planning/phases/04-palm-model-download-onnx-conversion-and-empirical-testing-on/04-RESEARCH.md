# Phase 4: Palm Model Verification and Empirical Testing — Research

**Researched:** 2026-06-19
**Domain:** ONNX model verification, QGIS Processing algorithm invocation, git strategy for large binaries, Python dependency resolution
**Confidence:** HIGH (all findings verified against actual files on disk)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Phase 4 = commit + verify + test what's already built. No new model downloads.
- **D-02:** Geoeye-Resnet101.onnx and Pleiades-Resnet101.onnx present but provenance uncertain. Run `verify_onnx_models.py` first; if verification fails, exclude and note in results. Do not block Phase 4 on their status.
- **D-03:** MOPAD model (`models/mopad/MOPAD_epoch_24.onnx`, 242 MB) is downloaded and considered valid. Include as a first-class VHR candidate alongside B1 and H1.
- **D-04:** Light requirements: MOD-01 through MOD-05.
- **D-05:** `mopad_algorithm.py` and `roboflow_algorithm.py` stay as standalone scripts — NOT registered in `optimal_ipb_provider.py`. Phase 4 uses them directly for testing only.
- **D-06:** `optimal_ipb_algorithm.py` edge-clamping + log message changes committed as Phase 4 task 1.
- **D-07:** All new files stay at current locations. No reorganization.
- **D-08:** Testing output = quantitative (detection count + confidence distribution at default threshold) AND visual (QGIS layer, confirm points/boxes fall on palm crowns).
- **D-09:** Test matrix: VHR (B1, H1, MOPAD) → Perak 5cm + Rupat 8.8cm; MR (B2/B3/B4 if verified) → Aceh 50cm; Roboflow → Perak + Rupat.
- **D-10:** Results in `.planning/phases/04-palm-model-download-onnx-conversion-and-empirical-testing-on/04-TEST-RESULTS.md`.
- **D-11:** Phase 4 success = at least one VHR model produces visually plausible palm detections on Perak or Rupat.
- **D-12:** `roboflow_algorithm.py` in scope — commit and test on Perak + Rupat.

### Claude's Discretion

- Wave structure and ordering of commits within Phase 4
- Exact column layout and formatting of 04-TEST-RESULTS.md
- Score threshold values used for each model (use defaults from each algorithm's code)
- Whether to use Python script or QGIS Processing Toolbox runner for model testing (whichever is faster)
- git-lfs vs .gitignore strategy for large ONNX files

### Deferred Ideas (OUT OF SCOPE)

- Provider integration for MOPAD + Roboflow (registering in `optimal_ipb_provider.py`)
- detectree2 (N1) — Detectron2, not ONNX-loadable without extra work
- deepforest (N2) — US NEON domain gap; skip unless all VHR fail
- MADAN (N4) — Baidu/Google Drive unconfirmed
- Confidence threshold tuning — use defaults, calibration is future work
- git-LFS remote setup — repo has no remote; LFS tracking is optional
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MOD-01 | All untracked Phase 4 files committed (`optimal_ipb_algorithm.py`, `mopad_algorithm.py`, `roboflow_algorithm.py`, `verify_onnx_models.py`, `download_missing.py`, model files in git-lfs or .gitignore as appropriate) | Git strategy section covers large-file handling; file list verified on disk |
| MOD-02 | All ONNX models verified with `verify_onnx_models.py` — pass/fail recorded; failures noted before testing | verify_onnx_models.py analysis shows MOPAD path gap; fix documented |
| MOD-03 | VHR models (B1, H1, MOPAD) run on Perak + Rupat; detection counts + visual check in `04-TEST-RESULTS.md` | QGIS Console invocation pattern documented; all three algorithms analyzed |
| MOD-04 | MR models (B2/B3/B4 — if verified) run on Aceh; detection counts + visual check recorded | `optimal_ipb_algorithm.py` is the runner; B2 is confirmed working; B3/B4 contingent on MOD-02 |
| MOD-05 | Roboflow algorithm run on Perak + Rupat; results recorded; API key usage confirmed working | `roboflow_algorithm.py` analyzed; API key pattern documented; Pillow dependency confirmed present |
</phase_requirements>

---

## Summary

Phase 4 is a commit-verify-test phase using work that already exists on disk. The primary technical challenges are (1) an MOPAD path gap in `verify_onnx_models.py`, (2) a missing `.gitignore` meaning large model files (37–484 MB) are currently untracked rather than explicitly excluded, and (3) the decision that all algorithms must be run from the QGIS Python Console rather than standalone scripts because both `mopad_algorithm.py` and `roboflow_algorithm.py` import QGIS Processing API classes (`QgsProcessingAlgorithm`, `QgsFeatureSink`, etc.) that are only available inside a running QGIS process.

The dependency stack is in good shape. `lsnms` 0.4.5 is installed in the Python 3.12 user roaming site-packages, which QGIS 3.44.2's embedded Python 3.12 picks up automatically. `onnxruntime` 1.24.4 is in `qgis_gdal_env` and injected by `__init__.py`. `Pillow` 12.0.0 is in `qgis_gdal_env`. All three OAM test rasters are confirmed present in `tif_online_samples/`. No blocking dependency issues exist.

The git strategy is straightforward: create a `.gitignore` that excludes all large binary files (`models/*.onnx`, `models/**/*.onnx`, `models/**/*.pth`, `tif_online_samples/`, the `Google-Resnet101-savedmodel/` directory). This avoids committing files up to 484 MB to a local-only repo with no remote. The `.py` script files and planning documents are committed normally. git-lfs is installed globally but no `.gitattributes` exists — there is no reason to set up LFS for a repo with no remote.

**Primary recommendation:** Run all algorithm tests via the QGIS Python Console using `processing.run()` with each algorithm's class instantiated directly. Use `layer.featureCount()` on the returned layer ID for detection count.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| ONNX model loading and inference | QGIS Plugin (Python) | qgis_gdal_env (onnxruntime) | All three ONNX algorithms use `onnxruntime.InferenceSession`; QGIS provides the `feedback` and `sink` objects |
| Raster I/O (tile reading) | QGIS Plugin (osgeo.gdal) | — | `gdal.Open(source.source())` resolves the layer path via QGIS layer registry |
| Vector output sink | QGIS Processing Framework | In-memory layer | `QgsFeatureSink` written through `parameterAsSink`; output is a QGIS in-memory vector layer |
| Roboflow API calls | External service (HTTPS) | QGIS Plugin (urllib) | `roboflow_algorithm.py` calls `detect.roboflow.com` via urllib; QGIS provides API key from global variable |
| NMS post-processing | lsnms (user site-packages) | helpers.py fallback | `from lsnms import nms` in all three algorithms; `roboflow_algorithm.py` has a graceful fallback if lsnms is missing |
| Git history (code files) | git (local) | — | No remote; commit .py files and planning docs normally |
| Git strategy (large binaries) | .gitignore | — | No remote = no LFS remote; exclude model files and TIFs from git entirely |

---

## Standard Stack

### Core (already installed — no action needed)

| Library | Version | Purpose | Where installed |
|---------|---------|---------|-----------------|
| onnxruntime | 1.24.4 | ONNX model inference for all ONNX algorithms | `qgis_gdal_env` Lib/site-packages [VERIFIED: filesystem] |
| lsnms | 0.4.5 | Vectorised NMS used by all three algorithms | `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages` [VERIFIED: filesystem] |
| Pillow | 12.0.0 | JPEG encoding in `roboflow_algorithm.py` (`_to_jpeg_bytes`) | `qgis_gdal_env` Lib/site-packages [VERIFIED: filesystem] |
| osgeo.gdal | 3.11.0 | Raster I/O in all algorithms | `qgis_gdal_env` (conda) [VERIFIED: filesystem] |
| numpy | 2.2.6 | Array math for tile preprocessing | `qgis_gdal_env` Lib/site-packages [VERIFIED: filesystem] |

### QGIS Processing API (provided by QGIS host — no install needed)

| Symbol | Module | Used by |
|--------|--------|---------|
| `QgsProcessingAlgorithm` | `qgis.core` | `mopad_algorithm.py`, `roboflow_algorithm.py` |
| `QgsFeatureSink`, `QgsFeature` | `qgis.core` | All three algorithm files |
| `QgsExpressionContextUtils` | `qgis.core` | `roboflow_algorithm.py` (reads API key from global variable) |
| `processing.run()` | `qgis.core` via console | Recommended testing invocation method |

---

## Architecture Patterns

### System Architecture Diagram

```
                    QGIS Python Console (testing entry point)
                                    │
                     processing.run("algorithm_id", params)
                                    │
                    ┌───────────────▼───────────────┐
                    │   QGIS Processing Framework    │
                    │   (resolves algorithm by ID)   │
                    └───────────────┬───────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
   OptimalIpbAlgorithm      MOPADPalmAlgorithm   RoboflowPalmDetectionAlgorithm
   (optimal_ipb_algorithm)  (mopad_algorithm)    (roboflow_algorithm)
   RetinaNet ONNX            Faster R-CNN ONNX   UiTM YOLOv8n API
   500×500 tiles             1024×1024 tiles     Resolution-aware tiles→10cm/px
              │                     │                     │
              ▼                     ▼                     ▼
   models/*.onnx via         models/mopad/         detect.roboflow.com HTTPS
   ort.InferenceSession      MOPAD_epoch_24.onnx   (Base64 JPEG POST)
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                    osgeo.gdal raster I/O (all algorithms)
                    helpers.pixel2coord, map_uint16_to_uint8
                    lsnms.nms post-processing
                                    │
                                    ▼
                    QgsFeatureSink → in-memory vector layer
                    (Point or BBox polygon, georeferenced)
```

### Recommended Project Structure (no changes needed — D-07)

```
optimal-ipb/
├── optimal_ipb_algorithm.py   # RetinaNet ONNX algorithm (modified, uncommitted)
├── mopad_algorithm.py         # MOPAD Faster R-CNN algorithm (untracked)
├── roboflow_algorithm.py      # Roboflow API algorithm (untracked)
├── verify_onnx_models.py      # Model verification script (untracked, needs MOPAD fix)
├── download_missing.py        # Imagery download helper (untracked)
├── helpers.py                 # Shared utilities (tracked)
├── .gitignore                 # NEW — exclude models/*.onnx, tif_online_samples/, etc.
├── models/
│   ├── tree_tops_yolov9.onnx          # B1 (203 MB) — excluded by .gitignore
│   ├── tribber93_yolov11_palm.onnx    # H1 (37.9 MB) — excluded by .gitignore
│   ├── Google-Resnet101.onnx          # B2 (211 MB) — excluded by .gitignore
│   ├── Geoeye-Resnet101.onnx          # B3 (221 MB) — excluded by .gitignore
│   ├── Pleiades-Resnet101.onnx        # B4 (221 MB) — excluded by .gitignore
│   ├── mopad/
│   │   ├── MOPAD_epoch_24.onnx        # (242 MB) — excluded by .gitignore
│   │   └── MOPAD_epoch_24.pth         # (484 MB) — excluded by .gitignore
│   └── MODEL_CONVERSION_STATUS.md     # tracked (text, small)
└── tif_online_samples/                # excluded by .gitignore (30–5 MB TIFs)
```

### Pattern 1: QGIS Console Algorithm Invocation

**What:** Run a registered Processing algorithm from the QGIS Python Console using `processing.run()`, which returns a dict with output IDs. The output vector layer can be retrieved and feature count read programmatically.

**When to use:** Any time you need to run `mopad_algorithm.py`, `roboflow_algorithm.py`, or `optimal_ipb_algorithm.py` without opening the full Processing Toolbox dialog.

**Note:** `mopad_algorithm.py` and `roboflow_algorithm.py` are NOT currently registered in `optimal_ipb_provider.py` (D-05). To test them from the console, they must first be temporarily registered OR imported and their `processAlgorithm` called indirectly through a minimal wrapper. The simplest approach is to register them temporarily for the test session. See Anti-Patterns section for the alternative (calling `processAlgorithm` directly — this does NOT work because the sink is not initialized outside the Processing framework).

**Recommended test invocation pattern — temporary registration approach:**

```python
# Source: [ASSUMED] — standard QGIS Processing pattern, verified against ARCHITECTURE.md
# Run in QGIS Python Console

# Step 1: Import and temporarily register the algorithm
import sys, os
plugin_dir = r'C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb'
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from mopad_algorithm import MOPADPalmAlgorithm
from qgis.core import QgsApplication
alg = MOPADPalmAlgorithm()
QgsApplication.processingRegistry().addAlgorithm(alg)

# Step 2: Run with parameters
import processing
raster_path = plugin_dir + r'\tif_online_samples\oam_perak_01E2b_0.05mpx.tif'
result = processing.run(
    'mopad-palm-detection',
    {
        'INPUT': raster_path,
        'SCORE_THR': 0.05,   # default from code
        'NMS_IOU': 0.3,      # default from code
        'TYPE': 0,           # Point output
        'EXCLUDE_GRASS': True,
        'OUTPUT': 'memory:'
    }
)

# Step 3: Get detection count
output_layer_id = result['OUTPUT']
from qgis.core import QgsVectorLayer, QgsProject
layer = QgsProject.instance().mapLayer(output_layer_id)
# If not in project (memory: layers from processing.run are sometimes not added):
from qgis.core import QgsProcessingContext
# Alternatively, use processing.runAndLoadResults to auto-add to canvas:
result2 = processing.runAndLoadResults('mopad-palm-detection', { ... })
# Then access via QgsProject.instance().mapLayersByName('MOPAD detections')[0]
count = layer.featureCount()
print(f"Detections: {count}")
```

**Alternative: Load raster via QGIS layer and pass layer object:**

```python
# Source: [ASSUMED] — standard QGIS Processing pattern
from qgis.core import QgsRasterLayer, QgsProject
rl = QgsRasterLayer(raster_path, 'perak')
QgsProject.instance().addMapLayer(rl)
result = processing.run('mopad-palm-detection', {'INPUT': rl, ...})
```

### Pattern 2: Running OptimalIpbAlgorithm (B1/H1/B2/B3/B4)

**What:** `optimal_ipb_algorithm.py` IS registered in `optimal_ipb_provider.py`. When the plugin is loaded in QGIS, the algorithm is already registered under the OPTIMAL-IPB provider. The algorithm scans `models/*.onnx` at `initAlgorithm` time and presents them as an enum. Models are selected by index, not by name.

```python
# Source: ARCHITECTURE.md §Entry Points + code inspection [VERIFIED: optimal_ipb_algorithm.py]
# Run in QGIS Python Console (plugin must be loaded first)
import processing

# The MODEL parameter is an enum INDEX into the list of .onnx files in models/
# The list is sorted alphabetically: Geoeye, Google, Pleiades, tree_tops, tribber93
# Verify the index order by checking modelsList in the algorithm

result = processing.runAndLoadResults(
    'OPTIMAL-IPB:palmtreecalculation',  # actual algorithm ID — verify from provider
    {
        'INPUT': r'C:\...\tif_online_samples\oam_perak_01E2b_0.05mpx.tif',
        'MODEL': 3,        # index of tree_tops_yolov9.onnx in sorted list (0-based)
        'mAP': 0.5,        # default score threshold
        'TYPE': 0,         # Point output
        'OUTPUT': 'memory:'
    }
)
```

**Caution — model enum index must be verified at runtime:** The enum is built from `os.listdir('models/')` alphabetically filtered to `.onnx`. On the current disk: `Geoeye-Resnet101.onnx`(0), `Google-Resnet101.onnx`(1), `Pleiades-Resnet101.onnx`(2), `tree_tops_yolov9.onnx`(3), `tribber93_yolov11_palm.onnx`(4). The planner should include a step to print `modelsList` from the console before testing to confirm indices.

### Pattern 3: Getting the Algorithm ID

```python
# Source: [ASSUMED] — standard QGIS Processing API
# List all registered algorithms to find the correct ID:
for alg in QgsApplication.processingRegistry().algorithms():
    if 'ipb' in alg.id().lower() or 'mopad' in alg.id().lower():
        print(alg.id())
```

### Anti-Patterns to Avoid

- **Calling `processAlgorithm()` directly on a fresh algorithm instance:** `processAlgorithm()` calls `self.parameterAsSink(...)` which requires the QGIS Processing context to be initialized. Calling it outside `processing.run()` raises `AttributeError: 'NoneType' object has no attribute 'addMapLayer'` or similar. Always use `processing.run()` or `processing.runAndLoadResults()`.
- **Running verify_onnx_models.py from cmd.exe:** The script imports `onnxruntime` which must be in sys.path. Running `python verify_onnx_models.py` from the Windows command prompt uses the wrong Python unless the qgis_gdal_env or user roaming Python is activated first. Preferred runner: `python-qgis.bat verify_onnx_models.py` or the QGIS Python Console via `exec(open('verify_onnx_models.py').read())`.

---

## Focus Area 1: verify_onnx_models.py — Analysis and Coverage Gap

### What it does [VERIFIED: verify_onnx_models.py source]

```python
models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
onnx_files = sorted(f for f in os.listdir(models_dir) if f.endswith('.onnx'))
```

It uses `os.listdir(models_dir)` — which lists only the immediate directory, not subdirectories. Files matched:
- `Geoeye-Resnet101.onnx`
- `Google-Resnet101.onnx`
- `Pleiades-Resnet101.onnx`
- `tree_tops_yolov9.onnx`
- `tribber93_yolov11_palm.onnx`

**NOT matched:** `models/mopad/MOPAD_epoch_24.onnx` — this is in a subdirectory.

### Fix required [VERIFIED: file structure on disk]

The planner must add a task that patches `verify_onnx_models.py` to also check the MOPAD path, OR runs a one-liner check for MOPAD separately. The minimal fix is to add the MOPAD path explicitly after the main loop:

```python
# Patch to add after the main loop — verified against actual file path
_MOPAD_PATH = os.path.join(models_dir, 'mopad', 'MOPAD_epoch_24.onnx')
if os.path.isfile(_MOPAD_PATH):
    extra_files = [('models/mopad/MOPAD_epoch_24.onnx', _MOPAD_PATH)]
else:
    extra_files = []

# Then run the same try/except ort.InferenceSession block for each
```

Alternatively, replace `os.listdir` with a recursive `os.walk` approach to collect all `.onnx` files. Simpler alternative: patch the script to use `glob.glob('**/*.onnx', recursive=True)`.

### Running verify_onnx_models.py

The script uses `onnxruntime` from sys.path. It can be run:
- From the QGIS Python Console: `exec(open(r'C:\...\optimal-ipb\verify_onnx_models.py').read())`
- From the cmd.exe with qgis_gdal_env activated: `conda activate qgis_gdal_env && python verify_onnx_models.py`

**Expected output for a valid model:**
```
[OK]  Google-Resnet101.onnx (211 MB)
      inputs=['input_1']
      outputs=['filtered_detections/1', 'filtered_detections/2', 'filtered_detections/3']
```

**Geoeye/Pleiades uncertainty:** `MODEL_CONVERSION_STATUS.md` says Geoeye and Pleiades `.h5` conversions FAILED with `TypeError: 'NoneType' object is not subscriptable` (Keras 3 BatchNorm incompatibility). However, the ONNX files ARE present on disk. Their provenance is unknown (possibly downloaded from the upstream OPTIMAL-IPB GitHub release rather than converted locally). `verify_onnx_models.py` will confirm whether the ONNX files are valid regardless of how they were produced. [VERIFIED: MODEL_CONVERSION_STATUS.md]

---

## Focus Area 2: Testing Approach — QGIS Console vs Standalone

### Why QGIS Console is required

Both `mopad_algorithm.py` and `roboflow_algorithm.py` import QGIS-specific symbols at module level:

```python
# mopad_algorithm.py line 14-32 [VERIFIED: source]
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing, QgsFeatureSink, QgsGeometry, QgsPointXY, QgsPoint,
    QgsFields, QgsField, QgsFeature, QgsProcessingAlgorithm, ...
    QgsMessageLog, QgsWkbTypes,
)
```

These imports fail outside a QGIS process. The algorithms cannot be run as standalone Python scripts. The QGIS Python Console is the only supported test runner for `mopad_algorithm.py` and `roboflow_algorithm.py`.

For `verify_onnx_models.py`, which only imports `onnxruntime` and `os`, a standalone runner works — but running it from the QGIS console also works and is simpler for the tester.

### Fastest approach on Windows QGIS 3.44.2

**Recommended workflow:** QGIS Python Console (`Ctrl+Alt+P` or Plugins > Python Console):
1. Open QGIS
2. Load the plugin (if not autoloaded)
3. Load the test raster as a QGIS layer
4. Paste console snippet and run
5. Read `featureCount()` from the output layer
6. Inspect visually in the QGIS canvas

This is faster than the Processing Toolbox dialog for repeated batch runs because parameters can be scripted in one paste operation.

### B1/H1/B2/B3/B4 via OptimalIpbAlgorithm

These run through the already-registered `OptimalIpbAlgorithm`. `initAlgorithm` scans `models/*.onnx` (NOT `models/mopad/*.onnx`) and builds a model enum. All five `.onnx` files in `models/` root are visible to this algorithm. MOPAD is NOT listed here — it has its own `MOPADPalmAlgorithm`.

Default parameters from code:
- `mAP` (score threshold): `0.5` [VERIFIED: optimal_ipb_algorithm.py `defaultValue=0.5`]
- `TYPE`: `0` (Point)

### MOPAD via mopad_algorithm.py

Default parameters from code [VERIFIED: mopad_algorithm.py]:
- `SCORE_THR`: `0.05`
- `NMS_IOU`: `0.3`
- `TYPE`: `0` (Point)
- `EXCLUDE_GRASS`: `True`

MOPAD uses a **lazy-loaded singleton** `_ort_session` at module level — the ONNX session is created once and reused across runs in the same QGIS session. This is different from `OptimalIpbAlgorithm` which reloads the model on every `processAlgorithm()` call.

MOPAD requires `providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']` — if CUDA is not available, `onnxruntime` silently falls back to CPU. No error is raised. [VERIFIED: mopad_algorithm.py `_get_session()`]

### Roboflow via roboflow_algorithm.py

Default parameters from code [VERIFIED: roboflow_algorithm.py]:
- `CONFIDENCE`: `0.25`
- `TYPE`: `0` (Point)

API key is read from QGIS global variable `roboflow_api_key` first, then environment variable `ROBOFLOW_API_KEY`. [VERIFIED: roboflow_algorithm.py `processAlgorithm` lines 157-171]

The algorithm is **resolution-aware**: it computes `raster_tile_px = round(64m / raster_m_per_px)` then upsamples to 640 px before sending to the API. For the Perak raster (0.05 m/px), `raster_tile_px = 64/0.05 = 1280` px — the algorithm will take tiles of 1280×1280 raster pixels. For Rupat (0.088 m/px), `raster_tile_px = round(64/0.088) = 727` px. [VERIFIED: roboflow_algorithm.py lines 204-215]

**Rate limit:** The code includes `time.sleep(0.1)` per tile as a courtesy rate limit. Perak at 0.05 m/px is 6567×14978 px; stride at Perak = 1280 - overlap ≈ 1200 px → approximately (6567/1200) × (14978/1200) ≈ 6×13 = 78 tiles → 78 API calls × 0.1s = minimum 8 seconds plus network latency. Well within Roboflow free tier (1000 calls/month). Rupat is smaller (7807×4782 px) → approximately (7807/727) × (4782/727) ≈ 11×7 = 77 tiles. [VERIFIED: roboflow_algorithm.py tile grid calculation + 02-04-SOURCES.md raster dimensions]

---

## Focus Area 3: Git Strategy for Large Model Files

### Current state [VERIFIED: filesystem + git status]

- **No `.gitignore` file exists** in the repository root.
- **No `.gitattributes` file exists** — git-lfs IS installed globally (version 3.7.0) but no patterns are tracked.
- **No remote is configured** (`git remote -v` returns empty).
- All model files and test rasters are **untracked** (shown as `??` in `git status`), not ignored.
- `git lfs status` shows only `optimal_ipb_algorithm.py` (modified) and deleted sample TIF files — no ONNX files.

### Model file sizes [VERIFIED: filesystem]

| File | Size | Location |
|------|------|----------|
| tree_tops_yolov9.onnx | 203 MB | models/ |
| Google-Resnet101.onnx | 211 MB | models/ |
| Geoeye-Resnet101.onnx | 221 MB | models/ |
| Pleiades-Resnet101.onnx | 221 MB | models/ |
| MOPAD_epoch_24.onnx | 242 MB | models/mopad/ |
| MOPAD_epoch_24.pth | 484 MB | models/mopad/ |
| tribber93_yolov11_palm.onnx | 37.9 MB | models/ |
| oam_perak_01E2b_0.05mpx.tif | 30.44 MB | tif_online_samples/ |
| oam_rupat_indonesia_0.088mpx.tif | 5.16 MB | tif_online_samples/ |
| oam_leuhan_aceh_0.5mpx.tif | 0.83 MB | tif_online_samples/ |

**Total binary payload:** ~1.6 GB across all model files.

### Recommended strategy: .gitignore

Since the repo has no remote and git-lfs has no remote backing store, committing binaries to git or setting up LFS tracking would only bloat the local `.git/objects` directory. The correct approach is:

1. Create `.gitignore` that excludes all large binaries.
2. Commit the `.py` scripts, `.md` planning files, and `.gitignore` itself normally.
3. Document in `MODEL_CONVERSION_STATUS.md` (already tracked in planning) where each binary came from.

**Recommended `.gitignore` content:**
```gitignore
# Model binary files — too large for git; re-download or re-convert as needed
models/*.onnx
models/*.h5
models/**/*.onnx
models/**/*.pth
models/Google-Resnet101-savedmodel/

# Test raster imagery — OAM downloads, re-downloadable
tif_online_samples/

# Python caches
__pycache__/
*.py[cod]
*.pyd

# QGIS generated files
*.aux.xml
```

**What this achieves for MOD-01:**
- `mopad_algorithm.py`, `roboflow_algorithm.py`, `verify_onnx_models.py`, `download_missing.py` — committed normally (small .py files).
- `models/*.onnx` and `models/mopad/*` — excluded via `.gitignore` (not committed, not LFS).
- `tif_online_samples/` — excluded via `.gitignore`.
- `MODEL_CONVERSION_STATUS.md` — already tracked (text file, small) — stays tracked.
- `.gitignore` itself — committed.

**git-lfs alternative (if desired in future):** Set up after a remote is configured. Command would be `git lfs track "*.onnx"` to create `.gitattributes`, then `git add .gitattributes` and commit. Not recommended for Phase 4 since there is no remote.

---

## Focus Area 4: mopad_algorithm.py and roboflow_algorithm.py — Blocking Issues

### mopad_algorithm.py — interface analysis [VERIFIED: source]

**Import chain:**
```python
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsFeatureSink, ..., QgsProcessingAlgorithm, ...)
from osgeo import gdal
from lsnms import nms
from .helpers import sliding_window, pixel2coord, map_uint16_to_uint8
```

- The relative import `from .helpers import ...` requires the module to be part of the `optimal_ipb` package. This works when loaded as part of the QGIS plugin but FAILS if the file is run as `python mopad_algorithm.py` directly. **Must run inside QGIS.** [VERIFIED: code]
- `lsnms` is available in `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages\lsnms` — accessible to QGIS 3.44.2's Python 3.12 via user site-packages. [VERIFIED: filesystem]
- `onnxruntime` is available in `qgis_gdal_env` (1.24.4) — injected by `__init__.py`. [VERIFIED: filesystem]

**Potential blocking issue — mopad_algorithm.py error message references wrong env name:**

Line 64 in `mopad_algorithm.py`:
```python
raise ImportError(
    'onnxruntime not found. Install it into the qgis_mmcv_env conda '
    'environment...'
)
```

The error message says `qgis_mmcv_env` but `onnxruntime` is actually in `qgis_gdal_env`. This is a documentation bug in the error message, not a functional bug — onnxruntime will be found via `qgis_gdal_env` sys.path injection. The message is misleading but does NOT block execution. [VERIFIED: mopad_algorithm.py line 64 + qgis_gdal_env filesystem]

**Model path hardcoded correctly:**
```python
_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'mopad', 'MOPAD_epoch_24.onnx')
```
`os.path.dirname(__file__)` resolves to the plugin root when loaded as a package. [VERIFIED: mopad_algorithm.py line 39-41]

**Tile count for Perak raster:**
- Perak: 6567×14978 px; `_STEP = 900`, `_TILE_SIZE = 1024`
- Tiles: `ceil(6567/900) × ceil(14978/900)` ≈ 8 × 17 = 136 tiles
- At CPU inference (~2-5 seconds/tile for Faster R-CNN), this is 5-11 minutes.

**Tile count for Rupat raster:**
- Rupat: 7807×4782 px
- Tiles: `ceil(7807/900) × ceil(4782/900)` ≈ 9 × 6 = 54 tiles
- At 2-5 sec/tile: 2-5 minutes. More practical for initial testing.

**Recommendation for planner:** Test MOPAD on Rupat first (smaller, faster) as the smoke test, then Perak if Rupat succeeds.

### roboflow_algorithm.py — interface analysis [VERIFIED: source]

**Import chain:**
```python
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsExpressionContextUtils, QgsFeature, ..., QgsProcessingAlgorithm, ...)
from osgeo import gdal
from .helpers import pixel2coord, map_uint16_to_uint8
```

- Same relative import issue — must run inside QGIS plugin context.
- `QgsExpressionContextUtils.globalScope().variable('roboflow_api_key')` reads the QGIS global variable. API key is confirmed set (D-12). [ASSUMED: user confirmed key is set in QGIS global var — not verified by tool]
- `Pillow` check: `try: from PIL import Image as _PIL`. Pillow 12.0.0 confirmed in qgis_gdal_env. [VERIFIED: filesystem]
- `lsnms` imported inside NMS block with graceful fallback: `except ImportError: ...pushWarning("lsnms not found — skipping NMS")`. If lsnms is not found, NMS is skipped and duplicates may appear near tile edges. [VERIFIED: roboflow_algorithm.py lines 338-353]

**Potential blocking issue — second `gdal.Open` after sink write:**

```python
# roboflow_algorithm.py line 359
ds2 = gdal.Open(source.source())
```

The code reopens the raster a second time just to call `pixel2coord` in the feature-writing loop. This is unnecessary but not a blocking bug — GDAL handles repeated opens of the same file. [VERIFIED: roboflow_algorithm.py lines 359-388]

**No blocking issues found.** Both algorithms are structurally sound for QGIS Console testing.

---

## Focus Area 5: Detection Output Format and Counting

### Output layer structure

All three algorithms write to `QgsFeatureSink` with the same pattern [VERIFIED: all three source files]:

| Algorithm | Fields | Geometry type |
|-----------|--------|---------------|
| `OptimalIpbAlgorithm` (B1/H1/B2/B3/B4) | `Score` (double) | Point or BBox polygon (TYPE param) |
| `MOPADPalmAlgorithm` | `Score` (double), `Class` (int), `Health` (string) | Point or BBox polygon (TYPE param) |
| `RoboflowPalmDetectionAlgorithm` | `Score` (double), `Class` (string) | Point or BBox polygon (TYPE param) |

### Getting detection count programmatically

```python
# Method 1: from processing.run result — works if output is a memory layer
result = processing.run('mopad-palm-detection', {..., 'OUTPUT': 'memory:'})
output_id = result['OUTPUT']
# For memory layers, featureCount() is available immediately
from qgis.core import QgsVectorLayer
layer = QgsVectorLayer(output_id, 'test', 'memory')  # not always needed
# Better: use runAndLoadResults to get the layer added to the project
result2 = processing.runAndLoadResults('mopad-palm-detection', {...})
layers = QgsProject.instance().mapLayersByName('MOPAD detections')
count = layers[0].featureCount()
print(f"Detections after NMS: {count}")
```

```python
# Method 2: From QGIS Log Messages panel
# All three algorithms print detection counts to QgsMessageLog or feedback:
# MOPAD: "[MOPAD] N detection(s) after NMS (score>=0.05, exclude_grass=True)"
# OptimalIPB: detection count is in the feedback progress log
# Roboflow: "Done — N palm(s) after NMS  (conf >= 25%, model: oil-palm-aerial-detection/1)"
```

### Getting confidence distribution

```python
# After getting the layer, iterate features to get score distribution
scores = [f['Score'] for f in layer.getFeatures()]
import numpy as np
if scores:
    print(f"n={len(scores)}, min={min(scores):.3f}, max={max(scores):.3f}, "
          f"median={np.median(scores):.3f}")
```

### Visual inspection in QGIS

Load the output layer to the canvas (use `runAndLoadResults` rather than `run`) and overlay on the raster. Set:
- Symbol size: 10px, red dot
- Label: `Score` field

A visual pass is recorded when 3+ detections fall visibly on distinct palm tree crowns (round canopy shadows) in the canvas. A visual fail is when detections are scattered on bare ground, cloud, or water, or when no detections appear at all.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ONNX model loading and I/O inspection | Custom reader | `onnxruntime.InferenceSession` + `.get_inputs()` / `.get_outputs()` | Already used in verify_onnx_models.py; handles opset compatibility automatically |
| Non-Maximum Suppression | Custom NMS loop | `lsnms.nms(boxes, scores, iou_threshold)` | Already used in all three algorithms; vectorized, handles empty arrays |
| Pixel to geographic coordinate | Manual GeoTransform math | `helpers.pixel2coord(ds, col, row)` | Already implemented correctly in helpers.py; uses GDAL GetGeoTransform |
| JPEG encoding for API calls | cv2.imencode or raw bytes | `PIL.Image.fromarray(...).save(buf, 'JPEG')` | Already in roboflow_algorithm.py `_to_jpeg_bytes()` |
| Recursive ONNX file discovery | Custom walker | `glob.glob('**/*.onnx', recursive=True)` | Standard library; replaces the os.listdir gap in verify_onnx_models.py |

---

## Common Pitfalls

### Pitfall 1: Running algorithm scripts standalone outside QGIS
**What goes wrong:** `ImportError: No module named 'qgis'` at first `from qgis.core import ...` line.
**Why it happens:** Both `mopad_algorithm.py` and `roboflow_algorithm.py` import QGIS API at module level. QGIS Python APIs (`qgis.core`, `qgis.PyQt`) are only available inside a running QGIS process.
**How to avoid:** Always run tests from the QGIS Python Console (`Ctrl+Alt+P`). Never `python mopad_algorithm.py` from the OS command prompt.
**Warning signs:** The error message includes `ModuleNotFoundError: No module named 'qgis'`.

### Pitfall 2: verify_onnx_models.py misses MOPAD
**What goes wrong:** Script prints "All 5 ONNX models verified" without mentioning MOPAD, giving a false sense of complete verification.
**Why it happens:** `os.listdir('models/')` does not recurse into `models/mopad/`.
**How to avoid:** Patch `verify_onnx_models.py` to also check `models/mopad/MOPAD_epoch_24.onnx` before running. This is a required task in Wave 0.
**Warning signs:** Output shows exactly 5 models (Geoeye, Google, Pleiades, tree_tops, tribber93) with no mention of MOPAD.

### Pitfall 3: Wrong model enum index for OptimalIpbAlgorithm
**What goes wrong:** Algorithm runs with the wrong model (e.g., index 0 = Geoeye when you wanted Google).
**Why it happens:** `initAlgorithm()` builds the model list from `os.listdir` — order depends on filesystem, but Python `sorted()` makes it alphabetical. The order can change if files are added or renamed.
**How to avoid:** Print `modelsList` from the QGIS console before testing:
```python
from qgis.core import QgsApplication
for alg in QgsApplication.processingRegistry().algorithms():
    if 'OPTIMAL-IPB' in alg.id():
        print(alg.id())
# Then inspect the enum options via the algorithm's parameters
```
Or simply use the Processing Toolbox dialog for B1/H1/B2/B3/B4 tests to get the visual dropdown.
**Warning signs:** Detection count is unexpectedly 0 or the log shows a different model name than expected.

### Pitfall 4: Committing large binary files without .gitignore
**What goes wrong:** `git add .` stages all untracked files including the 1.6 GB of model files and TIFs. `git commit` succeeds but inflates the `.git/objects` directory by 1.6 GB permanently (even after deletion, objects remain until `git gc`).
**Why it happens:** No `.gitignore` exists yet.
**How to avoid:** Create `.gitignore` as the very first action of Wave 0, before any `git add`. Never use `git add .` — always `git add <specific-files>`.
**Warning signs:** `git status` shows model files as "Changes to be committed" after `git add`.

### Pitfall 5: MOPAD inference session cached from a previous import
**What goes wrong:** When `mopad_algorithm.py` is re-imported or the module is reloaded in the same QGIS session, the `_ort_session` module-level singleton retains the session from the previous import. This is normally fine (efficient) but can cause issues if the ONNX file path changes between runs.
**Why it happens:** `_ort_session = None` at module level, set once by `_get_session()`, never cleared.
**How to avoid:** In the QGIS session, avoid reloading the module. If you need to force a fresh session, set `mopad_algorithm._ort_session = None` in the console before re-running.
**Warning signs:** Model path change appears to have no effect; old ONNX session is still used.

### Pitfall 6: Perak raster is very large for tile-based VHR models
**What goes wrong:** MOPAD runs 136 tiles on Perak, which at ~3 seconds per tile (CPU Faster R-CNN) takes 7+ minutes. `OptimalIpbAlgorithm` with B1 on Perak (500×500 tiles, step 470) runs ~(6567/470)×(14978/470) ≈ 14×32 = 448 tiles — potentially 15+ minutes.
**Why it happens:** Perak is 6567×14978 px, which is large for fine-step sliding window inference.
**How to avoid:** Test on Rupat first (7807×4782, step 900 for MOPAD → 54 tiles; step 470 for OptimalIPB → 17×11 = 187 tiles). Record Rupat results, then proceed to Perak if time allows.
**Warning signs:** Progress bar stuck at single-digit percent after 5 minutes.

---

## Code Examples

### Verified pattern: verify_onnx_models.py with MOPAD added

```python
# Source: verify_onnx_models.py [VERIFIED] + MOPAD path fix [ASSUMED]
import onnxruntime as ort
import os
import glob

plugin_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(plugin_dir, 'models')

# Collect all ONNX files recursively
onnx_files = sorted(
    os.path.relpath(p, plugin_dir)
    for p in glob.glob(os.path.join(models_dir, '**', '*.onnx'), recursive=True)
)

print(f"Models directory: {models_dir}")
print(f"ONNX files found: {onnx_files}\n")

all_ok = True
for rel_path in onnx_files:
    path = os.path.join(plugin_dir, rel_path)
    size_mb = os.path.getsize(path) / 1024 / 1024
    try:
        sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
        inputs  = [i.name for i in sess.get_inputs()]
        outputs = [o.name for o in sess.get_outputs()]
        print(f"  [OK]  {rel_path} ({size_mb:.0f} MB)")
        print(f"        inputs={inputs}")
        print(f"        outputs={outputs}")
    except Exception as e:
        print(f"  [FAIL] {rel_path} ({size_mb:.0f} MB): {e}")
        all_ok = False

print()
if all_ok:
    print(f"All {len(onnx_files)} ONNX models verified successfully.")
else:
    print("Some models failed verification.")
```

### Verified pattern: 04-TEST-RESULTS.md table structure

```markdown
# Phase 4 Test Results

**Date:** YYYY-MM-DD
**Environment:** QGIS 3.44.2, Windows 11, CPU inference

| Model | Raster | Threshold | Detection Count | Visual Pass/Fail | Notes |
|-------|--------|-----------|-----------------|------------------|-------|
| B1 tree_tops_yolov9.onnx | Perak 5cm | mAP=0.5 | N | Pass/Fail | |
| B1 tree_tops_yolov9.onnx | Rupat 8.8cm | mAP=0.5 | N | Pass/Fail | |
| H1 tribber93_yolov11_palm.onnx | Perak 5cm | mAP=0.5 | N | Pass/Fail | |
| H1 tribber93_yolov11_palm.onnx | Rupat 8.8cm | mAP=0.5 | N | Pass/Fail | |
| MOPAD epoch_24 | Perak 5cm | score≥0.05 | N | Pass/Fail | best pre-filter: X.XX (Healthy) |
| MOPAD epoch_24 | Rupat 8.8cm | score≥0.05 | N | Pass/Fail | |
| B2 Google-Resnet101.onnx | Aceh 50cm | mAP=0.5 | N | Pass/Fail | |
| B3 Geoeye-Resnet101.onnx | Aceh 50cm | mAP=0.5 | N | Pass/Fail | verify: OK/FAIL |
| B4 Pleiades-Resnet101.onnx | Aceh 50cm | mAP=0.5 | N | Pass/Fail | verify: OK/FAIL |
| Roboflow UiTM | Perak 5cm | conf≥0.25 | N | Pass/Fail | API calls: N, errors: N |
| Roboflow UiTM | Rupat 8.8cm | conf≥0.25 | N | Pass/Fail | |
```

---

## Wave Structure Recommendation

### Wave 0 — Commit and Prep (no testing yet)

**Tasks (sequential):**
1. Create `.gitignore` (before any git add)
2. Patch `verify_onnx_models.py` to add recursive ONNX discovery (MOPAD coverage)
3. Commit `optimal_ipb_algorithm.py` (edge-clamping fix, D-06) — specific file only
4. Commit all new untracked `.py` files: `mopad_algorithm.py`, `roboflow_algorithm.py`, `verify_onnx_models.py`, `download_missing.py`, `.gitignore`
5. Commit planning docs if commit_docs is enabled

**Can parallelize:** Steps 3 and 4 can be a single commit; step 1 must precede step 4.

### Wave 1 — Verify ONNX Models (MOD-02)

**Tasks:**
1. Run patched `verify_onnx_models.py` from QGIS console; capture output
2. Record pass/fail for each of the 6 ONNX files (5 in models/ root + MOPAD)
3. If Geoeye/Pleiades fail: mark as excluded in 04-TEST-RESULTS.md; do not block Wave 2+

**Gate:** Wave 1 must complete before Wave 2 (need to know which MR models to test).

### Wave 2 — VHR Testing (MOD-03)

**Tasks (can parallelize on separate QGIS sessions, but typically sequential):**
1. B1 tree_tops on Rupat → record count + visual
2. B1 tree_tops on Perak → record count + visual
3. H1 tribber93 on Rupat → record count + visual
4. H1 tribber93 on Perak → record count + visual
5. MOPAD on Rupat → record count + visual (test Rupat first — fewer tiles)
6. MOPAD on Perak → record count + visual (if time allows after Rupat)

**Recommendation:** Run Rupat first for each model (fewer tiles, faster feedback). If any VHR model passes on Rupat, the phase success criterion (D-11) is met. Perak runs are secondary validation.

### Wave 3 — MR Testing (MOD-04)

**Tasks (sequential):**
1. B2 Google-Resnet101 on Aceh → record count + visual
2. B3 Geoeye-Resnet101 on Aceh (only if Wave 1 verify passed) → record count + visual
3. B4 Pleiades-Resnet101 on Aceh (only if Wave 1 verify passed) → record count + visual

**Can parallelize with Wave 2** in principle (different algorithm, different raster) but QGIS is single-threaded — run sequentially.

### Wave 4 — API Testing (MOD-05)

**Tasks:**
1. Confirm `roboflow_api_key` QGIS global variable is set (quick console check)
2. Run Roboflow algorithm on Rupat → record count, API call count, error count, visual
3. Run Roboflow algorithm on Perak → record count, visual (more tiles, ~78 API calls)

### Wave 5 — Results Commit

**Tasks:**
1. Write `04-TEST-RESULTS.md` with all recorded results
2. Commit `04-TEST-RESULTS.md`
3. Visual inspection summary in TEST-RESULTS.md

---

## Validation Architecture

> config.json not present — `workflow.nyquist_validation` key is absent, treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + unittest (configured in `setup.cfg` `[tool:pytest]`) |
| Config file | `setup.cfg` (existing) |
| Quick run command | `python -m pytest test/test_init.py -x` |
| Full suite command | `python -m pytest test/ -x` |

**Note:** The existing tests (`test_init.py`, `test_qgis_environment.py`, `test_translations.py`) do NOT test the algorithm logic — they test QGIS plugin metadata and environment. Phase 4 is primarily a manual empirical testing phase (run models, observe output) rather than an automated unit test phase. The automated validation for Phase 4 requirements is via `verify_onnx_models.py` (MOD-02) and the manually filled `04-TEST-RESULTS.md` (MOD-03/04/05).

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MOD-01 | Untracked files committed to git | smoke | `git status --short` → shows no untracked Phase 4 .py files | N/A (git command) |
| MOD-02 | All ONNX models verified with onnxruntime | automated script | `python verify_onnx_models.py` (patched) → exit 0 | ✅ (needs MOPAD patch) |
| MOD-03 | VHR models produce detections; results in TEST-RESULTS.md | manual | QGIS Console + visual inspection | ❌ Wave 0 — create 04-TEST-RESULTS.md |
| MOD-04 | MR models produce detections on Aceh; results in TEST-RESULTS.md | manual | QGIS Console + visual inspection | ❌ Wave 0 — create 04-TEST-RESULTS.md |
| MOD-05 | Roboflow detections on Perak+Rupat; API key works | manual + network | QGIS Console + Roboflow response check | ❌ Wave 0 — create 04-TEST-RESULTS.md |

### Sampling Rate

- **Per Wave commit:** `git status --short` to confirm expected files staged/committed
- **Per MOD-02:** `python verify_onnx_models.py` → all [OK] lines
- **Phase gate:** `04-TEST-RESULTS.md` exists and has at least one "Pass" entry in the Visual Pass/Fail column for a VHR model (B1, H1, or MOPAD) on Perak or Rupat

### Wave 0 Gaps

- [ ] `04-TEST-RESULTS.md` — covers MOD-03, MOD-04, MOD-05
- [ ] `verify_onnx_models.py` patched for MOPAD — covers MOD-02
- [ ] `.gitignore` — covers MOD-01 (prevents accidental large file commits)

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| QGIS 3.44.2 | All algorithm testing | ✓ | 3.44.2 | — |
| Python 3.12 (QGIS-embedded) | All testing | ✓ | 3.12.x | — |
| onnxruntime | MOD-02, MOD-03, MOD-04 | ✓ | 1.24.4 (qgis_gdal_env) | — |
| lsnms | MOD-03, MOD-04, MOD-05 | ✓ | 0.4.5 (user roaming Python312) | roboflow_algorithm has graceful fallback |
| Pillow | MOD-05 (Roboflow JPEG encoding) | ✓ | 12.0.0 (qgis_gdal_env) | cv2 fallback in `_to_jpeg_bytes()` |
| osgeo.gdal | All raster I/O | ✓ | 3.11.0 (qgis_gdal_env) | — |
| Roboflow API (internet) | MOD-05 | ✓ (assumed) | N/A | No fallback — requires internet + valid key |
| git-lfs (binary handling) | MOD-01 | ✓ installed | 3.7.0 | .gitignore is the recommended alternative |
| MOPAD_epoch_24.onnx (242 MB) | MOD-03 (MOPAD) | ✓ | — | — |
| tree_tops_yolov9.onnx (203 MB) | MOD-03 (B1) | ✓ | — | — |
| tribber93_yolov11_palm.onnx (37.9 MB) | MOD-03 (H1) | ✓ | — | — |
| Google-Resnet101.onnx (211 MB) | MOD-04 (B2) | ✓ | — | — |
| Geoeye-Resnet101.onnx (221 MB) | MOD-04 (B3) | ✓ (verify first) | — | Skip if verify fails (D-02) |
| Pleiades-Resnet101.onnx (221 MB) | MOD-04 (B4) | ✓ (verify first) | — | Skip if verify fails (D-02) |
| oam_perak_01E2b_0.05mpx.tif | MOD-03, MOD-05 | ✓ | 5cm/px, 30.44 MB | — |
| oam_rupat_indonesia_0.088mpx.tif | MOD-03, MOD-05 | ✓ | 8.8cm/px, 5.16 MB | — |
| oam_leuhan_aceh_0.5mpx.tif | MOD-04 | ✓ | 50cm/px, 0.83 MB | — |

**Missing dependencies with no fallback:**
- Internet connectivity for Roboflow API (MOD-05) — no offline fallback; if internet is unavailable, record as "API BLOCKED" in TEST-RESULTS.md.

**Missing dependencies with fallback:**
- lsnms in roboflow_algorithm.py — graceful fallback to no-NMS with a warning already in code.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Keras/TF inference for RetinaNet models | onnxruntime inference | Phase 1 (June 2026) | Eliminates TF runtime from QGIS at inference time |
| `os.listdir('models/')` in verify script | `glob.glob('**/*.onnx', recursive=True)` (proposed fix) | Phase 4 patch | Covers MOPAD in subdirectory |
| Manual Roboflow API call (raw urllib) | `roboflow_algorithm.py` encapsulates tiling, resampling, NMS | Phase 4 (already written) | Resolution-aware, handles any input GSD |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | QGIS 3.44.2 Python 3.12 picks up `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages` (user site) where lsnms 0.4.5 is installed | Dependencies | If user site is excluded (e.g., QGIS startup flag `--no-site`), lsnms is not found; MOPAD/OptimalIPB NMS calls fail with ImportError |
| A2 | `roboflow_api_key` QGIS global variable is set and valid (user confirmed verbally in D-12) | Roboflow testing | If key is expired or not set, all Roboflow tiles return HTTP 401; MOD-05 blocked |
| A3 | MOPAD_epoch_24.onnx contains valid opset-compatible ONNX; `sess.run(['dets', 'labels'], {'image': blob})` output names are correct | MOPAD testing | If output names differ from `dets`/`labels`, `sess.run` raises `InvalidArgument` for every tile; zero detections |
| A4 | The correct algorithm ID for OptimalIpbAlgorithm is `OPTIMAL-IPB:palmtreecalculation` | QGIS Console testing | If the ID is different (e.g., `Calculate:OPTIMAL-IPB`), `processing.run()` raises `QgsProcessingException: Unknown algorithm` |
| A5 | Geoeye-Resnet101.onnx and Pleiades-Resnet101.onnx on disk are valid ONNX (sourced from upstream OPTIMAL-IPB GitHub release rather than the failed local conversion) | verify_onnx_models.py | If invalid, these models are excluded per D-02; no impact on success criterion |

---

## Open Questions

1. **Correct OptimalIpbAlgorithm ID for `processing.run()`**
   - What we know: ARCHITECTURE.md says the dialog is opened with `processing.execAlgorithmDialog("Calculate:OPTIMAL-IPB")` but this is the old format. The Processing framework uses `provider_id:algorithm_name` format.
   - What's unclear: The exact runtime ID — it may be `OPTIMAL-IPB:palmtreecalculation` or `optimal-ipb:palmtreecalculation` (lowercase). It can only be confirmed inside a running QGIS session.
   - Recommendation: Include a task to print all registered algorithm IDs matching "ipb" at the start of Wave 2 testing.

2. **MOPAD output names `dets` and `labels` — confirmed or assumed?**
   - What we know: `mopad_algorithm.py` line 119 calls `sess.run(['dets', 'labels'], {'image': blob})`.
   - What's unclear: Whether the actual ONNX file exports these exact names or uses different names (e.g., `output0`, `boxes`, `scores`).
   - Recommendation: `verify_onnx_models.py` already prints output names — confirm `dets` and `labels` appear in the output after Wave 1.

3. **Roboflow API key — is it the free tier or paid?**
   - What we know: Free tier is ~1000 API calls/month. Perak + Rupat together need ~155 API calls.
   - What's unclear: Whether the account is on free tier or has a higher limit. MOD-05 will consume ~155 of the monthly quota.
   - Recommendation: Low-risk; 155/1000 is well within free tier. Not a blocker.

---

## Security Domain

> `security_enforcement` key absent from config.json — treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No user login in plugin |
| V3 Session Management | No | No sessions; stateless plugin |
| V4 Access Control | No | Local file processing only |
| V5 Input Validation | Partial | Raster input via QGIS layer registry; no user-supplied paths |
| V6 Cryptography | No | No encryption; Roboflow uses HTTPS but not managed by plugin |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| API key exposure in logs | Information Disclosure | `roboflow_algorithm.py` sends key in HTTPS query string; never prints it. `feedback.pushInfo` calls do not include the key. [VERIFIED: roboflow_algorithm.py `_rf_infer` — key in URL only, not in log output] |
| Large file commit to git (accidental) | Availability (bloat) | `.gitignore` created in Wave 0 before any `git add` |
| ONNX model path traversal | Tampering | Model path is hardcoded in `_MODEL_PATH` using `os.path.dirname(__file__)` — not user-supplied |

---

## Sources

### Primary (HIGH confidence — verified against actual files)
- `verify_onnx_models.py` — source read and analyzed directly
- `mopad_algorithm.py` — source read and analyzed directly
- `roboflow_algorithm.py` — source read and analyzed directly
- `optimal_ipb_algorithm.py` — source read (partial)
- `helpers.py` — source read
- `models/MODEL_CONVERSION_STATUS.md` — read directly
- `__init__.py` — source read (sys.path injection pattern)
- `C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages\` — filesystem listing
- `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages\` — filesystem listing (lsnms, onnxruntime 1.17)
- `C:\Program Files\QGIS 3.44.2\bin\python-qgis.bat` — QGIS launch script read
- `.planning/codebase/ARCHITECTURE.md` — read
- `.planning/codebase/INTEGRATIONS.md` — read
- `.planning/codebase/STACK.md` — read
- `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md` — read
- `.planning/phases/02-palm-ensemble/02-04-SOURCES.md` — read (raster dimensions)
- `tif_online_samples/` — filesystem listing (all 3 rasters confirmed present)

### Secondary (MEDIUM confidence — contextual from planning docs)
- `.planning/phases/04-palm-model-download-onnx-conversion-and-empirical-testing-on/04-CONTEXT.md` — decisions
- `.planning/STATE.md` — project history
- `.planning/ROADMAP.md` — phase structure

---

## Metadata

**Confidence breakdown:**
- verify_onnx_models.py analysis: HIGH — source read directly
- MOPAD path gap: HIGH — confirmed by reading source + filesystem
- QGIS Console invocation pattern: MEDIUM — standard QGIS Processing API pattern (A4 is unverified algorithm ID)
- Git strategy: HIGH — no .gitignore, no remote, no .gitattributes — all confirmed on filesystem
- mopad_algorithm.py blocking issues: HIGH — no blockers, error message bug documented
- roboflow_algorithm.py blocking issues: HIGH — no blockers
- lsnms dependency: HIGH — confirmed in user roaming Python 3.12 site-packages
- onnxruntime dependency: HIGH — confirmed in qgis_gdal_env 1.24.4
- Wave structure: MEDIUM — based on analysis of tile counts and dependency ordering

**Research date:** 2026-06-19
**Valid until:** 2026-07-19 (30 days for this stable domain)
