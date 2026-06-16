# 02-04 Source Report — Model Checkpoints and GeoTIFF Samples

**Generated:** 2026-06-16
**Plan:** 02-04 (Wave 4)
**Purpose:** Record all sources probed for ONNX models and GeoTIFF palm plantation imagery at 10 cm/px–1.0 m/px GSD

---

## Model Checkpoints

| Name | Source URL | GSD Range | Architecture / Format | License | Local Path | Notes |
|------|-----------|-----------|-----------------------|---------|------------|-------|
| tree_tops_yolov9.onnx | https://chmura.put.poznan.pl/s/A9zdp4mKAATEAGu | 10 cm/px | YOLOv9, ONNX | Deepness zoo (CC/academic) | models/tree_tops_yolov9.onnx | ALREADY PRESENT — not re-downloaded. CONFIRMED INCOMPATIBLE with 50 cm/px raster (5× scale mismatch). Deepness zoo page fetched 2026-06-16, STATUS 200, 27904 bytes. |
| (Source A — Deepness zoo: Airbus Planes Detection) | https://chmura.put.poznan.pl/s/bBIJ5FDPgyQvJ49 | 70 cm/px | YOLOv7 tiny, ONNX | Deepness zoo (CC/academic) | Not downloaded — wrong domain (aircraft/satellite, not palm) and 70 cm/px coarser than ideal, but no palm class; planes detection only | Fetched zoo page 2026-06-16. Model is for airplane detection on satellite imagery, not vegetation/palm. |
| (Source A — Deepness zoo: Airbus Oil Storage Detection) | https://chmura.put.poznan.pl/s/gMundpKsYUC7sNb | 150 cm/px | YOLOv5-m, ONNX | Deepness zoo (CC/academic) | Not downloaded — 150 cm/px (coarser than 1 m/px target range), oil storage tanks class only | Fetched zoo page 2026-06-16. Outside GSD range and wrong object class. |
| (Source A — Deepness zoo: Aerial Cars Detection) | https://chmura.put.poznan.pl/s/vgOeUN4H4tGsrGm | 10 cm/px | YOLOv7-m, ONNX | Deepness zoo (CC/academic) | Not downloaded — 10 cm/px matches tree_tops training GSD but detects cars (not vegetation); provides no advantage over tree_tops_yolov9 for palm counting | Fetched zoo page 2026-06-16. Same GSD as existing model, wrong class. |
| (Source A — Deepness zoo: UAVVaste Instance Segmentation) | https://chmura.put.poznan.pl/s/v99rDlSPbyNpOCH | 0.5 cm/px | YOLOv8-L, ONNX | Deepness zoo (CC/academic) | Not downloaded — 0.5 cm/px (ultra-fine UAV, litter detection); GSD 100× finer than test raster | Fetched zoo page 2026-06-16. Instance segmentation for litter, not palm trees. |
| (Source A — Deepness zoo: Ship Detection) | https://github.com/ArturWoz/ship-detection/releases/download/release/ship-detection-model.onnx | 30 cm/px | YOLOv8s, ONNX | MIT | Not downloaded — 30 cm/px but detects ships on water, not palms on land; no palm class | Fetched zoo page 2026-06-16. Ship detection model with no palm relevance. |
| (Source A — Deepness secondary zoo) | https://deepness-models.put.poznan.pl | — | — | — | Not downloaded — DNS resolution failed (name could not be resolved); domain is not live | Fetch attempted 2026-06-16; `The remote name could not be resolved: 'deepness-models.put.poznan.pl'`. |
| (Source B — HuggingFace: tribber93/yolov11-palm-oil-tree) | https://huggingface.co/tribber93/yolov11-palm-oil-tree | unconfirmed aerial | YOLOv11, PyTorch | Not specified | Not downloaded — repository contains only .pt weights (best.pt, last.pt), no ONNX export; 0 downloads | API query returned siblings: weights/best.pt, weights/last.pt. No .onnx file present. Requires export via ultralytics — see RESEARCH.md §ONNX Export Workflow. |
| (Source B — HuggingFace: grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm) | https://huggingface.co/grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm | unconfirmed | YOLOv8n-GhostNet-CBAM, PyTorch | MIT | Not downloaded — repository contains only best.pt (3.45 MB), no ONNX export | API query returned siblings: README.md, best.pt. Custom architecture (GhostNet+CBAM backbone). No .onnx file present. |
| (Source B — HuggingFace: firdhokk/palm-tree-detection-with-rtdetr) | https://huggingface.co/firdhokk/palm-tree-detection-with-rtdetr-rd50vd-coco-o365 | unconfirmed | RT-DETR, Safetensors | Not specified | Not downloaded — SafeTensors format (42.9M params, 3.59 GB), not ONNX; RT-DETR architecture incompatible with Deepness YOLO pipeline | API query returned model.safetensors only; no .onnx file. |
| (Source B — HuggingFace oil palm onnx search) | https://huggingface.co/api/models?search=oil+palm+detection&library=onnx | — | — | — | Not downloaded — API returned 7 results, none with ONNX files; all are PyTorch (.pt), SafeTensors, CSV, or LLM models | Search performed 2026-06-16 via HuggingFace API. No aerial palm detection ONNX model found. |
| (Source B — HuggingFace palm tree onnx search) | https://huggingface.co/api/models?search=palm+tree+detection&library=onnx | — | — | — | Not downloaded — API returned 8 results; none are aerial detection ONNX models (allennlp image-to-3d, LLMs, etc.) | Search performed 2026-06-16 via HuggingFace API. No relevant aerial detection ONNX model found. |
| (Source B — HuggingFace tree detection aerial onnx) | https://huggingface.co/api/models?search=tree+detection+aerial&library=onnx | — | — | — | Not downloaded — API returned 0 results (empty array) | Search performed 2026-06-16 via HuggingFace API. Zero matches. |
| (Source C — Roboflow Manfred Michael oil-palm-detection) | https://universe.roboflow.com/manfred-michael/oil-palm-detection | unconfirmed aerial | YOLOv5/v7/v8/v9/v11 available | Roboflow public | Not downloaded — page returned HTTP 403 Forbidden | Fetch attempted 2026-06-16. 403 status. Known from RESEARCH.md (prior searches also returned 403). 4,063 images; .pt weights require Roboflow API key; export workflow available in RESEARCH.md. |
| (Source C2 — Roboflow UiTM oil-palm-aerial-detection) | https://universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection | unconfirmed aerial | YOLOv8 (assumed) | Roboflow public | Not downloaded — page returned HTTP 403 Forbidden | Fetch attempted 2026-06-16. 403 status. 8,532 images; .pt weights require Roboflow API key. |
| (Source D — GitHub: kaykyysee/PalmOilClassification) | https://github.com/kaykyysee/PalmOilClassification | ground-level close-up | YOLOv8, PyTorch | Not specified | Not downloaded — repository contains best.pt only (6.29 MB, ground-level FFB bunch classification), no ONNX; wrong domain (fruit bunch grading at mill, not aerial plantation counting) | API confirmed: no releases, no ONNX file. `description`: YOLOv8-based detection of palm oil fruit bunches (Matang/Mentah/Cacat) at mill. Not aerial. |
| (Source D — GitHub: Chris-pter/Oil-Palm-Tree-Detection-with-YOLOv8) | https://github.com/Chris-pter/Oil-Palm-Tree-Detection-with-YOLOv8 | unconfirmed aerial | YOLOv8, PyTorch | MIT | Not downloaded — Weights/best.pt (5.96 MB) and Weights/last.pt only; no ONNX export present in repo | API confirmed: Weights/ dir contains best.pt, last.pt. Images/ dir contains JPEG tiles (not GeoTIFF). No releases with ONNX assets. |
| (Source D — GitHub search oil palm detection onnx) | https://api.github.com/search/repositories?q=oil+palm+detection+onnx | — | — | — | Not found — GitHub search returned 1 result (kaykyysee/PalmOilClassification, documented above); no repos with ONNX release assets for aerial palm detection | Search performed 2026-06-16. |
| (Source D — GitHub search palm tree yolo onnx) | https://api.github.com/search/repositories?q=palm+tree+yolo+onnx | — | — | — | Not found — GitHub search returned 0 results | Search performed 2026-06-16. |
| (Source E — Zenodo oil palm detection onnx) | https://zenodo.org/api/records?q=%22oil+palm%22+%22onnx%22 | — | — | — | Not downloaded — API returned 5 records, all unrelated to palm aerial detection (phytoplankton CNN, gut analysis, vegetable oils chemistry PDFs) | Search performed 2026-06-16 via Zenodo API. No aerial palm detection ONNX model found. |
| (Source E — Zenodo palm onnx model) | https://zenodo.org/api/records?q=palm+onnx+model | — | — | — | Not downloaded — API returned results unrelated to palm tree detection (neuron segmentation models, gut toolbox) | Search performed 2026-06-16. No relevant ONNX model found. |

