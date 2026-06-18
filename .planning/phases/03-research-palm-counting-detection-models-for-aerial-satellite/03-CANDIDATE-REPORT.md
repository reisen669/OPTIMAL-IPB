# Phase 3 Candidate Report — Palm / Tree-Crown Detection Models

**Generated:** 2026-06-18
**Phase:** 03-research-palm-counting-detection-models-for-aerial-satellite
**Purpose:** Catalog of publicly available pretrained checkpoints for palm / tree-crown detection from aerial/satellite imagery. Feeds Phase 4 model selection.
**Test rasters:**
- Perak (5 cm/px): tif_online_samples/oam_perak_01E2b_0.05mpx.tif
- Rupat (8.8 cm/px): tif_online_samples/oam_rupat_indonesia_0.088mpx.tif
- Aceh (50 cm/px): tif_online_samples/oam_leuhan_aceh_0.5mpx.tif

---

## Main Candidate Catalog

The table below lists all 10 publicly accessible candidates with pretrained weights. Baselines (B1–B4) are already present in the `models/` directory; HuggingFace candidates (H1–H3) and new VHR candidates (N1–N3) require download in Phase 4. Restricted-access candidates (R1–R3) and Baidu-only candidates (N3/N4) are documented in separate sections below — they are NOT included in this main table.

| Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm |
|------|-------------|-------------------|--------|---------|----------|-----------|-------------|-----------|
| B1: tree_tops_yolov9.onnx | YOLOv9 | 5–20 cm/px (HIGH) | .onnx | Deepness zoo (CC/academic) | No (European aerial) | ✓ | ✓ | ✗ |
| B2: Google-Resnet101.onnx | RetinaNet | 30–100 cm/px (MEDIUM) | .onnx | See OPTIMAL-IPB source | Unknown | ✗ | ✗ | ✓ |
| B3: Geoeye-Resnet101.onnx | RetinaNet | 30–100 cm/px (MEDIUM) | .onnx | See OPTIMAL-IPB source | Unknown | ✗ | ✗ | ✓ |
| B4: Pleiades-Resnet101.onnx | RetinaNet | 30–100 cm/px (MEDIUM) | .onnx | See OPTIMAL-IPB source | Unknown | ✗ | ✗ | ✓ |
| H1: tribber93/yolov11-palm-oil-tree | YOLOv11 | unknown ~5–15 cm/px (LOW) | .pt | Not specified | Unknown | ? | ? | ? |
| H2: grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm | YOLOv8n-GhostNet-CBAM | unknown aerial (LOW) | .pt (3.45 MB) | MIT | Unknown | ? | ? | ? |
| H3: firdhokk/palm-tree-detection-with-rtdetr | RT-DETR | unknown (LOW) | .safetensors (3.59 GB) | Not specified | Unknown | ? | ? | ? |
| N1: detectree2 / 230103_randresize_full.pth | Mask R-CNN (Detectron2) | 5–20 cm/px (HIGH) | .pth (498 MB) | CC BY 4.0 | YES — Sabah, Malaysia | ✓ | ✓ | ✗ |
| N2: weecology/deepforest-tree | RetinaNet (PyTorch Lightning) | 5–20 cm/px (HIGH) | .pt / Safetensors | MIT | No (US NEON) | ✓ | ✓ | ✗ |
| N3: rs-dl/MOPAD | Faster RCNN (RPF module) | 5–20 cm/px (LOW) | .pth | Not specified | YES assumed | ? | ? | ? |

**GSD confidence labels:** HIGH = confirmed from paper/README; MEDIUM = inferred from satellite provenance; LOW = assumed from typical deployment context; check README in Phase 4.

**Notes:**
- H2 (grediiiii): Custom GhostNet+CBAM backbone — ONNX export may fail; test export early in Phase 4 before committing time to this candidate.
- H3 (firdhokk): RT-DETR architecture, 3.59 GB — LOW priority; requires non-YOLO HuggingFace Transformers conversion path.
- N1 (detectree2): BLOCKER — Detectron2 Mask R-CNN format. NOT loadable with `YOLO()`. NOT Deepness-compatible without additional integration work. See Key Integration Constraints section.
- N2 (weecology/deepforest): Requires DeepForest Python library (`pip install deepforest`) for inference — not a standalone ONNX import.
- N3 (MOPAD): Weights on Baidu Wangpan only (access codes 7n61 / 8mwa) — moved to Uncertain Access section; included here for reference only.

