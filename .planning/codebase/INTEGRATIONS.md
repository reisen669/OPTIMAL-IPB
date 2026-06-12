# External Integrations

**Analysis Date:** 2026-06-12

## APIs & External Services

**Deep Learning Model Weights (download-time only):**
- GitHub Releases — pre-trained model weights are downloaded manually from `https://github.com/p4wlppmipb/OPTIMAL-IPB/releases` and placed in `models/`. No runtime API call; download is a one-time setup step.
- ImageNet weights (optional, training only) — `keras_retinanet/models/resnet.py` `download_imagenet()` fetches from `https://github.com/fizyr/keras-models/releases/download/v0.0.1/` via `keras.utils.get_file`. Only used during training/conversion, not during QGIS plugin inference.

**No runtime external API calls.** The plugin operates entirely offline once models are downloaded.

## Data Storage

**Databases:**
- None. The plugin does not connect to any database.

**Raster Input:**
- Source: any GDAL-supported raster file opened by the user inside QGIS (GeoTIFF, etc.)
- Access: `gdal.Open(source.source())` — file path resolved via QGIS layer registry
- Operations: `ds.ReadAsArray(x, y, winW, winH)` for sliding-window tile reads, `ds.GetGeoTransform()` for pixel-to-coordinate mapping

**Vector Output:**
- Destination: QGIS `QgsFeatureSink` (in-memory layer or user-specified file)
- Written via QGIS Processing framework: `self.parameterAsSink(...)` with CRS from source raster
- Output geometry types: Point, Bounding Box polygon, or Circle polygon

**Model Files (local filesystem):**
- Directory: `models/` relative to plugin root (`optimal_ipb_algorithm.py` line 81 resolves via `inspect.getfile`)
- Formats: `.h5` (Keras HDF5) — only these are enumerated at algorithm init time
- SavedModel and `.onnx` formats exist on disk but are not loaded by current code

**File Storage:**
- Local filesystem only. No cloud object storage.

**Caching:**
- None. No HTTP cache, no model prediction cache. Each algorithm run reloads the model from disk.

## Authentication & Identity

**Auth Provider:**
- None. No authentication of any kind. The plugin has no user accounts, no tokens, no OAuth flows.

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry, Rollbar, or equivalent.

**Logs:**
- `QgsMessageLog` — imported in `optimal_ipb_algorithm.py` but not actively called in the current inference path (imported, unused)
- Standard Python `logging` module — used in `test/test_init.py` via `logging.getLogger('QGIS')`
- User-facing errors shown via `QMessageBox.information(...)` — e.g., when no `.h5` model files are found (`optimal_ipb_algorithm.py` line 232)

## CI/CD & Deployment

**Hosting:**
- GitHub: `https://github.com/p4wlppmipb/OPTIMAL-IPB`
- Issue tracker: `https://github.com/p4wlppmipb/OPTIMAL-IPB/issues`

**CI Pipeline:**
- GitHub Actions — `.github/workflows/codeql-analysis.yml`
  - Triggers: push to `master`, pull requests to `master`, weekly cron (Wednesday)
  - Jobs: CodeQL static analysis for Python and JavaScript
  - Runner: `ubuntu-latest`
  - No test execution, no build step in CI

**Deployment:**
- Manual: user copies plugin directory to QGIS plugins path or uses QGIS Plugin Manager
- `pb_tool.cfg` configures `pb_tool` for local deployment to QGIS plugin directory
- No automated deployment pipeline

## Environment Configuration

**Required setup (no env vars — path is hardcoded):**
- `C:\Users\suily\miniconda3\envs\qgis_gdal_env` — conda env providing geospatial dependencies; path is hardcoded in `__init__.py` line 34. Must exist on the target machine.
- `tensorflow` ≥ 2.3, `tf_keras`, `keras-resnet==0.2.0`, `lsnms` — must be pip-installed into the Python environment visible to QGIS (either the QGIS Python itself or accessible via another `sys.path` injection). Currently absent from `qgis_gdal_env`.
- Pre-trained `.h5` model file(s) — must be placed in `models/` before first use; plugin shows `QMessageBox` warning if none found.

**Secrets location:**
- None. No secrets, API keys, or credentials of any kind.

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None.

## QGIS Framework Integration

**Processing Provider registration:**
- `OptimalIpbPlugin.initProcessing()` in `optimal_ipb.py` line 57-59: registers `OptimalIpbProvider` with `QgsApplication.processingRegistry()`
- Algorithm ID: `"Calculate:OPTIMAL-IPB"` — used by `processing.execAlgorithmDialog(...)` in `optimal_ipb.py` line 78

**Menu / Toolbar:**
- Menu: `&Calculate` → `OPTIMAL-IPB` action
- Toolbar: icon added to QGIS main toolbar

**QGIS Geometry API:**
- `QgsGeometry.fromPolygonXY` — bounding box output
- `QgsCircle.fromCenterDiameter(...).toPolygon().asWkt()` — circle output
- `QgsPoint` / `QgsPointXY` — point output and coordinate construction
- All geometry uses the CRS of the input raster layer (no reprojection performed)

---

*Integration audit: 2026-06-12*
