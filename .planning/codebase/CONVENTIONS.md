# Coding Conventions

**Analysis Date:** 2026-06-12

## Source Boundaries

The codebase contains two distinct code populations with different conventions:

- **Plugin code** (original): `optimal_ipb.py`, `optimal_ipb_algorithm.py`, `optimal_ipb_provider.py`, `helpers.py`, `__init__.py`
- **Bundled third-party library** (`keras_retinanet/`): Originally from Fizyr, Apache 2.0 licensed. Do not apply plugin conventions here.

When writing new code, follow plugin code conventions only. Do not modify `keras_retinanet/` except where necessary to fix integration bugs.

---

## File Header Convention

Every plugin source file starts with two blocks:

1. A GPL license banner inside a `"""` docstring with plugin metadata (name, date, author, email).
2. Module-level dunder metadata (`__author__`, `__date__`, `__copyright__`, `__revision__`).

```python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OPTIMAL-IPB
                                 A QGIS plugin
 <one-line description>
                              -------------------
        begin                : 2020-09-22
        copyright            : (C) 2020 by Muhammad Nurdin
        email                : muhanur@apps.ipb.ac.id
 ***************************************************************************/
 ...GPL text...
"""

__author__ = 'Muhammad Nurdin'
__date__ = '2020-09-22'
__copyright__ = '(C) 2020 by Muhammad Nurdin'
__revision__ = '$Format:%H$'
```

The `__revision__` line is a git-archive substitution placeholder — include it verbatim in new files.

---

## Naming Patterns

**Files:**
- Plugin modules: `snake_case.py` — e.g., `optimal_ipb_algorithm.py`, `optimal_ipb_provider.py`
- Test files: `test_<subject>.py` — e.g., `test_init.py`, `test_qgis_environment.py`
- Helper/utility modules: plain descriptive names — e.g., `helpers.py`, `utilities.py`

**Classes:**
- Plugin classes: `PascalCase` with `Ipb` infix — e.g., `OptimalIpbPlugin`, `OptimalIpbAlgorithm`, `OptimalIpbProvider`
- Simple data-holding classes: lowercase — e.g., `minmax` in `optimal_ipb_algorithm.py` (non-standard; prefer PascalCase for new classes)
- Test classes: `PascalCase` ending in `Test` — e.g., `TestInit`, `QGISTest`, `SafeTranslationsTest`

**Functions:**
- Plugin helper functions: `snake_case` — e.g., `sliding_window`, `detect_palm`, `pixel2coord`, `map_uint16_to_uint8`
- Mixed convention observed: `non_max_suppression_fast` and `geom_type` are module-level functions; `format_img_size` uses the same pattern
- QGIS Processing override methods: camelCase as required by the QGIS API — e.g., `initAlgorithm`, `processAlgorithm`, `initGui`, `loadAlgorithms`

**Variables and parameters:**
- Local variables: `snake_case` — e.g., `mAP_val`, `model_name`, `band_arr_tmp`
- Algorithm parameter constants: `SCREAMING_SNAKE_CASE` class attributes — e.g., `OUTPUT`, `INPUT`, `OPTIMAL`, `mAP`, `TYPE`
- GDAL/numpy intermediate results: short abbreviations — e.g., `ds`, `winW`, `winH`, `xc`, `yc`

---

## Code Style

**Encoding declaration:**
All plugin files begin with `# -*- coding: utf-8 -*-`.

**Formatting:**
No automated formatter (black, autopep8) is enforced. `setup.cfg` configures flake8 ignore rules, relaxing PEP 8 in the following ways:
- Lines up to 127 characters are accepted (`E501` ignored)
- Tabs in indentation are accepted (`W191` ignored)
- Multiple spaces around operators and after commas are allowed (`E221`, `E241` ignored)
- Extra whitespace inside brackets is allowed (`E201`, `E202`, `E203` ignored)

Practical effect: `helpers.py`'s `non_max_suppression_fast` function uses **tab indentation** while all other plugin files use **4-space indentation**. New code should use 4-space indentation consistently.

**Linting:**
`pylintrc` is present. Key setting: `disable=locally-disabled,C0103` — naming convention warnings (C0103) are suppressed globally, which is why short variable names like `ds`, `b`, `c`, `x1`, `y1` are used freely.

---

## Import Organization

Plugin files do not enforce a strict import order but follow this de-facto pattern:

1. `from __future__` imports (if needed — only in `optimal_ipb_algorithm.py`)
2. Standard library imports (`os`, `sys`, `inspect`, `time`)
3. QGIS framework imports (`from qgis.PyQt.*`, `from qgis.core import ...`)
4. Third-party scientific imports (`numpy`, `pandas`, `lsnms`, `gdal`)
5. Local plugin imports (relative: `from .keras_retinanet.*`, `from .helpers import ...`, `from .optimal_ipb_provider import ...`)

Example from `optimal_ipb_algorithm.py`:
```python
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsFeatureSink, ...)

import numpy as np
import time
import pandas

from lsnms import nms
from osgeo import gdal

from .keras_retinanet.models import load_model
from .helpers import sliding_window
```