---

**GSD Tier Summary**

- **VHR (≤15 cm/px):** B1, H1, H2, N1, N2, N3 — test rasters matched: Perak (5 cm/px), Rupat (8.8 cm/px)
- **HR (15–100 cm/px):** No confirmed publicly downloadable model in this tier. The gap between VHR drone-trained models and MR satellite-trained models is real and well-documented. MOPAD (N3) may fall in this tier but GSD and accessibility are unconfirmed.
- **MR (0.5–2 m):** B2, B3, B4 — test raster matched: Aceh (50 cm/px)

---

## Uncertain Access: Baidu Wangpan Candidates

These candidates have pretrained weights that exist but are hosted on Baidu Wangpan. International accessibility outside China is unverified. They are excluded from the main catalog until Phase 4 confirms download success.

**N3 — rs-dl/MOPAD (Multi-class Oil Palm tree detection)**
- Architecture: Faster RCNN with Refined Pyramid Feature (RPF) module, PyTorch
- GitHub: https://github.com/rs-dl/MOPAD
- Weights: Baidu Wangpan — access code `7n61` (Site 2) and `8mwa` (Site 1)
- GSD: inferred ~5–20 cm/px from UAV operations (Skywalker X8 fixed-wing UAV, large-area 28.85 km² survey over ~300,000 oil palms). Exact UAV altitude not stated in README.
- License: Not specified
- SE Asia?: YES assumed — oil palm plantation UAV dataset; ISPRS Journal 2021 paper context suggests SE Asia region
- Phase 4 action: Attempt Baidu Wangpan download first; if blocked from non-China IP, deprioritize and focus on Zenodo/HuggingFace candidates.
- Domain match: Oil-palm-specific (5 growing-status classes) — highest domain relevance in the VHR tier.

**N4 — rs-dl/MADAN (Multi-level Attention Domain Adaptation Network)**
- Architecture: Batch-instance normalization + multi-level attention domain adaptation, PyTorch
- GitHub: https://github.com/rs-dl/MADAN
- arXiv: https://arxiv.org/abs/2008.11505
- Weights: Baidu Wangpan / Google Drive — format and availability not confirmed from GitHub README alone
- GSD: inferred ~5–30 cm/px from paper abstract (high-resolution satellite imagery of Malaysia/Indonesia palm plantations)
- License: Not specified
- SE Asia?: YES — explicitly designed for cross-regional SE Asia oil palm (Malaysia, Indonesia) domain adaptation
- Phase 4 action: Read MADAN README fully and attempt Google Drive link; if weights are unavailable, skip.
- Note: Even if accessible, MADAN requires domain adaptation training infrastructure — may not produce a standalone inference checkpoint suitable for Phase 4.

---

## Restricted Access: API Key or Account Required

These candidates have pretrained models but require authentication or payment. Excluded from the main catalog per decision D-04 (publicly downloadable without login or API key).

| Name | URL | Blocker |
|------|-----|---------|
| R1: Roboflow Manfred Michael (oil-palm-detection) | https://universe.roboflow.com/manfred-michael/oil-palm-detection | HTTP 403 Forbidden; Roboflow API key required. 4,063 aerial palm images. YOLOv5–v11 .pt weights. |
| R2: Roboflow UiTM (oil-palm-aerial-detection) | https://universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection | HTTP 403 Forbidden; Roboflow API key required. 8,532 aerial palm images. YOLOv8 .pt weights. |
| R3: ArcGIS Living Atlas Palm Tree Detection | https://hub.arcgis.com/content/916e02960d9e495baeb4d1d2ff4055d0 | ArcGIS account required (free tier unconfirmed). FasterRCNN, .dlpk format, 5–15 cm/px GSD. |

---

## Excluded Candidates (No Pretrained Weights / Out of Scope)

These were found during research but excluded because they provide no publicly downloadable pretrained checkpoint.

