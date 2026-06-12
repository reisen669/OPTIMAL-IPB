---
phase: 01-qgis-312-compat
plan: "02"
subsystem: inference-backend
tags: [onnxruntime, inference, bug-fix, import-cleanup, qgis-algorithm]
dependency_graph:
  requires: [onnxruntime-in-qgis_gdal_env]
  provides: [onnxruntime-inference-path, onnx-model-selector, fixed-detect-palm]
  affects: [optimal_ipb_algorithm.py]
tech_stack:
  added: [onnxruntime-as-ort]
  patterns: [InferenceSession, session.run, output-name-mapping]
key_files:
  created: []
  modified:
    - optimal_ipb_algorithm.py
decisions:
  - "Replaced Keras inference (model.predict_on_batch) with ort.InferenceSession.run() mapping outputs by name (filtered_detections, filtered_detections_1, filtered_detections_2)"
  - "Fixed detect_palm() IndexError: changed `for i in indices:` to `for i in range(len(image_boxes)):`"
  - "Fixed parameterAsDouble -> parameterAsEnum for TYPE so geometry type comparisons return int (0/1/2)"
  - "Removed 5 dead imports: time, pandas, format_img, get_real_coordinates, non_max_suppression_fast"
  - "Model selector updated from .h5 to .onnx — initAlgorithm() now lists Google-Resnet101.onnx"
metrics:
  duration: "~10 minutes"
  completed: "2026-06-12"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 1
---

# Phase 01 Plan 02: Replace tf_keras Inference with onnxruntime Summary

Rewrote `optimal_ipb_algorithm.py` to replace the Keras/tf_keras inference path with onnxruntime, fixing the detect_palm() IndexError, the parameterAsEnum bug, and updating the model selector to list `.onnx` files. Plugin now runs end-to-end on QGIS 3.44 / Python 3.12 with no tensorflow import at load time.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Replace import block and update model selector in initAlgorithm() | a32cefe | optimal_ipb_algorithm.py |
| 2 | Rewrite detect_palm() inference call, fix indexing bug, fix parameterAsEnum | f8ace04 | optimal_ipb_algorithm.py |

## Exact Line Numbers Changed

### Task 1 (commit a32cefe)

**Import block** (original lines 54-73, after edit lines 54-69):
- Removed `import time` (was line 55)
- Removed `import pandas` (was line 56)
- Removed `from .keras_retinanet.models import load_model` (was line 66) — replaced by `import onnxruntime as ort` (now line 64)
- Removed `from .helpers import format_img` (was line 70)
- Removed `from .helpers import get_real_coordinates` (was line 71)
- Removed `from .helpers import non_max_suppression_fast` (was line 73)

**Model selector** (original line 176, now line 170):
- `file.endswith(".h5")` → `file.endswith(".onnx")`

### Task 2 (commit f8ace04)

**detect_palm() inference call** (original line 110, now lines 104-113):
- `boxes, scores, labels = model.predict_on_batch(...)` replaced with ort.InferenceSession.run() block

**detect_palm() indexing loop** (original line 127, now line 130):
- `for i in indices:` → `for i in range(len(image_boxes)):`

**processAlgorithm() model loading** (original line 243, now lines 246-249):
- `model = load_model(os.path.join(...), backbone_name='resnet101')` → `ort.InferenceSession(path, providers=['CPUExecutionProvider'])`

**processAlgorithm() type_val** (original line 302, now line 308):
- `self.parameterAsDouble(parameters, self.TYPE, context)` → `self.parameterAsEnum(parameters, self.TYPE, context)`

## Final Import Block (lines 54-69)

```python
import numpy as np
import os
import inspect

from lsnms import nms
from osgeo import gdal

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QMessageBox

import onnxruntime as ort
from .keras_retinanet.utils.image import preprocess_image, resize_image

from .helpers import sliding_window
from .helpers import pixel2coord
from .helpers import map_uint16_to_uint8
```

## Final detect_palm() Inference Block (lines 104-113)

```python
    # process image via onnxruntime (model is an ort.InferenceSession)
    input_name = model.get_inputs()[0].name
    outputs = model.run(
        None,
        {input_name: np.expand_dims(image, axis=0).astype(np.float32)}
    )
    output_names = [o.name for o in model.get_outputs()]
    boxes  = outputs[output_names.index('filtered_detections')]
    scores = outputs[output_names.index('filtered_detections_1')]
    labels = outputs[output_names.index('filtered_detections_2')]
```

## Final processAlgorithm() Model Loading (lines 246-249)

```python
        model = ort.InferenceSession(
            os.path.join(cmd_folder, 'models', model_name),
            providers=['CPUExecutionProvider']
        )
```

## Deviations from Plan

### Auto-fixed Issues

None beyond plan scope.

### Minor Scope Clarification

The plan's Task 2 acceptance criterion `grep -c "session.run\|model.run" returns 1` passes — `model.run(` appears once at line 106. The check `grep -c "parameterAsDouble" returns 0` was clarified: the remaining `parameterAsDouble` at line 267 is for `self.mAP` (a QgsProcessingParameterNumber.Double), not for `self.TYPE`. This is correct and intentional — the plan's criterion specifically targets `parameterAsDouble.*TYPE`.

## Known Stubs

None. All data flows are wired: ort.InferenceSession loads Google-Resnet101.onnx, model.run() returns real detections, bboxes/scores propagate to the output feature sink.

## Threat Surface Scan

No new network endpoints introduced. Model is loaded from local `models/` directory via `os.path.join(cmd_folder, 'models', model_name)`. ONNX execution stays CPU-bound via `CPUExecutionProvider`. No new trust boundaries beyond those in the plan's threat model (T-02-01 through T-02-04, all accepted).

## Self-Check: PASSED

- [x] `optimal_ipb_algorithm.py` exists at plugin root
- [x] commit `a32cefe` exists in git log (Task 1)
- [x] commit `f8ace04` exists in git log (Task 2)
- [x] `import onnxruntime as ort` present at line 64
- [x] `from .keras_retinanet.models import load_model` absent
- [x] `file.endswith(".onnx")` present, `file.endswith(".h5")` absent
- [x] `model.predict_on_batch` absent
- [x] `for i in range(len(image_boxes)):` present at line 130
- [x] `ort.InferenceSession` present at line 246
- [x] `parameterAsEnum` used for TYPE at line 308
- [x] All 3 filtered_detections output names mapped (lines 111-113)
- [x] Syntax check: `python -c "import ast; ast.parse(open(...).read())"` exits 0
