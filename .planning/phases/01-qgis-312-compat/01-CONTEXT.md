# Phase 1: QGIS 3.12 Compatibility & ONNX Inference — Context

**Gathered:** 2026-06-12
**Status:** Ready for planning
**Source:** Session context + codebase analysis

<domain>
## Phase Boundary

This phase wires up the ONNX model for inference (replacing keras/tf_keras), fixes known bugs
surfaced during the Python 3.12 porting session, and ensures the plugin is end-to-end functional
on QGIS 3.44. The ONNX model and Cython extension were already produced in the prior session;
this phase makes the plugin's runtime code use them.

**In scope:**
- Swap inference backend from tf_keras → onnxruntime
- Fix detect_palm() indexing bug
- Update model selector to list .onnx files
- Install onnxruntime into qgis_gdal_env
- Remove stale cp37 .pyd artifact
- Validate end-to-end: plugin loads + runs in QGIS 3.44

**Out of scope:**
- Retraining or fine-tuning the model
- QGIS GUI changes beyond model selector
- Multi-model support or model management UI
- Performance optimization

</domain>

<decisions>
## Implementation Decisions

### D-01: Inference Backend
Replace `from .keras_retinanet.models import load_model` with `import onnxruntime as ort`.
Use `ort.InferenceSession(onnx_path)` to load the model. Call `session.run(None, {input_name: batch})`.

### D-02: ONNX Input Preparation
- `preprocess_image()` and `resize_image()` from `keras_retinanet.utils.image` are kept — they produce correct float32 numpy arrays.
- Input must be `float32` (onnxruntime expectation). Current preprocess already returns float32.
- Input shape: `(1, H, W, 3)` — verify against session input metadata at load time.
- Get input name from `session.get_inputs()[0].name` at runtime (do not hardcode).

### D-03: ONNX Output Mapping
ONNX model outputs (from conversion): `filtered_detections` (boxes), `filtered_detections_1` (scores), `filtered_detections_2` (labels).
Map via `session.get_outputs()` names rather than hardcoded indices for robustness.

### D-04: detect_palm() Indexing Bug Fix
Current bug at line 128: `for i in indices:` iterates raw index values over `image_boxes` which is already re-indexed by `scores_sort`. Fix: iterate `range(len(image_boxes))` instead.

### D-05: Model Selector
`initAlgorithm()` currently lists only `.h5` files:
```python
if file.endswith(".h5"):
```
Change to list `.onnx` files. Update `processAlgorithm()` to call `ort.InferenceSession` instead of `load_model`.

### D-06: onnxruntime Installation
Run: `conda install -n qgis_gdal_env onnxruntime -y`
This adds it to the env injected by `__init__.py`, no QGIS Python changes needed.

### D-07: Stale cp37 Artifact Cleanup
Delete `keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd`.
Python 3.12 skips it (wrong tag) but its presence is confusing.

### D-08: keras_retinanet anchors.py Import Cleanup
`anchors.py` line 18: `from tensorflow import keras` — inconsistent with models/__init__.py which uses tf_keras.
Since anchors.py is training-only and not called during inference, this is low priority — add a comment but don't break it.

### Claude's Discretion
- Exact wave structure and plan decomposition
- Whether to keep the __init__.py path hardcoded or add a fallback detection mechanism
- Error handling verbosity in the onnxruntime inference path
- Whether to keep models/__init__.py load_model() or deprecate it

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Plugin entry points
- `optimal_ipb_algorithm.py` — processAlgorithm(), detect_palm(), initAlgorithm()
- `__init__.py` — conda env injection (already done)
- `keras_retinanet/utils/compute_overlap.py` — pure Python fallback (already working)
- `keras_retinanet/models/__init__.py` — load_model() to be replaced

### Model artifacts
- `models/Google-Resnet101.onnx` — 211 MB, opset 13, outputs: filtered_detections/0/1/2
- `models/Google-Resnet101.h5` — 212 MB, original Keras 2 weights (keep for reference)
- `keras_retinanet/utils/compute_overlap.cp312-win_amd64.pyd` — compiled Cython, Python 3.12

### Codebase map
- `.planning/codebase/CONCERNS.md` — full list of known issues
- `.planning/codebase/ARCHITECTURE.md` — plugin layer architecture
- `.planning/codebase/STACK.md` — full dependency inventory

### Reference: original upstream
- https://github.com/p4wlppmipb/OPTIMAL-IPB — compare any changes against this baseline

</canonical_refs>

<specifics>
## Specific Ideas

### onnxruntime inference pattern (replaces model.predict_on_batch):
```python
import onnxruntime as ort

def load_onnx_model(path):
    return ort.InferenceSession(path, providers=['CPUExecutionProvider'])

def run_inference(session, image_batch):
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: image_batch.astype(np.float32)})
    output_names = [o.name for o in session.get_outputs()]
    # Map: filtered_detections → boxes, filtered_detections_1 → scores, filtered_detections_2 → labels
    boxes  = outputs[output_names.index('filtered_detections')]
    scores = outputs[output_names.index('filtered_detections_1')]
    labels = outputs[output_names.index('filtered_detections_2')]
    return boxes, scores, labels
```

### detect_palm() fix:
```python
# BEFORE (buggy):
for i in indices:
    b = np.array(image_boxes[i,:]).astype(int)

# AFTER (fixed):
for i in range(len(image_boxes)):
    b = np.array(image_boxes[i,:]).astype(int)
```

### Model selector fix:
```python
# BEFORE:
if file.endswith(".h5"):

# AFTER:
if file.endswith(".onnx"):
```

### processAlgorithm model loading:
```python
# BEFORE:
model = load_model(os.path.join(cmd_folder, 'models/', model_name), backbone_name='resnet101')

# AFTER:
model = ort.InferenceSession(
    os.path.join(cmd_folder, 'models', model_name),
    providers=['CPUExecutionProvider']
)
```

</specifics>

<deferred>
## Deferred Ideas

- GPU inference via CUDAExecutionProvider (onnxruntime-gpu not in scope)
- Making conda env path configurable via QGIS plugin settings dialog
- Removing keras_retinanet entirely once onnxruntime path is proven
- Training workflow improvements

</deferred>

---
*Phase: 01-qgis-312-compat*
*Context gathered: 2026-06-12 via session analysis*