---

## GeoTIFF Palm Plantation Samples

| Name | Source URL | GSD (m/px) | CRS | Region | Bands | File Size | License | Local Path | Notes |
|------|-----------|------------|-----|--------|-------|-----------|---------|------------|-------|
| oam_perak_01E2b_0.05mpx.tif | https://oin-hotosm-temp.s3.amazonaws.com/5bac980896c12c000583b0cc/0/5bac980896c12c000583b0cd.tif | 0.05 m/px (5 cm/px) | EPSG:32647 (WGS 84 / UTM zone 47N) | Perak, Malaysia (98°15'E, 2°07'N) | 3 (RGB, uint8) | 30.44 MB | CC-BY 4.0 (OpenAerialMap) | tif_online_samples/oam_perak_01E2b_0.05mpx.tif | Pixel Size: (0.049996, -0.049998) m. Size: 6567×14978 px. Corner: 98°15'02"E, 2°07'10"N. Perak, Malaysia — palm belt region. JPEG-compressed COG. gdalinfo confirmed: geotransform present, valid_percent=100%, no nodata issues. |
| oam_rupat_indonesia_0.088mpx.tif | https://oin-hotosm-temp.s3.us-east-1.amazonaws.com/68107f545a239162fb6d6d60/0/68107f545a239162fb6d6d61.tif | 0.088 m/px (8.8 cm/px) | EPSG:32647 (WGS 84 / UTM zone 47N) | Pulau Rupat, Riau, Indonesia (101°39'E, 2°07'N) | 3 (RGB, uint8) | 5.16 MB | CC-BY 4.0 (OpenAerialMap) | tif_online_samples/oam_rupat_indonesia_0.088mpx.tif | Pixel Size: (0.088249, -0.088251) m. Size: 7807×4782 px. UAV survey over Pulau Rupat, Riau — Sumatra palm plantation island. 40.83% valid pixels (cloud/nodata mask). JPEG-compressed COG. |
| oam_leuhan_aceh_0.5mpx.tif | https://oin-hotosm-temp.s3.us-east-1.amazonaws.com/65c6eb328931500001717ddc/0/65c6eb328931500001717ddd.tif | 0.5 m/px (50 cm/px) | EPSG:32647 (WGS 84 / UTM zone 47N) | Leuhan, Aceh Barat, Indonesia (96°06'E, 4°13'N) | 3 (RGB, uint8) | 0.83 MB | CC-BY 4.0 (OpenAerialMap) | tif_online_samples/oam_leuhan_aceh_0.5mpx.tif | Pixel Size: (0.5, -0.5) m. Size: 1952×2033 px. UAV survey over Aceh Barat — known palm/agricultural area. 100% valid pixels. Matches test raster GSD (50 cm/px). |
| (Source F — OpenAerialMap full result set) | https://api.openaerialmap.org/meta?has_tiled=true&resolution_from=0.1&resolution_to=1.0&bbox=95,1,119,7&limit=38 | varies | EPSG:32647 | SE Asia (MY, ID) | — | — | CC-BY 4.0 | Downloaded 3 candidates above; 35 remaining entries skipped | API returned 38 results for SE Asia bbox at 0.1–1.0 m GSD. STATUS 200. Skipped entries: 4 satellite tiles >200 MB (618–2181 MB), 1 UAV file >200 MB (240 MB), and 30 files with urban/infrastructure content not matching palm plantation context. |
| (Source G — Zenodo oil palm geotiff) | https://zenodo.org/api/records?q=oil+palm+geotiff&type=dataset | — | — | — | — | — | varies | Not downloaded — 10 records returned, all are classified land cover maps or ecological/agronomic CSV datasets, not raw RGB aerial imagery | Records include GlobalOilPalm extent maps (ZIP, 149 MB + 139 MB) and High-resolution global oil palm map 2019 (Sentinel-1/2 classified, 96.5 MB ZIP) — these are classification output rasters, not RGB aerial imagery for detection testing. |
| (Source G2 — Zenodo counting oil palm trees) | https://zenodo.org/api/records?q=%22oil+palm%22+%22counting%22+trees+aerial | — | — | — | — | — | varies | Not downloaded — returned records are PDFs, CSV data, and ecological studies; no raw GeoTIFF RGB imagery | Zenodo record 14603124 "Deep learning-based palm tree detection in unmanned aerial vehicle imagery with Mask R-CNN" contains only a PDF (1.3 MB) — no imagery dataset attached. |
| (Source H — Roboflow GeoTIFF check) | https://universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection | — | — | — | — | — | Roboflow | Not downloaded — page returned HTTP 403 Forbidden; Roboflow stores images as JPEG tiles by default, no GeoTIFF export format offered | Fetch attempted 2026-06-16. Same 403 as Task 1 Source C2. |
| (Source H — Roboflow Manfred Michael GeoTIFF) | https://universe.roboflow.com/manfred-michael/oil-palm-detection | — | — | — | — | — | Roboflow | Not downloaded — page returned HTTP 403 Forbidden | Fetch attempted 2026-06-16. Same 403 as Task 1 Source C. |
| (Source I — IEEE DataPort oil palm) | https://ieee-dataport.org/search#advanced/search?query=oil+palm+detection+geotiff | — | — | — | — | — | varies | Not downloaded — page returned HTTP 200 but showed 10 non-palm dataset links (eddy current NDT, weather data, UAV swarm networks, etc.) — search results are keyword-unrelated and no palm aerial GeoTIFF dataset with open download was listed | Fetched 2026-06-16. IEEE DataPort requires registration/subscription for most datasets; search results not relevant to palm aerial detection. |
| (Source J — Deepness zoo sample imagery) | https://qgis-plugin-deepness.readthedocs.io/en/latest/main/main_model_zoo.html | — | — | — | — | — | varies | Not downloaded — zoo page (STATUS 200, 27904 bytes) contains no .tif download links; all download links are ONNX model files on chmura.put.poznan.pl or GitHub release .onnx assets | Fetched 2026-06-16. No sample TIF imagery linked from the zoo page. |
| (Source K — GitHub oil palm detection geotiff) | https://api.github.com/search/repositories?q=oil+palm+detection+geotiff+sample | — | — | — | — | — | varies | Not downloaded — GitHub API returned 0 results for this query | Search performed 2026-06-16. |
| (Source K — GitHub palm-tree-detection topic) | https://api.github.com/search/repositories?q=topic:palm-tree-detection | — | — | — | — | — | varies | Not downloaded — GitHub API returned 0 repositories with this topic | Search performed 2026-06-16. |
| (Source K — GitHub palm tree aerial detection dataset) | https://api.github.com/search/repositories?q=palm+tree+aerial+detection+dataset | — | — | — | — | — | varies | Not downloaded — 2 results returned (Chris-pter/Oil-Palm-Tree-Detection-with-YOLOv8 and balasivak/Palm-Tree-Detection-YOLOV8); both contain JPEG tiles only, no GeoTIFF sample data | Chris-pter repo has Weights/best.pt + JPEG tiles; balasivak has Flask app + results CSV only. No GeoTIFF in either. |

