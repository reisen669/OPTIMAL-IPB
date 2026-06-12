# Testing Patterns

**Analysis Date:** 2026-06-12

## Test Framework

**Runner:**
- `unittest` (Python standard library) — no pytest, no nose in current test files
- Makefile (`make test`) historically called `nosetests` with `--with-coverage`, but nosetests is not installed; this target is effectively broken on the current setup
- `setup.cfg` contains a `[tool:pytest]` section with flake8 ignore rules, suggesting pytest was considered but is not actively used

**Assertion Library:**
- `unittest.TestCase` methods: `assertEqual`, `assertIn`
- One bare `assert` statement (non-TestCase style) in `test_init.py`

**Run Commands:**
```bash
# No working automated test runner is configured.
# Makefile target (historically used, currently broken):
make test    # calls nosetests — not installed

# Manual approach (requires QGIS Python environment):
python -m unittest discover -s test -p "test_*.py"

# Individual test file:
python -m unittest test.test_init
python -m unittest test.test_qgis_environment
python -m unittest test.test_translations
```

---

## Test File Organization

**Location:**
All tests are in `test/` directory (separate from source, not co-located).

**Naming:**
- Test files: `test_<subject>.py`
- Test classes: `PascalCase` ending in `Test` (e.g., `TestInit`, `QGISTest`, `SafeTranslationsTest`)
- Test methods: `test_<what_is_tested>` (e.g., `test_read_init`, `test_qgis_environment`, `test_projection`, `test_qgis_translations`)

**Structure:**
```
test/
├── __init__.py          # Imports qgis to set correct SIP API version
├── qgis_interface.py    # Stub QgisInterface for testing without full QGIS GUI
├── utilities.py         # get_qgis_app() shared setup helper
├── test_init.py         # Tests metadata.txt validity
├── test_qgis_environment.py  # Tests QGIS providers and CRS parsing
└── test_translations.py # Tests i18n translation loading
```

---

## Test Infrastructure

### QGIS Application Bootstrap

All tests requiring QGIS must call `get_qgis_app()` from `test/utilities.py` before any QGIS API use. This function initializes a `QgsApplication` singleton and returns `(QGIS_APP, CANVAS, IFACE, PARENT)`.

```python
from .utilities import get_qgis_app
QGIS_APP = get_qgis_app()  # Module-level call — runs at import time
```

`get_qgis_app()` guards against QGIS being unavailable:
```python
try:
    from qgis.core import QgsApplication
    ...
except ImportError:
    return None, None, None, None
```

### QgisInterface Stub

`test/qgis_interface.py` provides `QgisInterface(QObject)`, a stub implementation of the QGIS plugin interface. Most methods are no-ops (`pass`). It connects to `QgsMapLayerRegistry` signals to maintain a basic canvas layer set.

**Note:** `QgsMapLayerRegistry` was removed in QGIS 3.x (replaced by `QgsProject.instance()`). The stub in `qgis_interface.py` uses the QGIS 2.x API — it will fail at import time in QGIS 3.x environments. This is a known compatibility issue.

### test/__init__.py

Imports `qgis` as the first action to ensure the correct SIP API version is set before any other qgis imports:
```python
import qgis   # pylint: disable=W0611  # NOQA
```

---

## Test Structure

**Suite Organization:**
```python
class TestInit(unittest.TestCase):

    def test_read_init(self):
        """Test that the plugin __init__ will validate on plugins.qgis.org."""
        required_metadata = ['name', 'description', 'version', ...]
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.pardir, 'metadata.txt'))
        parser = configparser.ConfigParser()
        parser.read(file_path)
        assert parser.has_section('general'), message
        for expectation in required_metadata:
            self.assertIn(expectation, dict(metadata), message)

if __name__ == '__main__':
    unittest.main()
```

All three test files follow the same structure:
1. Module-level constants (`__author__`, `__date__`, `__copyright__`)
2. Optional module-level QGIS app initialization
3. Single `unittest.TestCase` subclass
4. One or more `test_*` methods
5. `if __name__ == '__main__': unittest.main()` guard

**setUp / tearDown:**
Only `SafeTranslationsTest` uses setUp/tearDown — both remove the `LANG` environment variable to ensure test isolation:
```python
def setUp(self):
    if 'LANG' in iter(os.environ.keys()):
        os.environ.__delitem__('LANG')

def tearDown(self):
    if 'LANG' in iter(os.environ.keys()):
        os.environ.__delitem__('LANG')
```

---

## Mocking

**Framework:** None — no `unittest.mock`, no third-party mocking library is used.

**Approach:** Test infrastructure uses a hand-written stub (`QgisInterface`) rather than mocking. The stub lives permanently in `test/qgis_interface.py` rather than being created per-test.

**What is faked:**
- The QGIS interface (`iface`) is replaced by `QgisInterface` stub
- A real `QgsApplication` is started (not mocked) via `get_qgis_app()`

