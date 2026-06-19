# Phase 5 Extended Report — Palm / Tree-Crown Detection Model Candidates

**Generated:** 2026-06-19
**Phase:** 05-extended-palm-detection-model-research
**Purpose:** Addendum to 03-CANDIDATE-REPORT.md. Documents new candidates NOT in Phase 3 (B1–N3).

Phase 3 baseline: B1–N3 (see `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md`). This report documents Phase 5 additions only.

---

## Main Candidate Catalog (Phase 5 additions)

Candidates with a downloadable or reportedly-public pretrained checkpoint. Counting/density-map models included in this table per D-02.

| Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm | Canvas 0.5m | Output type | QGIS path |
|------|-------------|-------------------|--------|---------|----------|-----------|-------------|-----------|-------------|-------------|-----------|
| E1: SelvaBox/CanopyRS (hugobaudchon) | DINO + Swin-L 384 (also Faster R-CNN + R50, DINO + R50) | 3–10 cm/px (HIGH — arXiv:2507.00170) | .pt/.pth (reportedly; release assets URL unconfirmed via WebFetch) | Apache-2.0 | PARTIAL (tropical rainforest; not SE Asia oil palm plantation) | ✓ | ✓ | ✗ | ✗ | bbox / mask | standalone script |
| E2: VHRTrees (RSandAI) | YOLOv8m | 50 cm/px (HIGH — Frontiers paper; README typo "0.5 km" is erroneous) | .pt (Google Drive) | Unspecified (academic open) | NO (Turkey satellite; generic trees; domain gap HIGH) | ✗ | ✗ | ✓ | ✓ | bbox | QGIS plugin (via Deepness after ONNX export) |
| E5: Google Forest Data Partnership — Community Palm Model | TF pixel classifier (Sentinel-2 native) | 10 m/px = 1000 cm/px (HIGH — Sentinel-2 native GSD) | TensorFlow SavedModel (.pb / SavedModel dir) | CC-BY 4.0 NC (non-commercial) | YES — Malaysia, Indonesia, Thailand oil palm | ✗ | ✗ | ✗ | ✗ | density-map (pixel probability at 10 m/px — NOT individual tree detection) | not applicable |

**Notes:**
- E1: Weight download URL not confirmed via automated WebFetch (GitHub Release assets page failed to load). Paper (arXiv:2507.00170) explicitly states "Our dataset, code, and pre-trained weights are made public." Manual browser verification recommended before Phase 6 commitment.
- E2: GSD 50 cm/px confirmed from Frontiers paper (0.3389/ffgc.2024.1495544). README "GSD 0.5 km" is a typo in the source repository.
- E5: Updated as recently as 2025 (model_2025b directory found in repo). Main table per D-13 (non-shortlist models still documented). INELIGIBLE for Phase 6 shortlist per D-14 criteria 1, 3, 4.
- E5 Note (D-01): "no localization — density-map; cannot produce QGIS vector layer directly"

---

## Restricted / API-Only Access

Models without locally downloadable weights. Available via Roboflow API inference only (roboflow_algorithm.py pattern). Free-tier API key does not permit weight file download (Roboflow Core plan required).

| Name | URL | Blocker |
|------|-----|---------|
| R1: Manfred Michael (oil-palm-detection) | https://universe.roboflow.com/manfred-michael/oil-palm-detection | API inference only — weights not downloadable (free tier; D-06). 4,063 aerial palm images. |
| R2: UiTM (oil-palm-aerial-detection) | https://universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection | API inference only — weights not downloadable (free tier; D-06). 8,532 images; Malaysian context (UiTM). |
| R4: Rio Bastian (oil-palm-tree-detection-xgrav) | https://universe.roboflow.com/rio-bastian/oil-palm-tree-detection-xgrav | API inference only (D-06). ~210 images; aerial classification. |
| R5: nn-2ju5u (oil-palm-detection-2kozl) | https://universe.roboflow.com/nn-2ju5u/oil-palm-detection-2kozl | API inference only (D-06). Image count unknown. |
| R6: oilpalm-gpu3a (oil-palm-tree-zyvyi) | https://universe.roboflow.com/oilpalm-gpu3a/oil-palm-tree-zyvyi | API inference only (D-06). 60 images; April 2024. |

