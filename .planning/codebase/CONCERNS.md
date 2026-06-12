# Codebase Concerns

**Analysis Date:** 2026-06-12

---

## Known Bugs

### IndexError in detect_palm() — line 127-128

**Symptoms:** `IndexError: index N is out of bounds for axis 0 with size M` during any inference run that produces detections.
**Files:** `optimal_ipb_algorithm.py` lines 116–135
**Trigger:** Any image window where at least one detection passes the score threshold.
**Root cause:** After sorting, `image_boxes` is compacted to length `len(indices)` but the loop still iterates over `indices`, which contains raw position values from the original 300-element model output. When a raw index value exceeds the length of the compacted `image_boxes` array the access `image_boxes[i, :]` raises `IndexError`.

```python
# Actual code — BUG
indices = np.where(scores[0, :] >= scorethreshold)[0]   # raw offsets, e.g. [5, 47, 123]
scores_sort = np.argsort(-scores[0][indices])
image_boxes = boxes[0, indices[scores_sort], :]         # shape (len(indices), 4)

for i in indices:                                        # WRONG: iterates raw offsets
    b = np.array(image_boxes[i, :]).astype(int)         # IndexError when i >= len(indices)
```

**Fix:** Replace `for i in indices:` with `for i in range(len(image_boxes)):` (or equivalently `enumerate(image_boxes)`).

---

### type_val retrieved as Double instead of Enum integer

**Symptoms:** Output type comparison `if type_val == 0` always resolves to `False` because `parameterAsDouble` returns a float (e.g. `0.0`) while `geom_type()` switcher keys are integers.
**Files:** `optimal_ipb_algorithm.py` lines 302–303, 330–336
**Trigger:** Every run. Users will silently get the wrong output geometry type.
**Root cause:** Line 302 calls `self.parameterAsDouble(parameters, self.TYPE, context)` for a parameter declared as `QgsProcessingParameterEnum`. The correct method is `self.parameterAsEnum(...)` which returns an `int`.

```python
# Line 302 — BUG
type_val = self.parameterAsDouble(parameters, self.TYPE, context)
# Should be:
type_val = self.parameterAsEnum(parameters, self.TYPE, context)
```

---

### Crash when no detections found — empty bboxes list

**Symptoms:** `ValueError: need at least one array to concatenate` (from `np.concatenate(scoreses)`) or `ValueError` from `nms()` receiving an empty array, when an entire image produces zero detections.
**Files:** `optimal_ipb_algorithm.py` lines 286–291
**Trigger:** Raster image with no oil-palm trees, or score threshold set very high.
**Root cause:** No guard on `len(bboxes) == 0` before calling `np.array(bboxes, ...)` and `np.concatenate(scoreses)`. Both calls fail on empty inputs.

---

## Tech Debt

### Hardcoded conda environment path in __init__.py

- Issue: `_CONDA_ENV = r"C:\Users\suily\miniconda3\envs\qgis_gdal_env"` is written literally into the plugin entry point. Installing on any other machine silently skips dependency injection, causing `ImportError` on `tf_keras`, `lsnms`, `pandas`, etc.
- Files: `__init__.py` lines 34–41
- Impact: Plugin is non-portable. Every new developer must manually edit this line. Deployment to any other Windows user profile fails without error message.
- Fix approach: Read the path from a config file (e.g. `plugin_config.ini` or a QGIS plugin settings key), or document an environment variable (`OPTIMAL_IPB_CONDA_ENV`) that can be overridden. Fall back gracefully with a QMessageBox explaining the missing dependency instead of silently continuing.

---

### ONNX model present but not wired — inference still uses full TF runtime

- Issue: `models/Google-Resnet101.onnx` exists but there is zero `onnxruntime` code anywhere in the plugin. Every inference run loads a full TF/Keras model via `load_model()` in `keras_retinanet/models/__init__.py`, pulling in the entire TF 2.x runtime (~500 MB RAM on first call).
- Files: `keras_retinanet/models/__init__.py` line 88–91, `optimal_ipb_algorithm.py` line 243
- Impact: Startup latency, excessive RAM consumption (TF initialises a GPU context even when unused), prevents distributing a lightweight plugin without conda env.
- Fix approach: Add an `onnxruntime`-based inference path; when the selected model file ends in `.onnx`, call `ort.InferenceSession(model_path)` instead of `keras.models.load_model()`. The preprocessing pipeline (`preprocess_image`, `resize_image`) is pure NumPy and is already compatible.

---

### Model selector only shows .h5 files — .onnx models invisible

