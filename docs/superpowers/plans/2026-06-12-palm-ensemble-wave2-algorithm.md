# Palm Ensemble — Wave 2: PalmEnsembleAlgorithm Implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `PalmEnsembleAlgorithm` to the OPTIMAL-IPB Processing provider — a second algorithm in the toolbox that merges any two palm centroid layers into a confidence-scored union output.

**Architecture:** One new Python file (`palm_ensemble_algorithm.py`) with the algorithm class; `optimal_ipb_provider.py` registers it. The algorithm is fully detector-agnostic: inputs are any two vector point layers, output fields are `confidence` (1.0/0.5), `source` (both/layer_a_name/layer_b_name), `score_a`, `score_b`. Spatial proximity matching with configurable distance threshold handles the merge.

**Tech Stack:** Python 3.12, QGIS 3.44 PyQGIS API (`qgis.core`), no new pip dependencies

**Gate:** Only begin after Wave 1 `02-01-SUMMARY.md` exists and confirms Plugin A and Plugin B.

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `palm_ensemble_algorithm.py` | **Create** | `PalmEnsembleAlgorithm` class + `_get_score()` helper |
| `optimal_ipb_provider.py` | **Modify** | Register `PalmEnsembleAlgorithm`; fix stale `inspect.getfile` icon bug |
| `test/test_ensemble_algorithm.py` | **Create** | Syntax + logic smoke tests (no full QGIS app required) |

---

### Task 1: Create `palm_ensemble_algorithm.py`

**Files:**
- Create: `palm_ensemble_algorithm.py`

- [ ] **Step 1: Create the file with complete algorithm code**

Write `C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\palm_ensemble_algorithm.py` with the following content in full:

```python
# -*- coding: utf-8 -*-
from __future__ import division

__author__ = 'optimal-ipb contributors'
__date__ = '2026-06-12'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsFeatureSink,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsMessageLog,
)


def _get_score(feat):
    """Return first parseable numeric score from a feature, or None."""
    for name in ('Score', 'score', 'confidence', 'prob', 'probability'):
        try:
            val = feat[name]
            if val is not None:
                return float(val)
        except (KeyError, ValueError, TypeError):
            pass
    for i in range(feat.fields().count()):
        try:
            val = feat[i]
            if val is not None:
                return float(val)
        except (ValueError, TypeError):
            pass
    return None


class PalmEnsembleAlgorithm(QgsProcessingAlgorithm):
    INPUT_A = 'INPUT_A'
    INPUT_B = 'INPUT_B'
    THRESHOLD = 'THRESHOLD'
    LAYER_A_NAME = 'LAYER_A_NAME'
    LAYER_B_NAME = 'LAYER_B_NAME'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_A,
                self.tr('Layer A (any palm detector output)'),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_B,
                self.tr('Layer B (any palm detector output)'),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                self.tr('Match distance threshold (map units)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.LAYER_A_NAME,
                self.tr('Layer A name (used in source field)'),
                defaultValue='detector_a',
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.LAYER_B_NAME,
                self.tr('Layer B name (used in source field)'),
                defaultValue='detector_b',
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Ensemble output'),
                QgsProcessing.TypeVectorPoint,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer_a = self.parameterAsVectorLayer(parameters, self.INPUT_A, context)
        layer_b = self.parameterAsVectorLayer(parameters, self.INPUT_B, context)
        threshold = self.parameterAsDouble(parameters, self.THRESHOLD, context)
        name_a = self.parameterAsString(parameters, self.LAYER_A_NAME, context)
        name_b = self.parameterAsString(parameters, self.LAYER_B_NAME, context)

        if layer_a.crs() != layer_b.crs():
            raise QgsProcessingException(
                f'CRS mismatch: Layer A is {layer_a.crs().authid()}, '
                f'Layer B is {layer_b.crs().authid()}. '
                'Reproject one layer to match before running ensemble.'
            )

        fields = QgsFields()
        fields.append(QgsField('confidence', QVariant.Double, 'double', 5, 2))
        fields.append(QgsField('source', QVariant.String, 'string', 50))
        fields.append(QgsField('score_a', QVariant.Double, 'double', 10, 6))
        fields.append(QgsField('score_b', QVariant.Double, 'double', 10, 6))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields,
            QgsWkbTypes.Point, layer_a.crs()
        )

        feats_a = list(layer_a.getFeatures())
        feats_b = list(layer_b.getFeatures())

        if not feats_a and not feats_b:
            QgsMessageLog.logMessage(
                'OPTIMAL-IPB Ensemble: both input layers are empty.',
                'OPTIMAL-IPB',
            )
            return {self.OUTPUT: dest_id}

        if not feats_a:
            QgsMessageLog.logMessage(
                f'OPTIMAL-IPB Ensemble: Layer A ({name_a}) is empty. '
                'Returning Layer B at confidence=0.5.',
                'OPTIMAL-IPB',
            )
            for feat in feats_b:
                out = QgsFeature(fields)
                out.setGeometry(feat.geometry())
                out.setAttributes([0.5, name_b, None, _get_score(feat)])
                sink.addFeature(out, QgsFeatureSink.FastInsert)
            return {self.OUTPUT: dest_id}

        if not feats_b:
            QgsMessageLog.logMessage(
                f'OPTIMAL-IPB Ensemble: Layer B ({name_b}) is empty. '
                'Returning Layer A at confidence=0.5.',
                'OPTIMAL-IPB',
            )
            for feat in feats_a:
                out = QgsFeature(fields)
                out.setGeometry(feat.geometry())
                out.setAttributes([0.5, name_a, _get_score(feat), None])
                sink.addFeature(out, QgsFeatureSink.FastInsert)
            return {self.OUTPUT: dest_id}

        matched_b = set()

        for feat_a in feats_a:
            if feedback.isCanceled():
                break
            pt_a = feat_a.geometry().asPoint()
            best_dist = float('inf')
            best_feat_b = None
            best_idx = None

            for idx, feat_b in enumerate(feats_b):
                if idx in matched_b:
                    continue
                dist = pt_a.distance(feat_b.geometry().asPoint())
                if dist < best_dist:
                    best_dist = dist
                    best_feat_b = feat_b
                    best_idx = idx

            out = QgsFeature(fields)
            score_a = _get_score(feat_a)

            if best_feat_b is not None and best_dist <= threshold:
                pt_b = best_feat_b.geometry().asPoint()
                mid = QgsPointXY((pt_a.x() + pt_b.x()) / 2,
                                 (pt_a.y() + pt_b.y()) / 2)
                out.setGeometry(QgsGeometry.fromPointXY(mid))
                out.setAttributes([1.0, 'both', score_a, _get_score(best_feat_b)])
                matched_b.add(best_idx)
            else:
                out.setGeometry(feat_a.geometry())
                out.setAttributes([0.5, name_a, score_a, None])

            sink.addFeature(out, QgsFeatureSink.FastInsert)

        for idx, feat_b in enumerate(feats_b):
            if idx not in matched_b:
                out = QgsFeature(fields)
                out.setGeometry(feat_b.geometry())
                out.setAttributes([0.5, name_b, None, _get_score(feat_b)])
                sink.addFeature(out, QgsFeatureSink.FastInsert)

        if not matched_b:
            QgsMessageLog.logMessage(
                f'OPTIMAL-IPB Ensemble: No matches within {threshold} map units. '
                'Consider increasing the threshold.',
                'OPTIMAL-IPB',
            )

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'palm-ensemble'

    def displayName(self):
        return self.tr('Palm Ensemble')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def shortHelpString(self):
        return self.tr(
            'Merges two palm detection point layers into a single confidence-scored layer.\n\n'
            'confidence=1.0: both detectors agree (point within threshold distance).\n'
            'confidence=0.5: only one detector found this palm.\n\n'
            'source field shows "both" or the detector name for unmatched points.\n\n'
            'Run your two detectors separately first, then feed their outputs here.'
        )

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PalmEnsembleAlgorithm()
```