---

## Summary

**Models downloaded (new):** 0 new ONNX files added to models/

**Models already present:** tree_tops_yolov9.onnx (10 cm/px, YOLOv9), Geoeye-Resnet101.onnx (~50 cm/px, RetinaNet), Google-Resnet101.onnx (~50 cm/px, RetinaNet), Pleiades-Resnet101.onnx (~50 cm/px, RetinaNet)

**Why no new model was downloaded:**
- Deepness zoo (Source A): No palm-specific detection model; all other detection models are for planes, oil tanks, cars, ships, litter — wrong class. No model at 50 cm/px – 1 m/px GSD exists in the zoo.
- HuggingFace (Source B): 3 palm-related YOLO models found, but all store only `.pt` PyTorch weights. No ONNX export present. ONNX export is possible via ultralytics (see RESEARCH.md §ONNX Export Workflow) but requires separate manual step.
- Roboflow (Sources C, C2): Both pages returned HTTP 403 Forbidden. Weights require Roboflow API key (not public-downloadable ONNX).
- GitHub (Source D): 2 relevant repos found; both have `.pt` weights only, no ONNX export. kaykyysee/PalmOilClassification is for ground-level fruit bunch classification (not aerial counting).
- Zenodo (Source E): 0 relevant ONNX model records found for aerial palm detection.

