<!-- refreshed: 2026-06-12 -->
# Architecture

**Analysis Date:** 2026-06-12

## System Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                        QGIS 3.x Host Application                     │
│   classFactory(__init__.py) → OptimalIpbPlugin(optimal_ipb.py)       │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ initGui() / initProcessing()
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│               Processing Provider Layer                               │
│        OptimalIpbProvider  (optimal_ipb_provider.py)                 │
│        id="OPTIMAL-IPB"  registered via QgsApplication               │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ loadAlgorithms()
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│               Algorithm Layer                                         │
│        OptimalIpbAlgorithm  (optimal_ipb_algorithm.py)               │
│        - initAlgorithm()  — declare params, scan models/ for .h5     │
│        - processAlgorithm() — sliding-window inference loop          │
└──────┬────────────────────────────────────────────┬──────────────────┘
       │                                            │
       ▼                                            ▼
┌──────────────────────┐              ┌─────────────────────────────┐
│  Raster I/O Layer    │              │  Inference Sub-package       │
│  osgeo/GDAL          │              │  keras_retinanet/            │
│  - gdal.Open()       │              │  - models/__init__.py        │
│  - ds.ReadAsArray()  │              │    load_model() via tf_keras  │
│  - GetGeoTransform() │              │  - utils/image.py            │
└──────────────────────┘              │    preprocess_image()        │
                                      │    resize_image()            │
                                      │  - layers/ (custom Keras)    │
                                      │  - backend/backend.py (TF)   │
                                      └──────────────┬──────────────┘
                                                     │
                                                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Model Store  (models/)                          │
│   Google-Resnet101.h5         — Keras 2 HDF5 weights (inference)     │
│   Google-Resnet101.onnx       — ONNX export (conversion complete)    │
│   Google-Resnet101-savedmodel/ — TF SavedModel format                │
└──────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Post-processing Layer                               │
│   helpers.py            — sliding_window(), pixel2coord(),           │
│                           map_uint16_to_uint8(), non_max_suppression  │
│   lsnms.nms()           — vectorised NMS replacing manual impl       │
└──────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   QGIS Vector Output Layer                            │
│   QgsFeatureSink / QgsFeature                                        │
│   Geometry types: Point | Polygon (BBox) | Circle                    │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `classFactory` | QGIS plugin entry point; injects Conda env into `sys.path` | `__init__.py` |
| `OptimalIpbPlugin` | Plugin lifecycle: register/unregister provider, add toolbar icon | `optimal_ipb.py` |
| `OptimalIpbProvider` | QGIS Processing provider; holds algorithm registry | `optimal_ipb_provider.py` |
| `OptimalIpbAlgorithm` | Algorithm definition, parameter declaration, inference orchestration | `optimal_ipb_algorithm.py` |
| `detect_palm()` | Per-tile inference: reads tile, normalises, runs model, collects raw bboxes | `optimal_ipb_algorithm.py:88` |
| `helpers.py` | Utility functions: sliding window, pixel→geo coordinate transform, NMS, uint16→uint8 normalisation | `helpers.py` |
| `keras_retinanet/models/__init__.py` | `load_model()` — loads `.h5` via `tf_keras` with custom objects; `backbone()` factory | `keras_retinanet/models/__init__.py` |
| `keras_retinanet/models/resnet.py` | `ResNetBackbone` class; builds ResNet50/101/152 + RetinaNet head | `keras_retinanet/models/resnet.py` |
| `keras_retinanet/models/retinanet.py` | FPN head, classification/regression submodels, `retinanet_bbox` | `keras_retinanet/models/retinanet.py` |
| `keras_retinanet/layers/` | Custom Keras layers: `Anchors`, `RegressBoxes`, `UpsampleLike`, `ClipBoxes`, `FilterDetections` | `keras_retinanet/layers/` |
| `keras_retinanet/backend/backend.py` | TF-level ops: `bbox_transform_inv`, `shift`, `map_fn`, `resize_images` | `keras_retinanet/backend/backend.py` |
| `keras_retinanet/utils/image.py` | `preprocess_image()` (ImageNet mean subtraction), `resize_image()` (min_side=800) | `keras_retinanet/utils/image.py` |
| `keras_retinanet/utils/anchors.py` | Anchor generation, `AnchorParameters.default` (sizes 32–512, strides 8–128) | `keras_retinanet/utils/anchors.py` |
| `keras_retinanet/utils/compute_overlap.py` | Pure-NumPy IoU (fallback; `.pyx` Cython variants present for py3.7 and py3.12) | `keras_retinanet/utils/compute_overlap.py` |

