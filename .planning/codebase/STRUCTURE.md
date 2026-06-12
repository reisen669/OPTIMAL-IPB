<!-- refreshed: 2026-06-12 -->
# Codebase Structure

**Analysis Date:** 2026-06-12

## Directory Layout

```
optimal-ipb/                         # Plugin root — QGIS loads from here
├── __init__.py                      # QGIS entry point: classFactory(); Conda path injection
├── optimal_ipb.py                   # OptimalIpbPlugin class (lifecycle, toolbar)
├── optimal_ipb_provider.py          # OptimalIpbProvider (QgsProcessingProvider)
├── optimal_ipb_algorithm.py         # OptimalIpbAlgorithm + detect_palm() + helpers import
├── helpers.py                       # Stateless utilities: sliding_window, pixel2coord, NMS, normalise
├── metadata.txt                     # QGIS plugin metadata (name, version, qgisMinimumVersion)
├── logo.png                         # Plugin icon (used in toolbar and provider)
├── setup.py                         # setuptools for building compute_overlap Cython extension
├── setup.cfg                        # flake8 / pytest config
├── pylintrc                         # pylint config
├── pb_tool.cfg                      # pb_tool packaging config
├── Makefile                         # Developer targets (deploy, translate, clean)
│
├── models/                          # Model storage — scanned at algorithm init
│   ├── Google-Resnet101.h5          # Primary inference model (Keras 2 HDF5, ResNet101 backbone)
│   ├── Google-Resnet101.onnx        # ONNX export (conversion complete, not yet wired into UI)
│   ├── Google-Resnet101-savedmodel/ # TF SavedModel format
│   │   ├── saved_model.pb
│   │   ├── fingerprint.pb
│   │   └── variables/
│   └── Put the model you downloaded here.md  # User instruction placeholder
│
├── keras_retinanet/                 # Vendored Fizyr keras-retinanet (modified for tf_keras + py3.12)
│   ├── __init__.py                  # Empty package marker
│   ├── initializers.py              # PriorProbability Keras initializer
│   ├── losses.py                    # smooth_l1 and focal loss functions
│   ├── backend/
│   │   ├── __init__.py
│   │   └── backend.py               # TF-level ops: bbox_transform_inv, shift, map_fn, resize_images
│   ├── layers/
│   │   ├── __init__.py              # Re-exports: RegressBoxes, UpsampleLike, Anchors, ClipBoxes, FilterDetections
│   │   ├── _misc.py                 # Anchors, RegressBoxes, UpsampleLike, ClipBoxes custom layers
│   │   └── filter_detections.py     # FilterDetections custom layer + filter_detections() function
│   ├── models/
│   │   ├── __init__.py              # Backbone base class, backbone() factory, load_model(), convert_model()
│   │   ├── resnet.py                # ResNetBackbone (resnet50/101/152) — active backbone
│   │   ├── retinanet.py             # FPN head, classification/regression submodels, retinanet_bbox
│   │   ├── densenet.py              # DenseNetBackbone (unused in production)
│   │   ├── effnet.py                # EfficientNetBackbone (unused in production)
│   │   ├── mobilenet.py             # MobileNetBackbone (unused in production)
│   │   ├── senet.py                 # SeBackbone (unused in production)
│   │   └── vgg.py                   # VGGBackbone (unused in production)
│   ├── preprocessing/               # Training-only data generators (not used during inference)
│   │   ├── generator.py             # Base generator class
│   │   ├── csv_generator.py
│   │   ├── coco.py
│   │   ├── pascal_voc.py
│   │   ├── kitti.py
│   │   └── open_images.py
│   ├── callbacks/                   # Training-only Keras callbacks (not used during inference)
│   │   ├── common.py
│   │   ├── eval.py
│   │   └── coco.py
│   ├── bin/                         # Standalone training/evaluation scripts (not used by plugin)
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── debug.py
│   │   └── convert_model.py
│   └── utils/
│       ├── __init__.py
│       ├── anchors.py               # AnchorParameters, generate_anchors, anchor_targets_bbox
│       ├── image.py                 # preprocess_image(), resize_image(), VisualEffect, TransformParameters
│       ├── compute_overlap.py       # Pure-NumPy IoU fallback (for py3.12 compatibility)
│       ├── compute_overlap.pyx      # Cython source for compute_overlap
│       ├── compute_overlap.cp312-win_amd64.pyd  # Compiled for Python 3.12 Windows
│       ├── compute_overlap.cp37-win_amd64.pyd   # Compiled for Python 3.7 Windows
│       ├── config.py                # Training config utilities
│       ├── colors.py                # Label colour utilities
│       ├── eval.py                  # mAP evaluation utilities (training)
│       ├── coco_eval.py             # COCO evaluation (training)
│       ├── gpu.py                   # setup_gpu() helper
│       ├── model.py                 # freeze() model utility
│       ├── tf_version.py            # TF version check (minimum 2.3.0)
│       ├── transform.py             # Affine transform utilities
│       ├── visualization.py         # Draw boxes/labels on images
│       └── build/                   # Cython build artifacts (generated, not committed to source)
│
├── test/                            # Plugin-level tests (QGIS environment tests)
│   ├── __init__.py
│   ├── test_init.py                 # Validates metadata.txt has required fields
│   ├── test_qgis_environment.py     # Smoke test for QGIS Python environment
│   ├── test_translations.py         # i18n translation file test
│   ├── utilities.py                 # Test helpers (get_qgis_app)
│   ├── qgis_interface.py            # Stub QgsInterface for headless testing
│   └── tenbytenraster.*             # 10×10 raster test fixture (ASC + QML + PRJ)
│
├── i18n/
│   └── af.ts                        # Afrikaans translation source (Qt Linguist format)
│
├── imgs/
│   ├── Readme01.png                 # README screenshot
│   └── Readme02.png                 # README screenshot
│
├── help/
│   ├── source/                      # Sphinx source docs
│   │   ├── conf.py
│   │   └── index.rst
│   └── build/                       # Generated HTML docs (not for editing)
│
├── scripts/
│   ├── compile-strings.sh           # Qt i18n compile script
│   ├── update-strings.sh            # Extract i18n strings script
│   └── run-env-linux.sh             # Linux dev environment setup
│
├── .planning/
│   └── codebase/                    # GSD codebase map documents
│
└── .github/
    └── workflows/
        └── codeql-analysis.yml      # GitHub Actions CodeQL security scan
```