| Candidate | Reason Excluded |
|-----------|-----------------|
| rs-dl/CROPTD (Cross-Regional Oil Palm Tree Detection) | Dataset only (PASCAL VOC format); code but no pretrained weights in repo |
| NourO93/Palm-Tree-Dataset (UAE Al Ain) | Dataset only; no weights; research-only license |
| Adeel0-0/PALM-TREE-DETECTION | Code only; no pretrained weights published — architecture descriptions only |
| Freudenberg U-Net (ThomasWangWeiHong) | Code only; no releases; train-from-scratch only |
| Kaggle riotulab/aerial-images-of-palm-trees | Dataset only; no model weights |
| Kaggle yohanesnuwara/oil-palm-detection | Dataset only; no model weights |
| arXiv:2502.13023 PRISM (Ecuador palms) | No public weights; research-only |
| arXiv:2410.11124 PalmDSNet (Ecuador) | No public weights; research-only |
| arXiv:2412.11949 Coconut YOLOv7 (Ghana) | No public weights; research-only |
| knwin/Detect-palmtrees-with-Yolo-and-ImageAI | Uses generic COCO YOLO weights, not palm-specific pretrained |
| odanylo/oilpalmSEasia | Google Earth Engine JavaScript API — not a detection model checkpoint |
| WiDS Datathon 2019 (Kaggle, ResNeXt101) | Satellite classification only (not individual tree detection); no public checkpoint |

---

## Sources Probed

All 11 source categories were probed during Phase 3 research. Phase 2 sources (A–E) were revisited to build on prior findings; categories F–K are new to Phase 3.

| # | Source Category | Platform | Result |
|---|----------------|----------|--------|
| A | Deepness zoo | chmura.put.poznan.pl | 0 new palm models; all non-palm classes. Already probed in Phase 2. SKIP. |
| B | HuggingFace | huggingface.co | H1 (tribber93), H2 (grediiiii), H3 (firdhokk) found in Phase 2; N2 (weecology/deepforest-tree) added in Phase 3. DONE. |
| C | Roboflow | universe.roboflow.com | R1 (Manfred Michael), R2 (UiTM) found but HTTP 403 Forbidden on both. BLOCKED. |
| D | GitHub | github.com | N1 (detectree2 / PatBall1), N3 (MOPAD / rs-dl), N4 (MADAN / rs-dl) + 2 Phase 2 repos. DONE. |
| E | Zenodo | zenodo.org | N1 detectree2 weights confirmed at record 12773341 (7 .pth files, CC BY 4.0). DONE. |
| F | Papers With Code | paperswithcode.com | BROKEN — site redirects to HuggingFace trending. Use arXiv directly instead. N/A. |
| G | arXiv | arxiv.org | 5+ papers found; most have no public weights. MADAN (2008.11505), PalmDSNet (2410.11124), PRISM (2502.13023). DONE. |
| H | IEEE Xplore | ieeexplore.ieee.org | Papers behind paywall; no associated public weights found. PARTIAL. |
| I | Kaggle | kaggle.com | Dataset-only entries; no pretrained checkpoint files published. DONE. |
| J | Google Dataset Search | datasetsearch.research.google.com | Redirects to other sources; no new checkpoints found beyond GitHub/Zenodo/HuggingFace. DONE. |
| K | ArcGIS Living Atlas | hub.arcgis.com | R3 (ArcGIS Palm Tree Detection, FasterRCNN, .dlpk) — ArcGIS account required. BLOCKED. |

---

## Key Integration Constraints for Phase 4

These constraints must be understood before selecting which candidates to pursue in Phase 4.

**1. detectree2 (N1) — Detectron2 format, NOT Deepness-compatible**

The recommended file `230103_randresize_full.pth` is a Detectron2 Mask R-CNN checkpoint. It cannot be loaded with `YOLO()` or imported directly into Deepness as a DetectorType model. Deepness does not natively support Detectron2 format.

Phase 4 must choose one of two paths:
- (a) Use detectree2's own Python API (`detectree2.models.predict.predict_on_image()`) as a standalone inference path outside Deepness. Output bounding boxes or instance masks; extract centroids; load the resulting point layer into QGIS as a vector layer.
- (b) Attempt ONNX export from Detectron2's inference graph using `torch.jit.trace` + the standard PyTorch ONNX export utility. Known issue: Detectron2 ONNX export has dynamic shape challenges; see Detectron2 deploy docs for the recommended approach.