**GeoTIFFs downloaded:** 3 files added to tif_online_samples/

| File | GSD | Region | Size |
|------|-----|--------|------|
| oam_perak_01E2b_0.05mpx.tif | 5 cm/px | Perak, Malaysia | 30.44 MB |
| oam_rupat_indonesia_0.088mpx.tif | 8.8 cm/px | Pulau Rupat, Riau, Indonesia | 5.16 MB |
| oam_leuhan_aceh_0.5mpx.tif | 50 cm/px | Leuhan, Aceh Barat, Indonesia | 0.83 MB |

**Next steps (per ENS-01/ENS-02 requirements):**

- **Path A — Use fine-GSD TIF with existing tree_tops_yolov9.onnx:** The Perak TIF (5 cm/px) and Rupat TIF (8.8 cm/px) are close to tree_tops training GSD (10 cm/px). Re-run tree_tops_yolov9.onnx in Deepness against oam_perak_01E2b_0.05mpx.tif — crown diameter should now be 50–75 px, matching training data. **This resolves the resolution mismatch for tree_tops without any new model.**

- **Path B — Export palm-specific ONNX from HuggingFace .pt weights:** Use ultralytics ONNX export (RESEARCH.md §ONNX Export Workflow) with tribber93/yolov11-palm-oil-tree (best.pt, YOLOv11) or grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm (best.pt, YOLOv8n) in SuperMap Python (torch 2.7.0+cu126). Patch ONNX metadata for Deepness. GSD unknown — must test empirically.

- **Path C — Use 50 cm/px TIF with OPTIMAL-IPB RetinaNet models:** oam_leuhan_aceh_0.5mpx.tif at 50 cm/px matches Geoeye-Resnet101/Pleiades-Resnet101/Google-Resnet101 training GSD (~0.5 m). Run OPTIMAL-IPB on this new Aceh imagery to validate Plugin A on a different geographic region.

- **Recommended next step for 02-03 resolution-mismatch problem:** Execute Path A first — load oam_perak_01E2b_0.05mpx.tif in QGIS, run Deepness with tree_tops_yolov9.onnx at 5 cm/px tile resolution, confidence 0.25. If detections appear, the resolution mismatch is solved without any new model download.