## Directory Purposes

**Plugin Root (`optimal-ipb/`):**
- Purpose: The four core Python files here constitute the entire plugin surface area visible to QGIS
- Contains: `__init__.py`, `optimal_ipb.py`, `optimal_ipb_provider.py`, `optimal_ipb_algorithm.py`, `helpers.py`
- Key files: `__init__.py` (entry point), `optimal_ipb_algorithm.py` (all inference logic)

**`models/`:**
- Purpose: Stores downloaded model weights; scanned at algorithm init for `.h5` files to populate UI enum
- Contains: `.h5` (Keras 2 HDF5), `.onnx` (ONNX export), SavedModel directory
- Key files: `Google-Resnet101.h5` — the only format currently used by `processAlgorithm()`
- Note: Only `.h5` files are auto-discovered. Place additional `.h5` files here to add them to the model dropdown.

**`keras_retinanet/`:**
- Purpose: Vendored inference library. The `models/`, `layers/`, `backend/`, and `utils/image.py` sub-modules are used during inference. The `preprocessing/`, `callbacks/`, and `bin/` sub-modules are training artefacts included for completeness but not imported at runtime.
- Contains: Backbone definitions, FPN head, custom Keras layers, anchor utilities, image preprocessing
- Key files: `models/__init__.py` (load_model), `utils/image.py` (preprocess_image/resize_image), `layers/__init__.py` (custom objects)

**`test/`:**
- Purpose: QGIS plugin validation tests — check metadata correctness and environment health, not algorithm logic
- Contains: unittest-based tests, headless QGIS stubs, one raster fixture
- Key files: `test_init.py`, `utilities.py`

**`scripts/`:**
- Purpose: Development workflow automation (i18n, environment setup)
- Contains: Bash scripts for Qt translation and Linux QGIS dev env
- Generated: No
- Committed: Yes

## Key File Locations

**Entry Points:**
- `__init__.py`: QGIS plugin loader entry — `classFactory(iface)` at line 45
- `optimal_ipb.py`: Plugin class — `OptimalIpbPlugin.initGui()` at line 61