- [ ] **Step 2: Syntax-check the new file**

```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m py_compile `
  "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\palm_ensemble_algorithm.py"
echo "Exit code: $LASTEXITCODE"
```

Expected: no output, exit code 0. Any `SyntaxError` must be fixed before continuing.

- [ ] **Step 3: Commit the new algorithm file**

```powershell
git add palm_ensemble_algorithm.py
git commit -m "feat: add PalmEnsembleAlgorithm skeleton"
```

---

### Task 2: Register Algorithm in Provider + Fix Icon Bug

**Files:**
- Modify: `optimal_ipb_provider.py` (lines 34, 38, 56–61, 86–87)

The provider still uses `inspect.getfile` for its icon (line 86) — the same bug that was fixed in the algorithm file. Fix it at the same time.

- [ ] **Step 1: Read the current provider file**

Read `optimal_ipb_provider.py` to confirm current content at lines 34–38 and 56–61 and 86–87.

- [ ] **Step 2: Apply three changes to `optimal_ipb_provider.py`**

**Change A** — add import at top of file (after line 33 `import os`):
Old:
```python
import os
import inspect
from qgis.PyQt.QtGui import QIcon
```
New:
```python
import os
from qgis.PyQt.QtGui import QIcon
```

**Change B** — add ensemble import alongside existing algorithm import (line 38):
Old:
```python
from .optimal_ipb_algorithm import OptimalIpbAlgorithm
```
New:
```python
from .optimal_ipb_algorithm import OptimalIpbAlgorithm
from .palm_ensemble_algorithm import PalmEnsembleAlgorithm
```

**Change C** — register the new algorithm in `loadAlgorithms` (line 60):
Old:
```python
    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.addAlgorithm(OptimalIpbAlgorithm())
        # add additional algorithms here
        # self.addAlgorithm(MyOtherAlgorithm())
```
New:
```python
    def loadAlgorithms(self):
        self.addAlgorithm(OptimalIpbAlgorithm())
        self.addAlgorithm(PalmEnsembleAlgorithm())
```

**Change D** — fix stale `inspect.getfile` icon (lines 86–88):
Old:
```python
    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        return icon
```
New:
```python
    def icon(self):
        cmd_folder = os.path.dirname(os.path.abspath(__file__))
        return QIcon(os.path.join(cmd_folder, 'logo.png'))
```

- [ ] **Step 3: Syntax-check the modified provider**

```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m py_compile `
  "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\optimal_ipb_provider.py"
echo "Exit code: $LASTEXITCODE"
```

Expected: no output, exit code 0.

- [ ] **Step 4: Commit provider changes**

```powershell
git add optimal_ipb_provider.py
git commit -m "feat: register PalmEnsembleAlgorithm; fix provider icon path"
```

---

### Task 3: Write Smoke Tests

**Files:**
- Create: `test/test_ensemble_algorithm.py`

These tests validate `_get_score()` and the merge logic using lightweight mock objects — no full QGIS application required.

- [ ] **Step 1: Create the test file**

Write `C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\test\test_ensemble_algorithm.py`:

```python
"""
Smoke tests for _get_score() and merge logic.
Run with: python -m pytest test/test_ensemble_algorithm.py -v
Requires: qgis_gdal_env Python (no QGIS application needed for these tests).
"""
import sys
import os
import pytest

# Allow importing plugin modules without a QGIS app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockField:
    def __init__(self, name):
        self._name = name
    def name(self):
        return self._name


class MockFields:
    def __init__(self, names):
        self._fields = [MockField(n) for n in names]
    def count(self):
        return len(self._fields)
    def __getitem__(self, i):
        return self._fields[i]


class MockFeature:
    def __init__(self, attrs, field_names):
        self._attrs = attrs
        self._fields = MockFields(field_names)
        self._data = dict(zip(field_names, attrs))
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._attrs[key]
        return self._data[key]
    def fields(self):
        return self._fields


# Import _get_score after path setup
from palm_ensemble_algorithm import _get_score


class TestGetScore:
    def test_score_field_by_name(self):
        feat = MockFeature([0.87], ['Score'])
        assert _get_score(feat) == pytest.approx(0.87)

    def test_confidence_field_by_name(self):
        feat = MockFeature([0.42], ['confidence'])
        assert _get_score(feat) == pytest.approx(0.42)

    def test_fallback_to_first_numeric_field(self):
        feat = MockFeature([0.99], ['weird_name'])
        assert _get_score(feat) == pytest.approx(0.99)

    def test_returns_none_when_value_is_none(self):
        feat = MockFeature([None], ['Score'])
        assert _get_score(feat) is None

    def test_string_score_parsed_as_float(self):
        feat = MockFeature(['0.75'], ['Score'])
        assert _get_score(feat) == pytest.approx(0.75)

    def test_nonnumeric_string_returns_none(self):
        feat = MockFeature(['notanumber'], ['Score'])
        assert _get_score(feat) is None
```

- [ ] **Step 2: Run the tests**

```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m pytest `
  "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\test\test_ensemble_algorithm.py" `
  -v
```

Expected output:
```
PASSED test_score_field_by_name
PASSED test_confidence_field_by_name
PASSED test_fallback_to_first_numeric_field
PASSED test_returns_none_when_value_is_none
PASSED test_string_score_parsed_as_float
PASSED test_nonnumeric_string_returns_none
6 passed
```

If `pytest` is not installed in qgis_gdal_env:
```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m pip install pytest
```

- [ ] **Step 3: Commit tests**

```powershell
git add test/test_ensemble_algorithm.py
git commit -m "test: add _get_score unit tests for ensemble algorithm"
```

---

### Task 4: QGIS Integration Test — Algorithm Loads and Appears in Toolbox

This task requires a live QGIS session.

- [ ] **Step 1: Reload the plugin in QGIS**

1. Open QGIS 3.44
2. Plugins → Manage and Install Plugins → Installed
3. Uncheck OPTIMAL-IPB, then recheck it (or use Plugin Reloader if installed)
4. Open View → Panels → Log Messages

- [ ] **Step 2: Verify no Python errors**

Expected in Log Messages panel (OPTIMAL-IPB tab):
```
OPTIMAL-IPB: cmd_folder=C:\...\optimal-ipb
OPTIMAL-IPB: models found=['Google-Resnet101.onnx']
```

No Python tracebacks. No `ImportError` for `palm_ensemble_algorithm`.

- [ ] **Step 3: Verify Palm Ensemble appears in Processing Toolbox**

Open Processing Toolbox (Ctrl+Alt+T).

Expected: Under the OPTIMAL-IPB provider, two algorithms appear:
- `OPTIMAL-IPB`
- `Palm Ensemble`

---

### Task 5: QGIS Integration Test — Ensemble Merge Logic

This task uses QGIS to test the merge algorithm on synthetic point layers.

- [ ] **Step 1: Create two synthetic point layers using the QGIS console**

Open QGIS Python Console (Plugins → Python Console) and run:

```python
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsProject
from qgis.PyQt.QtCore import QVariant

def make_layer(name, points_scores):
    layer = QgsVectorLayer('Point?crs=EPSG:4326', name, 'memory')
    pr = layer.dataProvider()
    pr.addAttributes([QgsField('Score', QVariant.Double)])
    layer.updateFields()
    feats = []
    for (x, y), score in points_scores:
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        f.setAttributes([score])
        feats.append(f)
    pr.addFeatures(feats)
    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)
    return layer

# Layer A: 3 palms
layer_a = make_layer('detector_a', [
    ((106.0, -6.0), 0.91),
    ((106.1, -6.1), 0.85),
    ((106.2, -6.2), 0.78),
])

# Layer B: 2 matching + 1 unmatched (far away)
layer_b = make_layer('detector_b', [
    ((106.0001, -6.0001), 0.88),   # near A[0] — should match
    ((106.1001, -6.1001), 0.82),   # near A[1] — should match
    ((107.0, -7.0), 0.60),         # far from all A — unmatched
])
```