Local helper imports from `helpers.py` are done one-per-line (not consolidated into a single `from .helpers import a, b, c` line), e.g.:
```python
from .helpers import sliding_window
from .helpers import format_img
from .helpers import get_real_coordinates
```

---

## QGIS Processing Algorithm Conventions

`OptimalIpbAlgorithm` follows the standard QGIS Processing framework pattern:

- Algorithm parameter IDs are class-level string constants: `OUTPUT`, `INPUT`, `OPTIMAL`, `mAP`, `TYPE`
- `initAlgorithm(self, config)` defines all parameters using `self.addParameter()`
- `processAlgorithm(self, parameters, context, feedback)` performs the computation and returns `{self.OUTPUT: dest_id}`
- `feedback.isCanceled()` is checked inside long loops to support cancellation
- User-facing strings use `self.tr(string)` which wraps `QCoreApplication.translate('Processing', string)`
- `createInstance()` returns `OptimalIpbAlgorithm()` — required by the QGIS framework

```python
def processAlgorithm(self, parameters, context, feedback):
    ...
    for (x, y) in sliding_window(width, height, stepSize):
        if feedback.isCanceled():
            break
        ...
    return {self.OUTPUT: dest_id}
```

---

## Error Handling

**Plugin code (`helpers.py`):**
Input validation uses `raise ValueError(...)` with descriptive messages:
```python
if not(0 <= lower_bound < 2**16) and lower_bound is not None:
    raise ValueError('"lower_bound" must be in the range [0, 65535]')
if lower_bound >= upper_bound:
    raise ValueError('"lower_bound" must be smaller than "upper_bound"')
```

**Plugin code (`optimal_ipb_algorithm.py`):**
No try/except in `processAlgorithm`. Errors surface as unhandled exceptions (QGIS will display them in the Processing log). Missing models are handled by a `QMessageBox.information()` call in `initAlgorithm`, not by raising an exception.

**Bundled library (`keras_retinanet/`):**
Uses `raise NotImplementedError` for abstract base methods, `raise ValueError` for invalid inputs, and `try/except ImportError` for optional dependency fallback (e.g., `tf_keras` vs `tensorflow.keras`).

**Test infrastructure (`test/utilities.py`):**
Uses `try/except ImportError: return None, None, None, None` to gracefully degrade when QGIS is unavailable.

There is no centralized error logging in the plugin. `QgsMessageLog` is imported in `optimal_ipb_algorithm.py` but never called; `LOGGER = logging.getLogger('QGIS')` is the pattern used in test code.

---

## Logging

**In test code:**
```python
LOGGER = logging.getLogger('QGIS')
LOGGER.info(file_path)    # test_init.py
LOGGER.debug(s)           # utilities.py
```

**In plugin runtime code:** No active logging calls. `QgsMessageLog` is imported but unused. User notifications go through `QMessageBox.information()` for critical setup issues only.

---

## Comments

**Inline comments:** Used to describe processing steps in `processAlgorithm` and `detect_palm`, e.g.:
```python
# crop image
# preprocess image for network
# correct for image scale
# select indices which have a score above the threshold
```

**Docstrings:** QGIS Processing override methods have docstrings (boilerplate from Plugin Builder). Helper functions in `helpers.py` have short `""" formats the image ... """` docstrings. `detect_palm` and `geom_type` have no docstrings.

**Commented-out code:** Present in `optimal_ipb_algorithm.py` — the old NMS call is commented out and replaced:
```python
# new_boxes = non_max_suppression_fast(bboxeses, overlapThresh=iouthreshold)
keep = nms(bboxeses, flatten_score, iou_threshold=0.3)
```

**Fizyr library docstrings:** Use `Args` / `Returns` / `Raises` headings (not NumPy or Google style) — e.g., `keras_retinanet/utils/image.py`.

---

## Module Design

**Plugin modules:**
- One class per file for the three main QGIS components (`OptimalIpbPlugin`, `OptimalIpbAlgorithm`, `OptimalIpbProvider`)
- `helpers.py` is a flat collection of utility functions with no class wrapper
- No `__all__` declarations

**Relative imports:**
All intra-plugin imports use explicit relative imports (`.module` syntax). Absolute imports are not used for plugin-internal code:
```python
from .optimal_ipb_provider import OptimalIpbProvider
from .keras_retinanet.models import load_model
from .helpers import sliding_window
```

**Global mutable state:**
`optimal_ipb_algorithm.py` uses module-level mutable lists as accumulators:
```python
bboxes = []
scoreses = []
modelsList = []
```
These are cleared at the start/end of `processAlgorithm`. This is an anti-pattern for thread safety — see CONCERNS.md.

---

## Dependency Injection for External Path

`__init__.py` injects a conda environment's site-packages into `sys.path` at plugin load time:
```python
_CONDA_ENV = r"C:\Users\suily\miniconda3\envs\qgis_gdal_env"
_site_pkgs = os.path.join(_CONDA_ENV, "Lib", "site-packages")
if os.path.isdir(_site_pkgs) and _site_pkgs not in sys.path:
    sys.path.insert(0, _site_pkgs)
```
This is hardcoded to the developer's machine. New code requiring additional dependencies must follow this same pattern or document an alternative.

---

*Convention analysis: 2026-06-12*
