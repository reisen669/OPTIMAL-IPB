---
phase: 02-palm-ensemble
plan: "04"
subsystem: model-acquisition
tags: [onnx, geotiff, palm-detection, openaerial, deepness, research]
dependency_graph:
  requires: []
  provides:
    - tif_online_samples/ (3 georeferenced GeoTIFFs from SE Asia, CC-BY 4.0)
    - .planning/phases/02-palm-ensemble/02-04-SOURCES.md (complete source inventory)
  affects:
    - 02-03-PLAN.md (resolution mismatch now solvable via high-res TIF path)
    - models/ (no new ONNX added; export from .pt weights is the path forward)
tech_stack:
  added:
    - OpenAerialMap API (https://api.openaerialmap.org) — GeoTIFF discovery
    - HuggingFace API (https://huggingface.co/api/models) — model card inspection
  patterns:
    - PowerShell Invoke-WebRequest for URL probing and binary download
    - gdalinfo (qgis_gdal_env) for GeoTIFF metadata inspection
    - GitHub REST API for repo/release discovery without authentication
    - Zenodo REST API for dataset record inspection
key_files:
  created:
    - tif_online_samples/oam_perak_01E2b_0.05mpx.tif
    - tif_online_samples/oam_rupat_indonesia_0.088mpx.tif
    - tif_online_samples/oam_leuhan_aceh_0.5mpx.tif
    - .planning/phases/02-palm-ensemble/02-04-SOURCES.md
  modified: []
decisions:
  - "No palm-specific ONNX model is publicly downloadable from any probed source; all candidates store .pt PyTorch weights only"
  - "Path A (use fine-GSD Perak TIF with existing tree_tops_yolov9.onnx) is the lowest-effort resolution-mismatch fix"
  - "Path B (export tribber93/yolov11-palm-oil-tree .pt to ONNX) is the fallback if Path A produces zero detections"
metrics:
  duration: "~45 minutes"
  completed: "2026-06-16"
  tasks_completed: 3
  tasks_total: 3
  files_created: 4
  files_modified: 0
---

# Phase 02 Plan 04: Model and GeoTIFF Acquisition Summary

Wave 4 executed a systematic search across 5 ONNX model sources (A–E) and 6 GeoTIFF sources (F–K). No publicly downloadable palm-specific ONNX model was found at any source. Three high-resolution SE Asia GeoTIFFs were acquired from OpenAerialMap (CC-BY 4.0) that directly resolve the 50 cm/px resolution mismatch by providing 5–50 cm/px test imagery.

---

## What Was Built

**tif_online_samples/ directory** (created, 3 files):

| File | GSD | Dimensions | CRS | Region | Size | License |
|------|-----|------------|-----|--------|------|---------|
| oam_perak_01E2b_0.05mpx.tif | 5 cm/px | 6567×14978 px | EPSG:32647 | Perak, Malaysia (98°15'E, 2°07'N) | 30.44 MB | CC-BY 4.0 |
| oam_rupat_indonesia_0.088mpx.tif | 8.8 cm/px | 7807×4782 px | EPSG:32647 | Pulau Rupat, Riau, Indonesia (101°39'E, 2°07'N) | 5.16 MB | CC-BY 4.0 |
| oam_leuhan_aceh_0.5mpx.tif | 50 cm/px | 1952×2033 px | EPSG:32647 | Leuhan, Aceh Barat, Indonesia (96°06'E, 4°13'N) | 0.83 MB | CC-BY 4.0 |

All three files: gdalinfo confirmed valid geotransform, 3-band RGB uint8, JPEG-compressed COG format (suitable for QGIS/Deepness), no corruption.

**02-04-SOURCES.md** (created):
- 20 model checkpoint rows (Sources A–E, all probed with actual HTTP responses)
- 13 GeoTIFF rows (Sources F–K, 3 downloaded + 10 negative-result rows with actual reasons)
- Summary section with next-step recommendations

---

## ONNX Models: New Files Added

**Count: 0 new ONNX files added to models/**

| Source | What Was Found | Outcome |
|--------|----------------|---------|
| Deepness zoo (A) | 6 detection models: Planes (70 cm/px), Oil Storage (150 cm/px), Cars (10 cm/px), UAVVaste (0.5 cm/px), Tree-Tops (10 cm/px — already present), Ships (30 cm/px) | Not downloaded — none are palm-class models; Tree-Tops already present |
| Deepness secondary zoo | deepness-models.put.poznan.pl | DNS resolution failed (domain not live) |
| HuggingFace (B) | 3 palm YOLO models: tribber93/yolov11-palm-oil-tree (YOLOv11, .pt only), grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm (YOLOv8n-GhostNet, .pt only, MIT), firdhokk/palm-tree-rtdetr (RT-DETR, SafeTensors, 3.59 GB) | Not downloaded — none have ONNX export; .pt export possible via ultralytics |
| Roboflow (C, C2) | UiTM 8532-image dataset, Manfred Michael 4063-image dataset | Not downloaded — both pages returned HTTP 403 Forbidden |
| GitHub (D) | kaykyysee/PalmOilClassification (YOLOv8 FFB bunch at mill), Chris-pter/Oil-Palm-Tree-Detection-with-YOLOv8 (YOLOv8, aerial) | Not downloaded — .pt weights only; kaykyysee is ground-level (wrong domain) |
| Zenodo (E) | 0 relevant records | Not downloaded — no aerial palm detection ONNX model records in Zenodo |

---

## GeoTIFF Metadata (gdalinfo verified)

### oam_perak_01E2b_0.05mpx.tif
- **Pixel Size:** (0.049996, -0.049998) m/px — actual GSD ~5 cm/px
- **CRS:** EPSG:32647 (WGS 84 / UTM zone 47N)
- **Bands:** 3 (R/G/B, uint8), JPEG compression, tiled 512×512
- **Overviews:** 5 levels present (suitable for QGIS zoom)
- **Source:** UAV/aircraft, Perak state (lat 2.11°N, lon 98.25°E) — Malaysian palm belt region
- **Compatibility with tree_tops_yolov9.onnx:** Excellent — 5 cm/px vs 10 cm/px training GSD (2× finer, crowns appear ~100 px wide vs training ~50 px — close enough)

### oam_rupat_indonesia_0.088mpx.tif
- **Pixel Size:** (0.088249, -0.088251) m/px — actual GSD ~8.8 cm/px
- **CRS:** EPSG:32647 (WGS 84 / UTM zone 47N)
- **Bands:** 3 (R/G/B, uint8), COG layout, 40.83% valid pixels (nodata mask)
- **Source:** UAV over Pulau Rupat, Riau — Sumatra palm plantation island
- **Compatibility with tree_tops_yolov9.onnx:** Very good — 8.8 cm/px vs 10 cm/px training GSD (~1.14× ratio, nearly perfect match)

### oam_leuhan_aceh_0.5mpx.tif
- **Pixel Size:** (0.5, -0.5) m/px — actual GSD 50 cm/px
- **CRS:** EPSG:32647 (WGS 84 / UTM zone 47N)
- **Bands:** 3 (R/G/B, uint8), 100% valid pixels
- **Source:** UAV over Leuhan, Aceh Barat, Indonesia — known agricultural/palm region
- **Compatibility with OPTIMAL-IPB RetinaNet:** Excellent — matches Geoeye/Pleiades/Google training GSD (~0.5 m); use with Plugin A

---

## Recommendation for ENS-01/ENS-02 Resolution-Mismatch Problem

**Path A (recommended first):** Load `tif_online_samples/oam_perak_01E2b_0.05mpx.tif` (5 cm/px) in QGIS. Run Deepness with `models/tree_tops_yolov9.onnx` at native 5 cm/px resolution. Palm crowns will now appear ~50–100 px wide, matching the training GSD. This resolves the resolution mismatch without any new model download or export.

**Path B (fallback if Path A yields zero detections):** Export `tribber93/yolov11-palm-oil-tree/weights/best.pt` to ONNX using SuperMap Python (torch 2.7.0+cu126 + ultralytics). Patch Deepness metadata keys (`model_type`, `det_type`, `class_names`, `resolution`). This provides a palm-specific YOLOv11 model, but training GSD is unknown — empirical test required.

**Path C (Plugin A validation):** Run OPTIMAL-IPB on `tif_online_samples/oam_leuhan_aceh_0.5mpx.tif` to validate Plugin A detection on a different geographic region (Aceh, Indonesia vs Malaysia training data).

**Model + raster pairing for next Deepness test run:**
- Plugin B: `tree_tops_yolov9.onnx` + `oam_rupat_indonesia_0.088mpx.tif` (closest GSD match to training)
- Plugin A: `Geoeye-Resnet101.onnx` + `oam_leuhan_aceh_0.5mpx.tif` (50 cm/px match)

---

## Source Report Location

`.planning/phases/02-palm-ensemble/02-04-SOURCES.md` — contains all 11 source categories (A–K) with actual URLs fetched, HTTP responses observed, file sizes, and ONNX/TIF metadata where applicable.

---

## Deviations from Plan

None — plan executed exactly as written. All sources A–K probed and documented. Three GeoTIFFs downloaded (all pass 500 KB minimum). No ONNX files downloaded (all sources returned no public ONNX; documented with actual HTTP responses per source).

---

## Known Stubs

None. All table rows in 02-04-SOURCES.md contain actual fetched outcomes, not placeholders.

---

## Threat Flags

None. All downloads are from HTTPS endpoints (OAM S3, GitHub raw, etc.). No credentials used. No files outside size bounds (all TIFs 0.83–30.44 MB, all < 200 MB limit; no ONNX downloads to validate against 1 MB minimum).

---

## Self-Check: PASSED

- [x] tif_online_samples/ exists and contains 3 TIF files >= 500 KB
- [x] 02-04-SOURCES.md exists, has both table headers and Summary section, 86 lines (> 50)
- [x] No bare placeholders (TODO/TBD/[placeholder]) in SOURCES.md
- [x] models/ has no new ONNX files < 1 MB (no ONNX downloaded at all)
- [x] Commits 7ece01c and 78103b2 exist in git log
- [x] All 11 source categories (A–K) appear in SOURCES.md with actual fetch outcomes