**What is NOT faked:**
- QGIS core providers (gdal, ogr) — the environment tests assert real provider registration
- CRS parsing — uses a real `QgsCoordinateReferenceSystem` object

---

## Fixtures and Test Data

**Raster fixture:**
`test/tenbytenraster.asc` — referenced in `test_qgis_environment.py` to test raster layer loading and CRS detection:
```python
path = os.path.join(os.path.dirname(__file__), 'tenbytenraster.asc')
layer = QgsRasterLayer(path, title)
```

**Translation fixture:**
`i18n/af.qm` — compiled Afrikaans translation file used in `test_translations.py` to verify Qt translation loading works. Expected translation: `'Good morning'` → `'Goeie more'`.

**Metadata fixture:**
`metadata.txt` — read by `test_init.py` via `configparser` to validate required QGIS plugin metadata fields are present.

No factory functions or fixture factories exist. Test data is loaded directly from files using `os.path`.

---

## Coverage

**Requirements:** None enforced. No coverage configuration in `setup.cfg` or any CI file.

**Historical coverage command** (from Makefile, currently broken):
```bash
nosetests -v --with-id --with-coverage --cover-package=.
```

**What is tested:**
- `metadata.txt` has required QGIS plugin fields (name, description, version, qgisMinimumVersion, email, author)
- QGIS environment has gdal, ogr, postgres providers registered
- QGIS CRS parsing from WKT string produces correct EPSG code
- Raster layer CRS detection from `.asc` file
- Qt translation loading from `.qm` file

**What is NOT tested (major gaps):**
- `optimal_ipb_algorithm.py` — `processAlgorithm`, `detect_palm`, `geom_type`, `initAlgorithm` have no tests
- `helpers.py` — `sliding_window`, `pixel2coord`, `map_uint16_to_uint8`, `non_max_suppression_fast` have no tests
- `optimal_ipb.py` — `OptimalIpbPlugin` lifecycle (initGui, unload, run) has no tests
- `optimal_ipb_provider.py` — `OptimalIpbProvider` registration has no tests
- `keras_retinanet/` — the bundled library has no tests in this repo
- Model loading from `.h5` files has no tests
- NMS (lsnms) integration has no tests
- GDAL raster reading path has no tests
- Output geometry creation (point/bbox/circle) has no tests

---

## Test Types

**Unit Tests:**
- `test_init.py` is effectively a unit test (reads a config file, checks fields)
- No pure unit tests for plugin logic exist (no tests for `helpers.py` functions)

**Integration Tests:**
- `test_qgis_environment.py` — integration test: requires a running QGIS environment with real providers
- `test_translations.py` — integration test: requires a compiled `.qm` file on disk

**E2E Tests:**
Not used. The algorithm is not exercised end-to-end in any test.

---

## Common Patterns

**Inline message on failure:**
```python
message = 'Cannot find a section named "general" in %s' % file_path
assert parser.has_section('general'), message

message = 'Cannot find metadata "%s" in metadata source (%s).' % (expectation, file_path)
self.assertIn(expectation, dict(metadata), message)
```

**Direct assertEqual for expected values:**
```python
expected_auth_id = 'EPSG:4326'
self.assertEqual(auth_id, expected_auth_id)

expected_message = 'Goeie more'
real_message = QCoreApplication.translate("@default", 'Good morning')
self.assertEqual(real_message, expected_message)
```

**Module-level QGIS app initialization (not in setUp):**
```python
QGIS_APP = get_qgis_app()  # runs when module is imported

class QGISTest(unittest.TestCase):
    def test_qgis_environment(self):
        r = QgsProviderRegistry.instance()
        self.assertIn('gdal', r.providerList())
```

---

## Adding New Tests

**Placement:**
New test files go in `test/` and must be named `test_<subject>.py`.

**QGIS bootstrap:**
If the test requires any `qgis.core` or `qgis.gui` types, call `get_qgis_app()` at module level before the test class:
```python
from .utilities import get_qgis_app
QGIS_APP = get_qgis_app()
```

**For testing plugin logic without QGIS:**
Functions in `helpers.py` (`sliding_window`, `map_uint16_to_uint8`, `pixel2coord`, `non_max_suppression_fast`) only depend on `numpy` — they can be tested without QGIS by importing directly and do not need `get_qgis_app()`.

**Template for a new test file:**
```python
# coding=utf-8
"""Tests for <subject>."""

__author__ = '<name>'
__date__ = '<YYYY-MM-DD>'
__copyright__ = '(C) <year> by <name>'

import unittest

class <Subject>Test(unittest.TestCase):
    """Test <subject>."""

    def test_<what>(self):
        """<What this verifies>."""
        # arrange
        # act
        # assert
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
```

---

*Testing analysis: 2026-06-12*