**Re-probe outcome (EXT-03):** R1 and R2 re-probed by confirming that `roboflow_api_key` is a QGIS global variable not accessible outside the QGIS Python environment. Roboflow documented policy (Core plan required for weight download) applied per D-06. Status unchanged from Phase 3: API inference only.

---

## Excluded Candidates (No Pretrained Weights / Ground-Level / Out of Scope)

| Candidate | Reason Excluded |
|-----------|----------------|
| TorchGeo (backbone models) | Backbone encoders only (ResNet, ViT, Swin, DOFA, Prithvi, ScaleMAE, Panopticon, Copernicus-Pretrain) — no palm/tree-crown detection pretrained weights |
| OpenMMLab / MMDetection (Source Q) | Probed — no palm/tree-crown fine-tuned MMDetection checkpoints found. GitHub search returned 403; no known repos identified. |
| ModelScope (Source P) | Inconclusive — full model catalog requires authenticated browsing. No palm/tree-crown models confirmed or denied. |
| E4: pinakinathc/oil-palm-detection | No pretrained weights — dataset and training code only (YOLOv5-based palm counting; drone imagery; GitHub code only) |
| PSGCNet (arXiv:2012.03597) | General crowd counting (person density estimation); not trained on aerial RS imagery; no aerial palm transfer weights available |
| R7: Roboflow palm-tree (kxzc5) | Ground-level photography (high probability) — 34 images, generic naming; not aerial oil palm detection |
| R8: Roboflow PalmTree (7bu7u) | Ambiguous imagery type — 338 images, non-specific "PalmTree" naming; insufficient evidence of aerial palm plantation context |
| arXiv:2403.03161 (PalmProbNet, Ecuador) | No public checkpoint — code unavailable or not released |
| arXiv:2410.11124 (PalmDSNet, Ecuador) | No public checkpoint — re-checked from Phase 3 excluded list; status unchanged |
| arXiv:2412.11949 (Coconut YOLOv7, Ghana) | No public checkpoint — re-checked; status unchanged |
| arXiv:2502.13023 (PRISM Ecuador, IJCAI 2025) | No public checkpoint — DIFFERENT paper from Zippppo/PRISM (2509.12400); Phase 3 exclusion confirmed |
| MDPI Remote Sensing 2024–2025 (Source O) | No palm/tree-crown papers with confirmed GitHub checkpoint links found via accessible search |
| CVPR 2024 / ICCV 2024 (Source R) | No palm/tree-crown detection papers with public code found in proceedings |

---

## Watch List (2024–2025 Papers Without Public Checkpoints)

Papers with promising scope but no downloadable checkpoint as of 2026-06-19. Re-check at indicated dates.

| Model name | Architecture | GSD | Why interesting | Check date |
|-----------|-------------|-----|----------------|------------|
| E3: PRISM / Zippppo (arXiv:2509.12400) | YOLO11 / RT-DETR variants (Ultralytics) | UAV aerial (cm/px; exact not confirmed) | Palm-specific UAV detection + crown-center localization; paper published Sep 2025; active development | 2027-01-01 |
| Ceroxylon palm detection (MDPI Forests 2025) | Unknown | Unknown | Ceroxylon palm detection, Peru/Amazonas — geographic mismatch for SE Asia but novel architecture potential | 2027-01-01 |

---

## Phase 6 Shortlist

**Top candidates meeting D-14 criteria:**
1. ONNX-exportable (via ultralytics, torch.onnx.export, or equivalent)
2. SE Asia domain match (trained on or near Malaysia/Indonesia palm data, OR tropical with low domain gap)
3. Runs in qgis_gdal_env Python 3.12 (no Detectron2, no PyTorch C++ extensions)
4. Localization output — produces individual detections (bbox or centroid), NOT count-only / density-map

**Assessment of Phase 5 candidates against all four criteria:**

| Candidate | D-14 Crit 1 (ONNX) | D-14 Crit 2 (SE Asia) | D-14 Crit 3 (Py 3.12) | D-14 Crit 4 (Localization) | Eligible |
|-----------|----|----|----|----|---|
| E1 CanopyRS | ASSUMED (Swin-L needs verification) | PARTIAL (tropical, not palm plantation) | UNKNOWN (DINO+Swin-L deps?) | YES (bbox) | CONDITIONAL |
| E2 VHRTrees | YES (ultralytics) | NO (Turkey, generic trees) | YES (ultralytics standard) | YES (bbox) | CONDITIONAL (criterion 2 fails) |
| E5 Google FDP | NO (TF SavedModel) | YES | NO (TF format) | NO (density-map) | INELIGIBLE |

