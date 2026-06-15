# Palm Detection Candidate Log

## Research date: 2026-06-15

## Ranking criteria

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Install complexity | high | Must work on Windows + Python 3.12 without custom builds |
| Output type | high | Must produce point or polygon — raster-only disqualifies |
| Palm/aerial suitability | medium | Pre-trained on tropical aerial/satellite RGB imagery preferred |
| QGIS 3.44 integration | medium | Native Processing algorithm preferred over scripted wrappers |
| P312 compatibility | required | Must run under QGIS 3.44's Python 3.12 |

---

## Ranked Candidates

### C1: OPTIMAL-IPB (current plugin)

- **Install:** Already installed at `plugins/optimal-ipb/` — no action needed
- **Output:** Point layer (centroids) with score field `score`
- **P312 compatible:** Yes — verified working after Phase 1 fixes
- **Windows compatible:** Yes
- **License:** (project-internal)
- **QGIS integration:** Native Processing algorithm in OPTIMAL-IPB provider
- **Model:** RetinaNet ONNX (Geoeye-Resnet101, Pleiades-Resnet101, Google-Resnet101) — trained on tropical palm aerial imagery at ~0.5 m GSD
- **Score range:** 0.0–1.0 (model confidence)
- **Notes:** Already fixed and verified in Phase 1. Strongest palm suitability of all candidates (model trained specifically on oil palm from satellite). Serves as Plugin A by default.

---

### C2: Deepness

- **Install:** QGIS Plugin Manager → search "Deepness" → Install
  - GitHub: https://github.com/PUTvision/qgis-plugin-deepness
  - No extra pip/conda installs required (bundles onnxruntime)
- **Output:** Polygon (bounding boxes) — centroid extraction needed for ensemble
- **P312 compatible:** Yes — uses onnxruntime, confirmed on QGIS 3.x / Python 3.9+; Python 3.12 expected to work
- **Windows compatible:** Yes
- **License:** MIT
- **QGIS integration:** Native Processing algorithms (Detection, Segmentation, Regression)
- **Model format:** ONNX — but expects YOLO-style output tensors, NOT the RetinaNet `filtered_detections` format our models use. Must use Deepness's own model zoo or a compatible detection model.
- **Model zoo:** Deepness hosts pre-trained models at https://deepness-models.put.poznan.pl — includes vegetation and agricultural detection models; palm-specific availability unverified.
- **Score field:** `score` (Deepness polygon attribute)
- **Notes:** Best external QGIS plugin option. Proper plugin manager install, native Processing, active maintenance (last release 2024). Main risk: finding a detection model that fires on tropical palms from ESRI imagery. If no suitable model is in the zoo, detection results may be poor.

---

### C3: DeepForest

- **Install:** `pip install deepforest` into qgis_gdal_env, then wrap as a custom Processing algorithm
  ```powershell
  & "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m pip install deepforest
  ```
- **Output:** Bounding boxes (GeoDataFrame / CSV) → requires a wrapper script to write as a polygon or point layer to QGIS
- **P312 compatible:** Likely yes (PyTorch dependency; recent deepforest 1.x targets Python 3.8+, should work on 3.12)
- **Windows compatible:** Yes
- **License:** MIT
- **QGIS integration:** None native — requires writing a Processing algorithm wrapper (~50 lines)
- **Model:** Pre-trained RetinaNet for tree crown detection (trained on North American aerial RGB, 0.1–1.0 m GSD). Not palm-specific but generalises to tropical tree crowns.
- **Score field:** `score` (GeoDataFrame column)
- **Notes:** Higher install complexity than Deepness (PyTorch is a ~2 GB dependency; requires wrapper code). Detection quality on Malaysian palm plantations unverified — model was trained on temperate forests. Viable fallback if Deepness fails.

---

## Install plan

| Order | Plugin | Slot targeted | Rationale |
|-------|--------|---------------|-----------|
| 1 | OPTIMAL-IPB (C1) | Plugin A | Already working — confirm on shared test raster |
| 2 | Deepness (C2) | Plugin B | Easiest install, native QGIS, most likely to work |
| 3 | DeepForest (C3) | Plugin B fallback | Only if Deepness produces no useful detections |

**Test raster (shared):** `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.5mpx.tif`
- 1284×956 px, 0.5 m GSD, RGB — best match to training resolution of all candidates

---

## Results

| Plugin | Slot | Install | QGIS load | Output | Score field | Decision |
|--------|------|---------|-----------|--------|-------------|----------|
| OPTIMAL-IPB | A | — | — | — | `score` | pending test |
| Deepness | B | — | — | — | `NONE (geometry only)` | pending — see 02-03-PLAN.md |
| DeepForest | B fallback | — | — | — | `score` | conditional |

Plugin A: TBD after testing
Plugin B: TBD after testing
