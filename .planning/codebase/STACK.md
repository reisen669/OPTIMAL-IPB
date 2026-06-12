# Technology Stack

**Analysis Date:** 2026-06-12

## Languages

**Primary:**
- Python 3.12 - All plugin logic, QGIS Processing algorithm, bundled keras_retinanet library

**Secondary:**
- Cython - Used by bundled `keras_retinanet/utils/compute_overlap.pyx` for compiled overlap computation (compiled `.pyd` artifact checked in)

## Runtime

**Environment:**
- QGIS 3.44's embedded Python 3.12 interpreter (host runtime)
- Dependencies NOT available in QGIS's own Python are injected at plugin load time via `sys.path.insert` in `__init__.py`

**Conda Environment (dependency injection):**
- Name: `qgis_gdal_env`
- Python: 3.12.12
- Path: `C:\Users\suily\miniconda3\envs\qgis_gdal_env`
- Injection code in `__init__.py` lines 34-41: inserts `Lib\site-packages` into `sys.path[0]` and adds DLL search directories via `os.add_dll_directory`

**Package Manager:**
- Conda (for `qgis_gdal_env` geospatial dependencies)
- pip (for ML dependencies that must be installed separately — not yet present in `qgis_gdal_env`)
- No lockfile committed to the repository

## Frameworks

**Core:**
- QGIS Processing Framework (QgsProcessingAlgorithm / QgsProcessingProvider) — plugin registers as a QGIS Processing provider via `OptimalIpbProvider` → `OptimalIpbAlgorithm`
- PyQt5 / qgis.PyQt — GUI toolkit exposed through QGIS (QAction, QIcon, QMessageBox, QVariant)