**No candidate fully satisfies all four D-14 criteria.** Phase 5 Phase 6 shortlist entries are conditional:

### Shortlist #1 (Conditional): E2 VHRTrees (RSandAI)

- Why shortlisted: Only Phase 5 candidate with confirmed-accessible Google Drive download links and standard YOLOv8m ONNX export path. Matches Canvas 0.5m and Aceh 50cm GSD. Despite Turkey training origin (criterion 2 failure), it is the best available candidate for the 50 cm/px resolution tier.
- ONNX-exportable: YES — `yolo export format=onnx` via ultralytics (standard path)
- SE Asia domain match: NO — Turkey satellite imagery, generic deciduous trees. Domain gap HIGH for SE Asia oil palm plantations. Likely to produce false positives on non-palm vegetation.
- qgis_gdal_env Python 3.12: YES — ultralytics is pip-installable, no special extensions
- Localization output: YES (bbox)
- Phase 6 action: Download YOLOv8m .pt from Google Drive (https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view); export to ONNX; test on canvas_0.5mpx.tif raster. Expect low palm-specific precision — validate whether generic tree detection is useful as a baseline.

### Shortlist #2 (Conditional — requires weight URL verification): E1 SelvaBox/CanopyRS (hugobaudchon)

- Why shortlisted: Paper explicitly states pretrained weights are public; Apache-2.0 license; GSD 3–10 cm/px covers Perak (5cm) and Rupat (8.8cm); trained on tropical tree crowns (closest available to SE Asia context among Phase 5 new candidates). Multiple architecture variants — Faster R-CNN+R50 may be ONNX-exportable without Swin-L complications.
- ONNX-exportable: ASSUMED — DINO+Swin-L 384 requires Phase 6 export verification. Faster R-CNN+R50 preset is more export-friendly (standard torchvision path).
- SE Asia domain match: PARTIAL — tropical rainforest (3 countries, XPRIZE Rainforest context). Not plantation row geometry. Domain gap MEDIUM for oil palm.
- qgis_gdal_env Python 3.12: UNKNOWN — depends on canopyrs package dependencies (DINO/Swin may require specific torch version).
- Localization output: YES (bbox via detection preset; mask via segmentation presets)
- Phase 6 action: (1) Verify weight download URL by visiting https://github.com/hugobaudchon/CanopyRS/releases in browser; (2) Install canopyrs package; (3) Confirm Python 3.12 compatibility; (4) Test Faster R-CNN+R50 preset on Perak 5cm raster; (5) Attempt ONNX export of detection preset.

---

## Sources Probed (Phase 5)

| # | Source | Platform | Result |
|---|--------|----------|--------|
| L | SelvaBox/CanopyRS | github.com/hugobaudchon/CanopyRS | E1 found — weights reportedly public; URL unconfirmed via WebFetch |
| M | VHRTrees (RSandAI) | github.com/RSandAI/VHRTrees | E2 found — YOLOv8m Google Drive links; GSD 50cm/px confirmed |
| N | arXiv / IEEE re-probe | arxiv.org | Rate-limited; WebSearch fallback — no new candidates beyond E1–E3; Phase 3 papers still no weights |
| O | MDPI Remote Sensing / ISPRS 2024–2025 | mdpi.com, sciencedirect.com | HTTP 403 on MDPI search; WebSearch fallback — no palm checkpoints found |
| P | ModelScope (Alibaba) | modelscope.cn | Authenticated access required — model catalog not accessible via unauthenticated fetch |
| Q | OpenMMLab / MMDetection | github.com | GitHub search 403; no known palm/tree-crown MMDetection checkpoints found |
| R | CVPR / ICCV 2024 | cvpr.thecvf.com, DmitryRyumin/CVPR-2023-24-Papers | No palm/tree-crown detection papers with public code confirmed |
| S | Roboflow Universe re-probe | universe.roboflow.com | R1/R2 API-only (D-06, key QGIS-only, Core plan required); R4/R5/R6 aerial API-only; R7 ground-level excluded; R8 excluded (ambiguous) |
| T | Palm counting / density models | arxiv.org, github.com | E4 no weights (excluded); E5 TF SavedModel 10m/px SE Asia YES (main table, Phase 6 INELIGIBLE); PSGCNet crowd-only (excluded) |