**2. DeepForest (N2) — Requires DeepForest Python library**

The weecology/deepforest-tree model weights are stored on HuggingFace but the full inference pipeline is embedded in the DeepForest library (`pip install deepforest`). The model cannot be run standalone without DeepForest. DeepForest does not expose a standard ONNX export method — there is no equivalent of a generic model-export call in the DeepForest API.

Phase 4 should treat DeepForest as a standalone inference path outside Deepness: use `model.predict_image(path="raster.tif")` to generate a bounding box DataFrame, then convert to a QGIS vector layer. Install DeepForest into `qgis_gdal_env` first.

**3. grediiiii H2 — Custom GhostNet+CBAM backbone**

The YOLOv8n model uses a non-standard GhostNet+CBAM backbone not present in the ultralytics codebase. Attempting ONNX export via ultralytics may raise `NotImplementedError` or an ONNX opset compatibility error for unsupported operators.

Phase 4 action: Download `best.pt` and attempt ONNX export immediately. If export fails within the first 30 minutes of Phase 4, skip this candidate entirely. Do not invest further time in custom backbone workarounds.

**4. firdhokk H3 — RT-DETR, 3.59 GB safetensors**

The RT-DETR model uses a HuggingFace Transformers pipeline, not an ultralytics YOLO pipeline. The file is 3.59 GB. Loading and running inference requires the `transformers` library and an RT-DETR-specific preprocessing pipeline.

This candidate is very low priority for Phase 4. Deprioritize unless all other VHR candidates fail to produce usable detections on Perak/Rupat rasters.

---

## Recommended Shortlist for Phase 4

Top candidates for Phase 4 download, conversion, and empirical testing, organized by GSD tier.

---

### Tier 1: VHR — ≤15 cm/px (Perak 5 cm + Rupat 8.8 cm rasters)

**Entry 1 — tree_tops_yolov9.onnx (B1) — BASELINE, already present**
- Why: Already in models/, Deepness-ready, verified to detect tree crowns at 5–10 cm/px. No download or conversion needed. Use as the benchmark against which new candidates are measured.
- Suits: Perak (5 cm/px) ✓, Rupat (8.8 cm/px) ✓
- Action in Phase 4: Run on Perak and Rupat rasters via Deepness; record detection count and confidence distribution as the baseline for comparison.

**Entry 2 — tribber93/yolov11-palm-oil-tree (H1) — HIGH PRIORITY**
- Why: Oil-palm-specific (not generic tree crown), YOLOv11 family — exports to ONNX via ultralytics; directly Deepness-compatible after export. Best domain match in the VHR tier among freely downloadable candidates.
- Suits: Perak (?), Rupat (?) — GSD unknown; check README in Phase 4; assumed UAV aerial
- Action in Phase 4: Download weights/best.pt from HuggingFace (`https://huggingface.co/tribber93/yolov11-palm-oil-tree`); export to ONNX via `ultralytics`; patch Deepness metadata; test on Perak raster.
- Risk: GSD confidence LOW — model may not generalize to our imagery if trained at a different GSD. Validate GSD from README/model card before scheduling full testing.

**Entry 3 — detectree2 / 230103_randresize_full.pth (N1) — HIGH PRIORITY**
- Why: Trained on Sabah, Malaysia (SE Asia tropical forest) — strongest geographic domain match of any new candidate. CC BY 4.0 license. Correct GSD tier (5–20 cm/px). Open download, no login required.
- Suits: Perak (5 cm/px) ✓, Rupat (8.8 cm/px) ✓
- Download: `https://zenodo.org/records/12773341/files/230103_randresize_full.pth` (no authentication required; 498 MB)
- Action in Phase 4: Download 230103_randresize_full.pth; run inference via detectree2 Python API (NOT via Deepness — Detectron2 format). Export centroid layer from bounding boxes; compare detection count with B1 baseline.
- Caveat: Detects generic tropical tree crowns, not oil-palm class specifically. Will detect all crowns including non-palm vegetation. Deepness integration requires additional work — see Key Integration Constraints section.