- [ ] **Step 2: Run Palm Ensemble on the two layers**

1. Open Processing Toolbox → OPTIMAL-IPB → Palm Ensemble
2. Set Layer A = `detector_a`
3. Set Layer B = `detector_b`
4. Match distance threshold = `0.02` (degrees — covers the 0.0001° offset in our synthetic data)
5. Layer A name = `detector_a`
6. Layer B name = `detector_b`
7. Click Run

- [ ] **Step 3: Verify output**

Open attribute table of the output layer.

Expected 5 features:
| confidence | source | score_a | score_b |
|-----------|--------|---------|---------|
| 1.0 | both | 0.91 | 0.88 |
| 1.0 | both | 0.85 | 0.82 |
| 0.5 | detector_a | 0.78 | NULL |
| 0.5 | detector_b | NULL | 0.60 |

(Row ordering may differ.)

- [ ] **Step 4: Test empty-layer edge case**

1. Create an empty layer:
```python
empty = make_layer('empty', [])
```

2. Run Palm Ensemble with Layer A = `empty`, Layer B = `detector_b`
3. Expected: output has 3 features, all `confidence=0.5`, `source='detector_b'`

4. Check OPTIMAL-IPB Log Messages for the warning:
```
OPTIMAL-IPB Ensemble: Layer A (empty) is empty. Returning Layer B at confidence=0.5.
```

---

### Task 6: Final Commit and Summary

- [ ] **Step 1: Create Wave 2 summary**

Write `.planning/phases/02-palm-ensemble/02-02-SUMMARY.md`:

```markdown
---
phase: 02-palm-ensemble
plan: 02
status: complete
completed: 2026-06-12
---

## Wave 2 Complete

### Files changed
- `palm_ensemble_algorithm.py` — created, PalmEnsembleAlgorithm + _get_score()
- `optimal_ipb_provider.py` — registered PalmEnsembleAlgorithm; fixed inspect.getfile icon bug
- `test/test_ensemble_algorithm.py` — created, 6 unit tests for _get_score()

### Tests
- 6 _get_score() unit tests: PASS
- QGIS toolbox: Palm Ensemble appears under OPTIMAL-IPB provider
- Synthetic layer test: confidence=1.0 for matched pairs, confidence=0.5 for unmatched
- Empty layer edge case: returns other layer at confidence=0.5 with log warning

### Acceptance criteria
- [x] PalmEnsembleAlgorithm appears in Processing Toolbox
- [x] Ensemble of two identical layers → all confidence=1.0
- [x] Ensemble with one empty layer → all confidence=0.5
- [x] source field values reflect user-supplied layer names
- [x] Syntax check passes
- [x] No crash on zero-detection input
```

- [ ] **Step 2: Final commit**

```powershell
git add .planning/phases/02-palm-ensemble/02-02-SUMMARY.md
git commit -m "feat: Wave 2 complete — PalmEnsembleAlgorithm implemented and tested"
```

---

## Wave 2 Acceptance Criteria

- [ ] `PalmEnsembleAlgorithm` appears in the Processing Toolbox under OPTIMAL-IPB
- [ ] Ensemble of two identical point layers → all points at `confidence=1.0`
- [ ] Ensemble with one empty layer → all points at `confidence=0.5`
- [ ] `source` field values reflect the user-supplied layer names, not hardcoded plugin names
- [ ] Ensemble on synthetic Layer A + Layer B → `confidence=1.0` points at midpoints of matched pairs
- [ ] Syntax check passes (`py_compile` exits 0)
- [ ] No crash when either input layer has zero features
- [ ] `optimal_ipb_provider.py` no longer imports `inspect`