## Pattern Overview

**Overall:** QGIS Processing Plugin — Provider/Algorithm pattern

**Key Characteristics:**
- Follows the standard QGIS Processing framework: one `QgsProcessingProvider` registers one or more `QgsProcessingAlgorithm` subclasses.
- Inference is synchronous and blocking inside `processAlgorithm()` — no threading. The QGIS feedback/cancel mechanism (`feedback.isCanceled()`) is polled per tile.
- The `keras_retinanet/` sub-package is a bundled vendored copy of the Fizyr keras-retinanet library, modified to support `tf_keras` and Python 3.12.
- Model loading occurs at the start of each `processAlgorithm()` call (not cached between runs).
- Raw detection results accumulate in **module-level global lists** (`bboxes`, `scoreses` at `optimal_ipb_algorithm.py:76–77`) and are cleared after each run.

## Layers

**QGIS Plugin Lifecycle Layer:**
- Purpose: Satisfy QGIS plugin protocol (`classFactory`, `initGui`, `unload`)
- Location: `__init__.py`, `optimal_ipb.py`
- Contains: Plugin class, Conda `sys.path` injection, toolbar action
- Depends on: `qgis.core`, `qgis.PyQt`
- Used by: QGIS application loader

**Processing Provider Layer:**
- Purpose: Expose algorithms to the QGIS Processing Toolbox
- Location: `optimal_ipb_provider.py`
- Contains: `OptimalIpbProvider(QgsProcessingProvider)`
- Depends on: `optimal_ipb_algorithm.py`
- Used by: `OptimalIpbPlugin.initProcessing()`

**Algorithm Layer:**
- Purpose: Define user-facing parameters, drive the sliding-window inference loop, write vector output
- Location: `optimal_ipb_algorithm.py`
- Contains: `OptimalIpbAlgorithm`, `detect_palm()`, `minmax` dataclass, `geom_type()` switcher, global bbox accumulators
- Depends on: `keras_retinanet/`, `helpers.py`, `osgeo.gdal`, `lsnms`, `numpy`, `pandas`
- Used by: `OptimalIpbProvider.loadAlgorithms()`

**Inference Sub-package Layer:**
- Purpose: Model architecture definition, weight loading, image preprocessing, custom Keras layer implementations
- Location: `keras_retinanet/`
- Contains: Backbone classes, FPN head, custom layers, anchor utilities, image utilities
- Depends on: `tensorflow`, `tf_keras` (primary) / `tensorflow.keras` (fallback), `keras_resnet`, `cv2`, `PIL`
- Used by: `OptimalIpbAlgorithm.processAlgorithm()`

**Utility/Helper Layer:**
- Purpose: Stateless geometric and image processing utilities
- Location: `helpers.py`
- Contains: `sliding_window`, `pixel2coord`, `map_uint16_to_uint8`, `format_img`, `non_max_suppression_fast`
- Depends on: `numpy` only
- Used by: `optimal_ipb_algorithm.py`

## Data Flow

### Primary Inference Path