**Deep Learning:**
- keras_retinanet (bundled, vendored fork of Fizyr's keras-retinanet) — `keras_retinanet/` directory contains the full library source. Modified for small-object (oil palm) detection.
- TensorFlow ≥ 2.3 — required by keras_retinanet (`keras_retinanet/utils/tf_version.py` enforces minimum TF 2.3.0). Accessed via `from tensorflow import keras` and `import tensorflow`
- tf_keras — preferred over `tensorflow.keras` for loading `.h5` models (Keras 2 compatibility). Loaded with fallback: `try: import tf_keras as keras; except ImportError: from tensorflow import keras` in `keras_retinanet/models/__init__.py` line 88-90
- keras_resnet — used by `ResNetBackbone` in `keras_retinanet/models/resnet.py`; provides ResNet50/101/152 with custom Keras layers

**Testing:**
- pytest (configured via `setup.cfg` `[tool:pytest]` section)
- Python `unittest` — test files in `test/` subclass `unittest.TestCase`

**Build/Dev:**
- pb_tool — QGIS Plugin Builder tool for deployment (`pb_tool.cfg`)
- Cython ≥ 0.28 — required to compile `compute_overlap.pyx` (listed in `setup.py` `setup_requires`)
- setuptools — `setup.py` wraps `setuptools` with a custom `BuildExtension` for Cython

## Key Dependencies

**Critical (must be available via QGIS Python or injected via sys.path):**
- `tensorflow` ≥ 2.3.0 — DL inference backend; NOT currently in `qgis_gdal_env` conda env; must be pip-installed separately
- `tf_keras` — Keras 2 standalone package for loading pre-trained `.h5` model files; NOT currently in `qgis_gdal_env`
- `keras_resnet` — ResNet backbone definitions; NOT currently in `qgis_gdal_env`
- `lsnms` — fast NMS (Non-Maximum Suppression) library, imported as `from lsnms import nms` in `optimal_ipb_algorithm.py` line 60; NOT currently in `qgis_gdal_env`

**Geospatial (provided by `qgis_gdal_env` conda env):**
- `gdal` 3.11.0 / `osgeo.gdal` — raster I/O, georeferencing, pixel-to-coordinate transforms; conda package `gdal-3.11.0`
- `numpy` 2.2.6 — array operations, image windowing, bbox manipulation
- `pandas` 2.3.3 — imported in `optimal_ipb_algorithm.py` but not actively used in current inference path (likely residual)
- `Pillow` 12.0.0 — image loading in keras_retinanet preprocessing utilities (`from PIL import Image`)
- `opencv-python-headless` 4.12.0 — image resize/processing in keras_retinanet utils (`import cv2`); headless variant (no GUI)
- `rasterio` 1.4.3 — available in conda env; not directly imported by plugin code (GDAL used instead)
- `geopandas` 1.1.1 — available in conda env; not directly imported by plugin code
- `shapely` 2.1.2 — available in conda env; geometry support

**Additional geospatial libraries in `qgis_gdal_env`:**
- `pyproj` 3.7.2 — CRS transformations
- `pyogrio` 0.11.1 — fast vector I/O
- `affine` 2.4.0 — affine transform utilities
- `six` 1.17.0 — Python 2/3 compatibility shim (used by keras_retinanet)

**Planned (present as model artifact, not yet wired into code):**
- `onnxruntime` — `.onnx` model file `models/Google-Resnet101.onnx` exists but no `onnxruntime` import found anywhere in the codebase; integration is not yet implemented

## Model Files

**Location:** `models/` directory (models downloaded separately; not committed to source)

**Formats present:**
- `models/Google-Resnet101.h5` — Keras HDF5 format, loaded via `keras_retinanet.models.load_model(..., backbone_name='resnet101')`
- `models/Google-Resnet101-savedmodel/` — TensorFlow SavedModel format directory (contains `saved_model.pb`, `variables/`, `assets/`, `fingerprint.pb`)
- `models/Google-Resnet101.onnx` — ONNX format; not yet used by code
- `models/Put the model you downloaded here.md` — placeholder instruction file

**Loading pattern in `optimal_ipb_algorithm.py` line 243:**
```python
model = load_model(os.path.join(cmd_folder, 'models/', model_name), backbone_name='resnet101')
```
Only `.h5` files are scanned via `os.listdir` filter `file.endswith(".h5")` (line 176-178).

## Configuration

**Environment:**
- No `.env` files; no environment variable configuration
- Conda env path is hardcoded in `__init__.py` line 34: `_CONDA_ENV = r"C:\Users\suily\miniconda3\envs\qgis_gdal_env"`
- QGIS plugin metadata in `metadata.txt`

**Runtime parameters (set via QGIS Processing dialog):**
- Input raster layer (GeoTIFF or any GDAL-supported format)
- Model selection (enum of `.h5` files in `models/`)
- mAP threshold (float 0–1, default 0.5)
- Output geometry type (Point / Bounding Box / Circle)
- Output layer (vector feature sink)

**Sliding window parameters (hardcoded in `optimal_ipb_algorithm.py` line 239):**
- Window size: 500×500 pixels
- Step size: 470 pixels (30px overlap)
- IoU threshold for NMS: 0.3

**Build:**
- `setup.py` — Cython extension build for `compute_overlap.pyx`
- `setup.cfg` — pytest / flake8 config
- `pb_tool.cfg` — QGIS plugin deployment config
- `pylintrc` — pylint configuration

## Platform Requirements

**Development:**
- Windows (hardcoded path `C:\Users\suily\miniconda3\envs\qgis_gdal_env` in `__init__.py`)
- QGIS 3.x (minimum 3.0 per `metadata.txt`; tested against 3.44)
- Miniconda/Anaconda with `qgis_gdal_env` environment
- Separately pip-installed: `tensorflow ≥ 2.3`, `tf_keras`, `keras-resnet==0.2.0`, `lsnms`

**Production:**
- Single-user Windows desktop deployment inside QGIS
- No server deployment (`server=False` in `metadata.txt`)
- No containerisation or cloud deployment detected

---

*Stack analysis: 2026-06-12*