**Configuration:**
- `metadata.txt`: QGIS plugin metadata (name, version, minimum QGIS version, tags)
- `setup.py`: Build config for `compute_overlap` Cython extension
- `pb_tool.cfg`: pb_tool packaging/deployment configuration

**Core Logic:**
- `optimal_ipb_algorithm.py`: All inference orchestration, parameter definitions, output generation
- `helpers.py`: Tile iteration, coordinate conversion, image normalisation
- `keras_retinanet/models/__init__.py`: Model loading with custom objects
- `keras_retinanet/utils/image.py`: Image preprocessing pipeline

**Testing:**
- `test/test_init.py`: Metadata field validation
- `test/test_qgis_environment.py`: QGIS Python environment smoke test

## Naming Conventions

**Files:**
- Plugin core files use `snake_case` matching the QGIS Plugin Builder convention: `optimal_ipb.py`, `optimal_ipb_algorithm.py`, `optimal_ipb_provider.py`
- Helper utilities use plain `snake_case`: `helpers.py`
- keras_retinanet files use `snake_case` with leading underscore for private modules: `_misc.py`
- Test files use `test_` prefix: `test_init.py`, `test_qgis_environment.py`

**Directories:**
- Plugin-level directories are lowercase: `models/`, `test/`, `scripts/`, `i18n/`, `imgs/`
- Vendored sub-package mirrors upstream naming: `keras_retinanet/`

**Classes:**
- Plugin classes use `PascalCase` with the `OptimalIpb` prefix: `OptimalIpbPlugin`, `OptimalIpbProvider`, `OptimalIpbAlgorithm`
- keras_retinanet classes use `PascalCase`: `ResNetBackbone`, `FilterDetections`, `AnchorParameters`

**Constants / Algorithm Parameters:**
- Algorithm parameter keys are `SCREAMING_SNAKE_CASE` string constants on the class: `INPUT`, `OUTPUT`, `OPTIMAL`, `mAP`, `TYPE`

## Where to Add New Code

**New inference backbone or model format (e.g. ONNX runtime path):**
- Backend implementation: `keras_retinanet/models/` — add a new module (e.g. `onnx_model.py`)
- Wire into UI: `optimal_ipb_algorithm.py` — update `initAlgorithm()` to scan for `.onnx` files or add a separate enum parameter
- Model loading: extend or replace the `load_model()` call in `processAlgorithm()` at line 243

**New output geometry type:**
- Add to `outputType` list at `optimal_ipb_algorithm.py:79`
- Add a corresponding branch in `geom_type()` switcher at line 137
- Add geometry construction in the output loop at lines 330–339

**New per-tile preprocessing step:**
- Add to `detect_palm()` in `optimal_ipb_algorithm.py:88`, between `ds.ReadAsArray()` and `preprocess_image()`
- Or add a new utility function to `helpers.py` and import it in `optimal_ipb_algorithm.py`

**New algorithm (second detection task):**
- Add new `QgsProcessingAlgorithm` subclass as a new file in the plugin root (e.g. `count_palms_algorithm.py`)
- Register it in `OptimalIpbProvider.loadAlgorithms()` at `optimal_ipb_provider.py:60`

**New plugin-level test:**
- Add to `test/` as `test_<feature>.py` using `unittest.TestCase`
- Use `test/utilities.py:get_qgis_app()` to get a headless QGIS instance

**Shared utility functions:**
- Geometric / image utilities with no QGIS dependency: `helpers.py`
- keras_retinanet-internal utilities: `keras_retinanet/utils/`

## Special Directories

**`keras_retinanet/utils/build/`:**
- Purpose: Cython extension build artifacts from `python setup.py build_ext`
- Generated: Yes (by setuptools/Cython)
- Committed: Partially — the `.pyd` binary at root level (`compute_overlap.cp312-win_amd64.pyd`) is committed; the `build/` subtree should be gitignored

**`help/build/`:**
- Purpose: Sphinx-generated HTML documentation
- Generated: Yes (`make html` in `help/`)
- Committed: Yes (currently)

**`__pycache__/` (throughout):**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: Should not be — no `.gitignore` entry observed

---

*Structure analysis: 2026-06-12*