1. User triggers algorithm via QGIS dialog or console → `processing.execAlgorithmDialog("Calculate:OPTIMAL-IPB")` (`optimal_ipb.py:78`)
2. `OptimalIpbAlgorithm.initAlgorithm()` scans `models/` for `.h5` files and populates the model enum (`optimal_ipb_algorithm.py:174–176`)
3. `OptimalIpbAlgorithm.processAlgorithm()` loads the selected model via `load_model(path, backbone_name='resnet101')` (`optimal_ipb_algorithm.py:243`)
4. `load_model()` calls `tf_keras.models.load_model()` with custom object dict built by `ResNetBackbone` (`keras_retinanet/models/__init__.py:86–91`)
5. GDAL opens the input raster; per-band 2nd/98th percentile min/max values computed for uint16→uint8 normalisation (`optimal_ipb_algorithm.py:254–259`)
6. `sliding_window(width, height, stepSize=470)` generates `(x, y)` offsets for 500×500 pixel tiles (`helpers.py:3–6`)
7. For each tile, `detect_palm(model, ds, x, y, 500, 500, minmaxlist, mAP_val)` is called (`optimal_ipb_algorithm.py:284`)
8. Inside `detect_palm()`: `ds.ReadAsArray()` reads raw pixels; bands reordered to BGR; `map_uint16_to_uint8()` applied if not uint8; `preprocess_image()` subtracts ImageNet means; `resize_image()` rescales to min_side=800 (`optimal_ipb_algorithm.py:88–113`)
9. `model.predict_on_batch()` runs forward pass; returns `boxes, scores, labels` (`optimal_ipb_algorithm.py:110`)
10. Boxes are rescaled by `scale`, filtered by score threshold; pixel-space coordinates offset by tile `(x, y)` and appended to global `bboxes` / `scoreses` lists (`optimal_ipb_algorithm.py:112–135`)
11. After all tiles: `lsnms.nms(bboxeses, flatten_score, iou_threshold=0.3)` performs global NMS (`optimal_ipb_algorithm.py:291`)
12. Surviving boxes converted from pixel to geographic coordinates via `pixel2coord(ds, xc, yc)` using GDAL `GetGeoTransform()` (`helpers.py:68–73`)
13. Each detection emitted to `QgsFeatureSink` as Point, Polygon (bbox), or Circle depending on `TYPE` parameter (`optimal_ipb_algorithm.py:330–343`)
14. Global lists cleared; `{OUTPUT: dest_id}` returned to QGIS (`optimal_ipb_algorithm.py:345–348`)

### Model Loading Detail

1. `load_model(filepath, backbone_name='resnet101')` called in `keras_retinanet/models/__init__.py:70`
2. Tries `import tf_keras as keras`; falls back to `from tensorflow import keras` if tf_keras absent
3. `backbone('resnet101')` constructs `ResNetBackbone` which populates `custom_objects` with `UpsampleLike`, `PriorProbability`, `RegressBoxes`, `FilterDetections`, `Anchors`, `ClipBoxes`, `_smooth_l1`, `_focal`
4. `keras.models.load_model(filepath, custom_objects=...)` deserialises the `.h5` file

**State Management:**
- Module-level mutable globals: `bboxes = []`, `scoreses = []`, `modelsList = []` declared at `optimal_ipb_algorithm.py:76–78`. `bboxes` and `scoreses` are cleared at the end of each `processAlgorithm()` call. `modelsList` is rebuilt each `initAlgorithm()` call.
- No persistent state between plugin sessions beyond loaded model in memory (model is reloaded on each run).

## Key Abstractions

**`OptimalIpbAlgorithm` (QgsProcessingAlgorithm subclass):**
- Purpose: Encapsulates the full palm detection workflow as a QGIS Processing algorithm
- Examples: `optimal_ipb_algorithm.py:145`
- Pattern: Template Method — QGIS framework calls `initAlgorithm()` then `processAlgorithm()`

**`Backbone` (abstract base class):**
- Purpose: Defines interface for all backbone architectures (retinanet builder, ImageNet download, preprocessing)
- Examples: `keras_retinanet/models/__init__.py:5`, concrete: `keras_retinanet/models/resnet.py:26`
- Pattern: Abstract Factory — `backbone(name)` returns correct subclass

**`detect_palm()` (module-level function):**
- Purpose: Encapsulates single-tile inference including normalisation, preprocessing, model call, bbox accumulation
- Examples: `optimal_ipb_algorithm.py:88`
- Pattern: Procedure with side effects on module globals — not a pure function

## Entry Points

**QGIS Plugin Entry:**
- Location: `__init__.py:45` — `classFactory(iface)`
- Triggers: QGIS plugin loader at startup
- Responsibilities: Conda env path injection, instantiate `OptimalIpbPlugin`