**Entry 4 (optional) — grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm (H2) — MEDIUM PRIORITY**
- Why: MIT license, oil-palm-specific, very small model (3.45 MB). Worth attempting if ONNX export succeeds.
- Suits: Unknown GSD — confirm from README before committing Phase 4 time.
- Action in Phase 4: Download best.pt from HuggingFace (`https://huggingface.co/grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm`); attempt `ultralytics` ONNX export immediately. If export fails due to custom GhostNet+CBAM backbone, skip this candidate.
- Risk: High ONNX export failure probability due to non-standard custom backbone. Do not invest more than 30 minutes before skipping.

---

### Tier 2: HR — 15–100 cm/px (no matching test raster)

No confirmed publicly downloadable model exists in this GSD tier. The gap between VHR drone-trained models and MR satellite-trained models is real and documented in the literature. Phase 4 may revisit if MOPAD (N3) becomes accessible via Baidu Wangpan — attempt download first and confirm GSD from the ISPRS 2021 paper before scheduling tests. Do not block Phase 4 schedule waiting for Baidu access.

---

### Tier 3: MR — 0.5–2 m (Aceh 50 cm raster)

**Entry 1 — Google-Resnet101.onnx / Geoeye-Resnet101.onnx / Pleiades-Resnet101.onnx (B2/B3/B4) — BASELINES, already present**
- Why: Already in models/, Deepness-ready (RetinaNet ONNX). Only publicly available candidates at the MR tier. Cover the Aceh (50 cm/px) raster.
- Suits: Aceh (50 cm/px) ✓
- Action in Phase 4: Run on Aceh raster via OPTIMAL-IPB plugin; validate detection on new geographic region (Aceh Barat, Indonesia). Compare results across all three satellite-origin models to assess consistency.

---

### Deprioritized / Conditional

- **weecology/deepforest-tree (N2):** Correct GSD tier (10 cm/px training), MIT license, but US NEON temperate/boreal forest training only — significant domain gap from SE Asia oil palm plantations. Attempt if VHR tier candidates (H1, N1) underperform on Perak/Rupat. Requires `pip install deepforest` into `qgis_gdal_env`.
- **firdhokk/palm-tree-detection-with-rtdetr (H3):** 3.59 GB safetensors, RT-DETR HuggingFace Transformers pipeline — skip in Phase 4 unless all other VHR candidates fail. Do not invest Phase 4 time here.
- **MOPAD (N3) / MADAN (N4):** Strong domain fit (SE Asia oil palm) but Baidu Wangpan accessibility is uncertain from non-China IP. Phase 4 should attempt download as a stretch goal; do not block the Phase 4 schedule on Baidu access resolution.

---

## Assumptions to Validate in Phase 4

Before committing Phase 4 testing time to each candidate, validate these assumptions:

- A1: tribber93/yolov11 training GSD assumed ~5–15 cm/px (typical UAV at 100–150 m AGL). Validate by reading the HuggingFace model card README in Phase 4.
- A2: grediiiii/Yolov8n training is aerial (not ground-level photography). Validate by reading model card — if ground-level, it cannot detect trees in raster tiles.
- A3: MOPAD (rs-dl) dataset was collected in SE Asia oil palm plantations. Validate from the ISPRS Journal 2021 paper (UAV oil palm detection — geographic region not explicit in README).
- A4: MOPAD training GSD ~5–15 cm/px (large-area fixed-wing UAV survey). Validate from paper UAV flight altitude — if fixed-wing at 500 m AGL, GSD may be 20–30 cm/px.
- A5: Baidu Wangpan MOPAD/MADAN links accessible from non-China IP addresses. Validate by download attempt in Phase 4; if blocked, deprioritize immediately.
- A6: MADAN model weights are available (format and hosting not confirmed from GitHub README alone). Validate by reading MADAN README fully and attempting the Google Drive link.
- A7: Google/Geoeye/Pleiades-Resnet101.onnx training GSD ~50 cm/px. Validate from original OPTIMAL-IPB model provenance documentation — STATE.md records ~50 cm/px; confirm before extending to new regions.
- A8: detectree2 performance is acceptable at 8.8 cm/px (Rupat), despite Zenodo docs noting performance decreases above 100 mm GSD. Validate empirically by running on Rupat raster alongside Perak raster and comparing detection density.