- Issue: `initAlgorithm()` only appends files ending in `".h5"` to `modelsList`, so `models/Google-Resnet101.onnx` never appears in the UI dropdown.
- Files: `optimal_ipb_algorithm.py` lines 175–177
- Impact: Users cannot select the ONNX model even after ONNX inference is wired; the ONNX file is invisible in the tool.
- Fix approach: Change the filter to `if file.endswith(".h5") or file.endswith(".onnx"):`.

---

### Global mutable state: bboxes[] and scoreses[] at module level

- Issue: `bboxes = []` and `scoreses = []` are declared at module scope (lines 76–77) and mutated inside `detect_palm()`. They are only cleared at the end of `processAlgorithm()` (lines 345–346). If the algorithm is cancelled mid-run, an exception is thrown, or two algorithm instances run concurrently, the lists carry stale data into the next run, corrupting results.
- Files: `optimal_ipb_algorithm.py` lines 76–77, 133–135, 286–287, 345–346
- Impact: Silent result corruption on error recovery or parallel runs. Not thread-safe (QGIS can execute multiple processing algorithms simultaneously).
- Fix approach: Move `bboxes` and `scoreses` to local variables inside `processAlgorithm()`, pass them into `detect_palm()` as arguments (or accumulate return values), and remove the module-level declarations.

---

### Stale Python 3.7 compiled artifact alongside Python 3.12 build

- Issue: `keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd` (Python 3.7 binary extension) coexists with `compute_overlap.cp312-win_amd64.pyd` and the pure-NumPy fallback `compute_overlap.py`. Python 3.12 will load the `.py` fallback correctly, but the orphaned `.pyd` is a source of confusion and potential import resolution errors if Python version detection changes.
- Files: `keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd`
- Impact: Repository noise; risk of wrong binary being loaded if a Python 3.7 interpreter is ever on `sys.path`.
- Fix approach: Delete `compute_overlap.cp37-win_amd64.pyd`. Also remove the intermediate build artefacts under `keras_retinanet/utils/build/` from version control (add to `.gitignore`).

---

### Inconsistent keras import strategy — anchors.py uses `from tensorflow import keras` directly

- Issue: `keras_retinanet/models/__init__.py` (`load_model`, lines 87–91) correctly attempts `import tf_keras as keras` with a fallback to `from tensorflow import keras` to support Keras 2 model loading. However, all other modules in `keras_retinanet/` (including `utils/anchors.py` line 18, `backend/backend.py` line 18, `initializers.py` line 17, all layer files, all model backbone files) bypass this logic and import `from tensorflow import keras` directly. On TF 2.16+ where `tensorflow.keras` is Keras 3, these modules will fail or produce incompatible objects.
- Files: `keras_retinanet/utils/anchors.py:18`, `keras_retinanet/backend/backend.py:18`, `keras_retinanet/initializers.py:17`, `keras_retinanet/layers/filter_detections.py:18`, `keras_retinanet/layers/_misc.py:18`, `keras_retinanet/losses.py:18`, `keras_retinanet/models/resnet.py:17`, `keras_retinanet/models/retinanet.py:17`, and 8 others.
- Impact: The tf_keras workaround in `__init__.py` only protects model loading; the custom layer classes, losses, and initializers that are used as `custom_objects` are still built with the Keras 3 API, causing class mismatch when `tf_keras.models.load_model` attempts to deserialise them.
- Fix approach: Create a shared `keras_retinanet/compat.py` that exposes a single `keras` object (tries `tf_keras` first), then have all modules do `from ..compat import keras` instead of `from tensorflow import keras`.

---

## Performance Bottlenecks

### Per-band ReadAsArray() during min/max computation loads entire raster into RAM

- Issue: `processAlgorithm()` lines 254–258 call `band.ReadAsArray()` for every band, loading the full raster (potentially multi-GB) into memory three times just to compute 2nd/98th percentile statistics.
- Files: `optimal_ipb_algorithm.py` lines 254–258
- Impact: OOM kills for large imagery; unnecessarily slow startup.
- Fix approach: Use `gdal.Band.ComputeRasterStatistics()` or `gdal.Band.GetHistogram()` for approximate percentile computation without reading the full array.

---

### Model reloaded on every algorithm run — no caching

- Issue: `load_model(...)` is called inside `processAlgorithm()` (line 243), which means the entire Keras model is deserialized from disk and re-compiled on every execution click.
- Files: `optimal_ipb_algorithm.py` line 243
- Impact: 10–30 second cold-start per run due to TF graph compilation; unacceptable UX for iterative use.
- Fix approach: Cache the loaded model in a module-level or class-level dict keyed by `model_name`. Only reload if the model file changes.

---

## Fragile Areas

### detect_palm() appends to global lists without error recovery