**Processing Algorithm Entry:**
- Location: `optimal_ipb_algorithm.py:169` — `initAlgorithm(config)`
- Triggers: QGIS Processing Toolbox initialisation
- Responsibilities: Scan `models/` for `.h5` files, declare input/output parameters

**Inference Entry:**
- Location: `optimal_ipb_algorithm.py:234` — `processAlgorithm(parameters, context, feedback)`
- Triggers: User clicks "Run" in the algorithm dialog
- Responsibilities: Load model, open raster, run sliding-window loop, apply NMS, write vector output

## Architectural Constraints

- **Threading:** Single-threaded. Inference runs synchronously on the QGIS main thread inside `processAlgorithm()`. The only concurrency hook is `feedback.isCanceled()` polled per tile.
- **Global state:** `bboxes`, `scoreses`, `modelsList` are module-level lists in `optimal_ipb_algorithm.py`. This makes the algorithm non-reentrant — concurrent runs from two algorithm instances would corrupt results.
- **Model discovery:** Only `.h5` files in `models/` are listed in the UI enum (`initAlgorithm` line 175–177). The `.onnx` and SavedModel formats are present on disk but not yet wired into the algorithm.
- **Keras version pinning:** `load_model()` explicitly prefers `tf_keras` (Keras 2 legacy API) over `tensorflow.keras` (Keras 3) because the `.h5` weights were saved with Keras 2. This is documented in a comment at `keras_retinanet/models/__init__.py:86`.
- **Conda path injection:** The absolute path `C:\Users\suily\miniconda3\envs\qgis_gdal_env` is hard-coded in `__init__.py:34`. This breaks portability to any other machine.
- **Circular imports:** None detected.

## Anti-Patterns

### Module-level mutable accumulator globals

**What happens:** `bboxes = []` and `scoreses = []` at `optimal_ipb_algorithm.py:76–77` are written by `detect_palm()` (a free function) and consumed/cleared in `processAlgorithm()`.
**Why it's wrong:** Makes the algorithm non-reentrant and ties `detect_palm()` to implicit shared state, making it untestable in isolation.
**Do this instead:** Pass `bboxes` and `scoreses` as arguments to `detect_palm()` and return results; instantiate them as local variables inside `processAlgorithm()`.

### Hard-coded absolute Conda environment path

**What happens:** `_CONDA_ENV = r"C:\Users\suily\miniconda3\envs\qgis_gdal_env"` in `__init__.py:34`.
**Why it's wrong:** Plugin fails silently on any machine that is not the developer's. `sys.path` injection is silently skipped if the directory does not exist.
**Do this instead:** Derive the path from an environment variable (e.g. `os.environ.get("OPTIMAL_IPB_ENV")`) or use a `pb_tool.cfg`-driven dependency bundling approach.

### Model reloaded on every run

**What happens:** `load_model()` is called inside `processAlgorithm()` on every algorithm execution.
**Why it's wrong:** Loading a large `.h5` RetinaNet model can take 10–30 seconds and reallocates GPU/CPU memory each run.
**Do this instead:** Cache the loaded model as an instance variable on `OptimalIpbAlgorithm` (or on the provider), keyed by model path; reload only when the selection changes.

## Error Handling

**Strategy:** Minimal — mostly silent failures or Qt message boxes.

**Patterns:**
- `QMessageBox.information()` shown in `initAlgorithm()` when `models/` directory contains no `.h5` files (`optimal_ipb_algorithm.py:232`)
- `tf_keras` import failure silently falls back to `tensorflow.keras` inside `load_model()` (`keras_retinanet/models/__init__.py:87–90`)
- `feedback.isCanceled()` checked per tile — allows graceful abort but leaves global lists partially populated (they are cleared unconditionally at the end of the method)
- No try/except around GDAL raster open, model predict, or NMS operations

## Cross-Cutting Concerns

**Logging:** `QgsMessageLog` is imported (`optimal_ipb_algorithm.py:52`) but not used in the current implementation. Python `logging` with logger name `'QGIS'` used only in `test/test_init.py`.
**Validation:** GDAL raster validity not checked before use. Model file existence enforced implicitly by the enum being empty (triggers `QMessageBox`).
**Authentication:** Not applicable — local file processing only.

---

*Architecture analysis: 2026-06-12*
