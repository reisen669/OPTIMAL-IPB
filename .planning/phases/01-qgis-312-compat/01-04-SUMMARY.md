---
phase: 01-qgis-312-compat
plan: 04
status: complete
completed: 2026-06-15
---

## Wave 4 Complete: Multi-Resolution Imagery Download

**Objective:** Download satellite imagery for the palm plantation area at three target resolutions (0.5, 0.3, 0.1 m/px) from ESRI World Imagery.

### Output Files

| File | Resolution | Dimensions | Size | Zoom |
|------|------------|------------|------|------|
| `imagery_0.5mpx.tif` | 0.5 m/px | 1284 × 956 px | 3.5 MB | Z=18 |
| `imagery_0.3mpx.tif` | 0.3 m/px | 2140 × 1594 px | 0.3 MB | Z=19 |
| `imagery_0.1mpx.tif` | 0.1 m/px | 6419 × 4782 px | 2.8 MB | Z=20 |

### Location

- **Coordinates:** 3.388°N, 102.99°E (Johor, Malaysia)
- **Coverage:** 641.87 m × 478.17 m = 30.69 ha
- **Source:** ESRI World Imagery (Maxar/DigitalGlobe)

### Execution Notes

- All three files downloaded successfully at target zoom levels
- **No fallback needed** — ESRI has native Z=20 coverage for this location
- GDAL WMS/TMS driver used with cubic resampling
- All outputs: 3-band RGB GeoTIFF, EPSG:3857, LZW compression

### Files Created

- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.5mpx.tif`
- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.3mpx.tif`
- `sample_data_qgis/mys_lat3388N_lon10299E/imagery_0.1mpx.tif`
- `sample_data_qgis/mys_lat3388N_lon10299E/DOWNLOAD_SUMMARY.md`

### Commit

`98882f1` — feat(data): add multi-resolution ESRI imagery for Johor palm plantation

### Next Steps

These multi-resolution images can be used to:
1. Test OPTIMAL-IPB detection quality across GSD values
2. Compare detection results at 0.5, 0.3, and 0.1 m/px
3. Evaluate ensemble performance in Phase 2