- Files: `optimal_ipb_algorithm.py` lines 88–135
- Why fragile: If `preprocess_image`, `resize_image`, or `model.predict_on_batch` raises an exception mid-run, the function exits without appending to `bboxes` but the calling loop continues. `bboxes.clear()` at line 345 only runs if `processAlgorithm` completes normally; a cancelled run or exception leaves stale data for the next run.
- Safe modification: Wrap sliding window loop in try/finally to always call `bboxes.clear(); scoreses.clear()`.
- Test coverage: No unit tests cover `detect_palm()` directly.

---

### helpers.py uses `cv2` without importing it

- Files: `helpers.py` line 39 (`cv2.resize`), line 1 (only `import numpy as np`)
- Why fragile: `format_img_size()` calls `cv2.resize()` but `cv2` is never imported in this file. The function will raise `NameError: name 'cv2' is not defined` if called.
- Impact: `format_img` and `format_img_size` are dead at runtime. `format_img` is imported in `optimal_ipb_algorithm.py` line 70 but never called (confirmed by grep — it is an unused import), so this does not currently crash inference. However, any future caller of `format_img` will fail immediately.
- Safe modification: Either add `import cv2` at the top of `helpers.py` or delete `format_img_size`, `format_img_channels`, and `format_img` as unreachable dead code.

---

### No raster band-count validation before indexing bands

- Files: `optimal_ipb_algorithm.py` lines 90–103
- Why fragile: `detect_palm()` accesses `a_image[2]`, `a_image[1]`, `a_image[0]` directly assuming at least 3 bands. If the user supplies a single-band (grayscale) or 4-band (RGBA) raster, this raises `IndexError` with no user-facing explanation.
- Safe modification: Add a guard in `processAlgorithm()` after `rastercount = ds.RasterCount`: if `rastercount < 3`, show a `QMessageBox` error and return early.

---

## Dead Code

### Unused imports in optimal_ipb_algorithm.py

- `import time` — no `time.*` call exists in the file.
- `import pandas` — no `pandas.*` call exists in the file.
- `from .helpers import format_img` — `format_img` is never called (and would crash if called; see helpers.py concern above).
- `from .helpers import get_real_coordinates` — never called.
- `from .helpers import non_max_suppression_fast` — commented out at line 290; the function is dead.
- Files: `optimal_ipb_algorithm.py` lines 55–56, 70–71, 73

---

### Commented-out NMS call

- `# new_boxes = non_max_suppression_fast(bboxeses, overlapThresh=iouthreshold)` at line 290 is a code remnant from before `lsnms` was adopted. The variable `iouthreshold = 0.5` (line 238) is also only referenced by this dead comment.
- Files: `optimal_ipb_algorithm.py` lines 238, 290

---

## Test Coverage Gaps

### Core inference logic has zero test coverage

- What's not tested: `detect_palm()`, `processAlgorithm()`, the sliding-window loop, the global state clear/reset, the NMS call, and all geometry construction code.
- Files: `optimal_ipb_algorithm.py` (entire file except class boilerplate)
- Risk: All five confirmed bugs listed above would be caught by a basic unit test against a synthetic 3-band GDAL in-memory raster.
- Priority: High — these are the only files that change between releases.

### Existing tests do not exercise plugin functionality

- What's not tested: The three test files in `test/` (`test_init.py`, `test_qgis_environment.py`, `test_translations.py`) only verify metadata presence and QGIS environment setup. None import or call any plugin logic.
- Files: `test/test_init.py`, `test/test_qgis_environment.py`, `test/test_translations.py`
- Risk: Regressions in algorithm logic go undetected until manual use.
- Priority: High

---

## Dependencies at Risk

### tf_keras / tensorflow — heavy runtime, version-locked model format

- Risk: The `.h5` model was saved with Keras 2. TF 2.16+ ships Keras 3 as `tensorflow.keras`, breaking deserialization of custom layers. `tf_keras` (the standalone Keras 2 compatibility package) must be present and is not a standard QGIS dependency.
- Impact: Entire inference pipeline fails on TF 2.16+ without `tf_keras` installed in the conda env.
- Migration plan: Export model to ONNX (already done — `models/Google-Resnet101.onnx` exists) and switch inference to `onnxruntime`, eliminating the TF dependency for end users.

### keras_resnet — unmaintained, Keras 2 only

- Risk: `keras_retinanet/models/resnet.py` imports `keras_resnet` (line 18). This package has not been updated for Keras 3 and relies on the same `from tensorflow import keras` pattern.
- Impact: `resnet_retinanet()` and therefore model loading fails on TF 2.16+ without `tf_keras`.
- Migration plan: Inline the ResNet backbone definition (it is small) or replace with `tf.keras.applications.ResNet101` once migrated to ONNX export.

---

*Concerns audit: 2026-06-12*
