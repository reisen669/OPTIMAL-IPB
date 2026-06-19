# Phase 5: Extended Palm / Tree-Crown Detection Model Research — Research

**Researched:** 2026-06-19
**Domain:** Palm / tree-crown detection model discovery — ModelScope, OpenMMLab, TorchGeo, VHRTrees, SelvaBox, PRISM, Roboflow re-probe, IEEE/arXiv re-probe, palm counting/density
**Confidence:** MEDIUM (new candidates verified via web search and WebFetch; checkpoint format/ONNX-exportability ASSUMED until executor probes directly)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Include density-map-only models (heatmaps, Gaussian kernel, no bounding boxes) in the counting tier. Document each with note: "no localization — count-only; cannot produce QGIS vector layer directly."
- **D-02:** Counting/density models go in the SAME main candidate table as detection models. Add two extra columns to the Phase 3-style table: **Output type** (bbox / centroid / density-map / count-only) and **QGIS path** (QGIS plugin / standalone script / not applicable). Do NOT create a separate table.
- **D-03:** No architecture constraint — any palm/tree counting approach with pretrained weights is in scope (CSRNet, MCNN, P2PNet, regression heads, etc.).
- **D-04:** Papers from 2024–2025 with no public checkpoint → **Watch List** section. Format: model name, architecture, GSD, why interesting, note to check for future checkpoint releases. Not in the main candidate table.
- **D-05:** Roboflow R1 and R2: re-probe using existing `roboflow_api_key` QGIS global variable. Goal: determine if weights are downloadable, not just updating status.
- **D-06:** If Roboflow key gives API-hosted inference only (not direct weight download): document as "API inference only, weights not downloadable" — distinct from BLOCKED.
- **D-07:** ArcGIS Living Atlas R3 — out of scope. .dlpk format incompatible with QGIS/onnxruntime.
- **D-08:** IEEE Xplore re-probe: search arXiv for preprint versions; if preprint links to public GitHub with pretrained weights, that is a valid new candidate.
- **D-09:** Priority new source categories: ModelScope (Alibaba), OpenMMLab/MMDetection zoo, TorchGeo, CVPR/ICCV 2024, MDPI Remote Sensing (2024–2025), ISPRS J Photogrammetry (2024–2025).
- **D-10:** Coverage scope = any tree crown detection. Researcher MUST specify for each: (a) what it was designed for (species, region, sensor), (b) expected SE Asia oil palm domain gap. Filter only by checkpoint access.
- **D-11:** ESA/Copernicus ML repos — excluded. Sentinel-2 10–60 m/px incompatible with VHR/MR test rasters.
- **D-12:** Phase 6 goal = QGIS Processing Toolbox integration. Phase 6 test raster: `sample_data_qgis/canvas_0.5mpx.tif` (0.5 m/px).
- **D-13:** Models NOT suitable for QGIS integration must still appear in the full candidate table — do not discard them.
- **D-14:** Phase 6 shortlist criteria — ALL FOUR required: (1) ONNX-exportable, (2) SE Asia domain match, (3) runs in qgis_gdal_env Python 3.12, (4) localization output (bbox or centroid, not density-map).
- **D-15:** Phase 6 shortlist size = top 5 candidates.
- **D-16:** `05-EXTENDED-REPORT.md` is an addendum only — states "Phase 3 baseline: B1–N3 (see 03-CANDIDATE-REPORT.md)" at top; does not re-document Phase 3 models.

### Claude's Discretion

- Exact table column ordering in the extended candidate table
- Whether to include a "Sources Probed" appendix (follow Phase 3 pattern)
- GSD confidence labeling convention (HIGH/MEDIUM/LOW — follow Phase 3 pattern)
- Grouping/ordering of candidates within the main table
- How many Watch List entries are "enough" before stopping paper search

### Deferred Ideas (OUT OF SCOPE)

- ONNX conversion of Phase 5 candidates — Phase 6 scope
- Empirical inference testing on rasters — Phase 6 scope
- Fine-tuning candidates on SE Asia data — out of scope
- ArcGIS Living Atlas R3 conversion — ecosystem incompatible

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXT-01 | All new candidates documented with architecture, GSD range (cm/px), format, license, download URL, SE Asia applicability | Candidate leads section below; executor probes each URL |
| EXT-02 | Palm counting / density-estimation models covered as a separate tier (distinct from detection/bounding-box models) | Counting tier leads: pinakinathc/oil-palm-detection, Google community palm model, PSGCNet; Watch List entries |
| EXT-03 | Sources from Phase 3 marked PARTIAL/BLOCKED re-probed (IEEE Xplore → arXiv preprints; Roboflow R1/R2 via API key; ArcGIS excluded per D-07) | Roboflow re-probe strategy below; arXiv query strings for IEEE re-probe |
| EXT-04 | 05-EXTENDED-REPORT.md produced with summary table and Phase 6 shortlist addendum | Report structure section below |

</phase_requirements>

---

## Summary

Phase 5 searches source categories that Phase 3 did not cover (ModelScope, OpenMMLab, TorchGeo, CVPR/ICCV 2024 proceedings, MDPI/ISPRS 2024–2025, arXiv re-probe) and re-probes the two Phase 3 BLOCKED/PARTIAL sources (Roboflow R1/R2 via existing API key; IEEE Xplore via arXiv preprints). The phase produces `05-EXTENDED-REPORT.md` as a structured addendum to `03-CANDIDATE-REPORT.md` and identifies a top-5 Phase 6 shortlist.

Research in this session has identified **seven concrete new candidate leads** that Phase 3 did not document, plus several Watch List papers. The most significant new candidate is **VHRTrees (RSandAI)** — multiple pretrained YOLO weights (YOLOv5/v7/v8/v9) for satellite-native tree detection at 0.5 m/px GSD, matching the Canvas test raster. **SelvaBox / CanopyRS** provides DINO-Swin-L pretrained on tropical forests at 3–10 cm/px, and is the highest-priority new VHR candidate for SE Asia. **PRISM (Zippppo)** and the **Google Forest Data Partnership community palm model** are relevant but face ONNX/TensorFlow integration barriers.

The Roboflow weight-download situation has a key finding: **raw .pt weight download is restricted to paid Core plans**. The existing `roboflow_api_key` likely provides API inference (not weight download). Executor should test it but document as "API inference only" if weights are not downloadable.

**Primary recommendation:** Prioritize executor search in this order: (1) SelvaBox/CanopyRS pretrained weights on HuggingFace, (2) VHRTrees YOLO weights on Google Drive, (3) Roboflow R1/R2 weight download attempt via API key, (4) ModelScope search with Chinese-language palm queries, (5) arXiv/IEEE re-probe for 2024–2025 SE Asia papers, (6) counting-tier candidates.

---

## Architectural Responsibility Map

This phase is a research/documentation phase with no runtime component. All "architecture" here refers to the report artifact produced, not the plugin.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Model discovery / web search | Executor agent | — | No QGIS or plugin involvement |
| Checkpoint URL validation | Executor agent | — | HTTP probes from researcher environment |
| Report authoring (05-EXTENDED-REPORT.md) | Executor agent | — | Output artifact for Phase 6 planner |
| Phase 6 shortlist evaluation | Executor agent | — | Apply D-14 criteria to each candidate |

---

## Standard Stack

Phase 5 has no new library dependencies. The executor uses web search tools only. The report format follows Phase 3 conventions exactly.

### Report Column Schema (Phase 3 + Phase 5 extensions)

Phase 3 column schema (from `03-CANDIDATE-REPORT.md`):

```
Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm
```

Phase 5 extends with TWO new columns (D-02):

```
Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm | Canvas 0.5m | Output type | QGIS path
```

**Canvas 0.5m column** added per CONTEXT.md specifics: the Phase 6 test raster is `sample_data_qgis/canvas_0.5mpx.tif` (0.5 m/px). Mark ✓ / ✗ / ? per model row.

**Output type values:** `bbox` / `centroid` / `density-map` / `count-only` / `mask`

**QGIS path values:** `QGIS plugin` / `standalone script` / `API call` / `not applicable`

---

## Architecture Patterns

### Recommended Plan Structure

Phase 5 work is a **research-execute phase** — no code changes, only web searching and report writing. The natural structure is:

**Wave 0 (Setup):** Read all canonical refs. No plans needed — executor reads CONTEXT.md + 03-CANDIDATE-REPORT.md before searching.

**Wave 1 (Parallel search — all plans executable simultaneously):** One plan per source category. Searching is independent and parallelizable.

**Wave 2 (Report writing — gates on Wave 1 completion):** One plan to compile all findings into `05-EXTENDED-REPORT.md`.

### Recommended Plan Count: 5 plans

| Plan | Wave | Scope | Required Before |
|------|------|-------|-----------------|
| 05-01-PLAN.md | Wave 1 | New source search: SelvaBox/CanopyRS, VHRTrees, PRISM/arXiv, TorchGeo, OpenMMLab | — |
| 05-02-PLAN.md | Wave 1 | New source search: ModelScope, MDPI/ISPRS 2024–2025, CVPR/ICCV 2024 proceedings | — |
| 05-03-PLAN.md | Wave 1 | Roboflow R1/R2 re-probe (via `roboflow_api_key`) + additional Roboflow Universe palm models | — |
| 05-04-PLAN.md | Wave 1 | IEEE Xplore re-probe via arXiv preprints; counting/density model search | — |
| 05-05-PLAN.md | Wave 2 | Write `05-EXTENDED-REPORT.md`: compile all findings, apply Phase 6 shortlist criteria | 05-01 through 05-04 complete |

**Rationale:** Wave 1 plans are fully parallelizable (no shared state). Wave 2 gates on Wave 1 to ensure all discoveries are included before the report is written.

### Recommended Project Structure

No new source files or directories. All output goes to:

```
.planning/phases/05-extended-palm-detection-model-research/
├── 05-CONTEXT.md          (exists)
├── 05-RESEARCH.md         (this file)
├── 05-01-PLAN.md          (Wave 1 — to be created by planner)
├── 05-02-PLAN.md          (Wave 1 — to be created by planner)
├── 05-03-PLAN.md          (Wave 1 — to be created by planner)
├── 05-04-PLAN.md          (Wave 1 — to be created by planner)
└── 05-05-PLAN.md          (Wave 2 — to be created by planner)
```

Primary output artifact:

```
.planning/phases/05-extended-palm-detection-model-research/
└── 05-EXTENDED-REPORT.md  (produced by Wave 2 plan)
```

---

## Known Candidate Leads

These are the specific repositories and models the executor should probe. Each was discovered during this research session. Priority is HIGH → MEDIUM → LOW for executor time allocation.

### Priority HIGH: VHR tree-crown candidates with SE Asia or tropical relevance

---

**E1: SelvaBox / CanopyRS (hugobaudchon)**
- **GitHub:** https://github.com/hugobaudchon/CanopyRS
- **Paper:** arXiv:2507.00170 (SelvaBox: A high-resolution dataset for tropical tree crown detection)
- **Architecture:** DINO-Swin-L backbone; also Faster R-CNN, Mask R-CNN, RetinaNet, Mask2Former, SAM 2 variants
- **GSD:** 3–10 cm/px (UAV drone imagery, multi-resolution pipeline) [CITED: arxiv.org/html/2507.00170]
- **Dataset:** 83,000+ manually labeled tree crowns across three tropical forest countries
- **Pretrained weights:** Publicly available; repo documentation references a Model Zoo at hugobaudchon.github.io/CanopyRS/user-guide/presets/ [CITED: github.com/hugobaudchon/CanopyRS]
- **HuggingFace:** SelvaBox dataset hosted on HuggingFace [CITED: arxiv.org/html/2507.00170]
- **Format:** Not confirmed — likely .pt/.pth (PyTorch) for DINO/Swin variants [ASSUMED]
- **SE Asia applicability:** Panama, Brazil, Ecuador training data — tropical forest crowns. No SE Asia oil palm specific data. Domain gap: moderate (tropical canopy match, but no oil palm class). [CITED: arxiv.org/html/2507.00170]
- **Output type:** bbox / instance segmentation (SelvaMask)
- **Phase 6 shortlist eligibility:** Contingent on ONNX export feasibility for DINO/Swin-L backbone and Python 3.12 compatibility
- **Executor action:** (a) Visit hugobaudchon.github.io/CanopyRS/user-guide/presets/ and github.com/hugobaudchon/CanopyRS/releases; (b) confirm checkpoint format and download URL; (c) check ONNX export path; (d) document GSD from README

---

**E2: VHRTrees (RSandAI)**
- **GitHub:** https://github.com/RSandAI/VHRTrees
- **Paper:** Frontiers in Forests and Global Change, 2024 — "VHRTrees: a new benchmark dataset for tree detection in satellite imagery and performance evaluation with YOLO-based models" [CITED: frontiersin.org/articles/10.3389/ffgc.2024.1495544/full]
- **Architecture:** YOLOv5, YOLOv7, YOLOv8, YOLOv9 — 8 best-performing experiments
- **GSD:** 0.5 m/px or better (VHR satellite imagery from Google Earth, RGB, Turkey regions) [CITED: frontiersin.org article WebFetch]
- **Pretrained weights:** 8 experiments with direct Google Drive download links in the GitHub repository [CITED: WebFetch of github.com/RSandAI/VHRTrees README]
- **Best performer:** YOLOv8m, F1-score 0.932, mAP@50 0.934
- **Format:** .pt (YOLO — ONNX-exportable via ultralytics)
- **License:** Not confirmed [ASSUMED open, given academic context; check repo]
- **SE Asia applicability:** Turkey satellite imagery — generic tree detection, not oil palm. Domain gap: high (temperate trees, different crown morphology). But satellite-native GSD (0.5 m) matches Canvas test raster exactly. [CITED: frontiersin.org]
- **Output type:** bbox
- **QGIS path:** QGIS plugin (ONNX via Deepness after ultralytics export)
- **Canvas 0.5m:** ✓ (design GSD matches)
- **Executor action:** (a) Visit github.com/RSandAI/VHRTrees and confirm Google Drive weight links are accessible without login; (b) download YOLOv8m weights; (c) confirm ONNX export path via ultralytics; (d) record license

---

**E3: PRISM / Orthomosaics to Raw UAV (Zippppo)**
- **GitHub:** https://github.com/Zippppo/PRISM
- **Paper:** arXiv:2509.12400 — "From Orthomosaics to Raw UAV Imagery: Enhancing Palm Detection and Crown-Center Localization" [CITED: arxiv.org/html/2509.12400v2]
- **Architecture:** Benchmarks YOLOv8–12 and RT-DETRv1–v2 (largest variants). Also YOLOv8/v11/v12 in pose mode for crown-center keypoint localization.
- **GSD:** ~5 cm/px inferred from DJI Phantom 4 RTK at 90 m AGL [ASSUMED: typical 5–8 cm/px for this drone/altitude combination]
- **Dataset:** Orthomosaic patches on GitHub; raw patches on zenodo.org/records/17094346; 1,500 images, 8,842 annotated palm bounding boxes [CITED: arxiv.org/html/2509.12400v2]
- **Pretrained weights:** Not explicitly released in paper — dataset available but model weights status unknown [ASSUMED not yet released; executor must check repo releases]
- **SE Asia applicability:** Ecuador palm forest (not SE Asia oil palm). Domain gap: moderate for palm detection but different genus (tropical palms vs. Elaeis guineensis). Crown-center localization mode is relevant for precision agriculture.
- **Output type:** bbox; keypoint (centroid mode) via pose YOLO
- **QGIS path:** standalone script (YOLO export to ONNX if weights released)
- **Executor action:** (a) Visit github.com/Zippppo/PRISM and check Releases tab for model weights; (b) if no weights, move to Watch List; (c) note Zenodo data record 17094346

---

### Priority MEDIUM: Counting / density tier + new detection models

---

**E4: pinakinathc/oil-palm-detection**
- **GitHub:** https://github.com/pinakinathc/oil-palm-detection
- **Purpose:** Oil Palm Tree Counting in Drone Images [CITED: GitHub search result]
- **Architecture:** Appears to use YOLOv5 framework [ASSUMED from repo file listing "yolov5 folder"; unconfirmed]
- **GSD:** UAV drone imagery; likely 5–15 cm/px [ASSUMED]
- **Pretrained weights:** No releases published in repository [CITED: WebSearch result stating "no releases published"]. Weights may exist in raw files or LFS. Status: likely code-only, no downloadable checkpoint.
- **SE Asia applicability:** Unknown — paper/dataset origin not confirmed
- **Output type:** count (counting model — may produce density map or point detections)
- **Executor action:** (a) Visit github.com/pinakinathc/oil-palm-detection; (b) check README for model download link or checkpoint; (c) if no weights, add to Watch List or Excluded Candidates; (d) confirm whether it is detection or density estimation

---

**E5: Google Forest Data Partnership — Community Palm Model**
- **GitHub:** https://github.com/google/forest-data-partnership
- **Paper:** arXiv:2405.09530 — "A community palm model" [CITED: arxiv.org/abs/2405.09530]
- **Architecture:** Unknown — uses satellite multi-spectral input (Sentinel-1, Sentinel-2, ALOS-2, terrain). Model type not specified in abstract. [ASSUMED CNN or transformer for pixel-wise classification]
- **GSD:** 10 m/px (Sentinel-2 native) [CITED: Google Earth Engine catalog entry for Palm Probability model 2025a: "per-pixel probability estimates at 10-meter resolution"]
- **Coverage:** Indonesia, Malaysia, Thailand, Nigeria, Colombia, Brazil, Côte d'Ivoire, Ghana, Ecuador, Honduras [CITED: Google Earth Engine catalog]
- **Format:** TensorFlow SavedModel (downloadable from /models directory) [CITED: github.com/google/forest-data-partnership search result]
- **License:** CC-BY 4.0 NC (non-commercial) [CITED: Google Earth Engine catalog]
- **SE Asia applicability:** YES — explicitly trained for Malaysia, Indonesia, Thailand oil palm [CITED: Google Earth Engine catalog]
- **Output type:** pixel probability (semantic segmentation / density-map equivalent at 10 m/px — NOT individual tree detection)
- **QGIS path:** not applicable (10 m/px output; cannot produce individual palm detections on VHR/MR rasters)
- **Perak 5cm:** ✗ (resolution mismatch — model operates at 10 m/px)
- **Canvas 0.5m:** ✗ (same resolution mismatch)
- **Phase 6 shortlist:** Ineligible (D-14 criterion 4: localization output required)
- **Why document:** SE Asia explicit coverage; highest geographic relevance for oil palm mapping. Counting-tier value as a plantation boundary model.
- **Executor action:** (a) Visit github.com/google/forest-data-partnership/tree/main/models; (b) confirm TF SavedModel format and download access; (c) document SE Asia coverage; (d) classify as density/pixel model in Output type column

---

**E6: Additional Roboflow Universe oil palm models (new — not in Phase 3)**

Phase 3 found R1 (Manfred Michael) and R2 (UiTM). Research this session found three additional Roboflow Universe oil palm models NOT in Phase 3:

| Provisional ID | Workspace | URL | Image count |
|---------------|-----------|-----|-------------|
| R4 | Rio Bastian — OIL PALM TREE DETECTION | universe.roboflow.com/rio-bastian/oil-palm-tree-detection-xgrav | 210 |
| R5 | nn-2ju5u — oil-palm-detection-2kozl | universe.roboflow.com/nn-2ju5u/oil-palm-detection-2kozl | unknown |
| R6 | oilpalm-gpu3a — oil-palm-tree-zyvyi | universe.roboflow.com/oilpalm-gpu3a/oil-palm-tree-zyvyi | 60 |

**Critical finding for all Roboflow models (R1–R6):** [CITED: docs.roboflow.com/deploy/download-roboflow-model-weights]

Raw .pt weight download is **restricted to paid Core plans and Enterprise customers**. Free API key provides API-hosted inference only, not direct weight download. The existing `roboflow_api_key` (from `roboflow_algorithm.py`) is almost certainly a free-tier key providing API inference access only — not weight download. Executor should:
1. Attempt weight download via `roboflow` Python SDK with the existing key
2. If download returns 403 or requires upgrade: document ALL Roboflow models as "API inference only, weights not downloadable" (D-06)
3. This covers R1, R2, R4, R5, R6 in a single probe

**QGIS path (if API-only):** API call (requires `roboflow_algorithm.py` pattern; works only with internet connectivity and API rate limits)

---

**E7: VHRTrees-style satellite YOLO — confirm GSD for Roboflow palm-tree-detection**

Two Roboflow tree/palm detection models from general search (may include aerial imagery):

| Provisional ID | Workspace | URL | Note |
|---------------|-----------|-----|------|
| R7 | palm-tree — palm-tree-detection-kxzc5 | universe.roboflow.com/palm-tree/palm-tree-detection-kxzc5 | 34 images, likely ground-level |
| R8 | PalmTree — palm-tree-detection-7bu7u | universe.roboflow.com/palmtree-3uhul/palm-tree-detection-7bu7u | 338 images |

These have low probability of being aerial/satellite-suitable (small datasets, likely ground-level photography). Executor should check the dataset sample images; if ground-level, add to Excluded Candidates, do not document in main table.

---

### Priority LOW: ModelScope, OpenMMLab, TorchGeo (likely no palm-specific pretrained models)

**ModelScope (Alibaba):** [ASSUMED] Direct search attempts via WebFetch returned only the site header — full model catalog requires authenticated browsing or direct platform access. The executor must search modelscope.cn interactively using these query strings:

Chinese queries for ModelScope internal search:
- `油棕榈 检测` (oil palm detection)
- `棕榈树 目标检测` (palm tree object detection)
- `棕榈计数` (palm counting)
- `遥感 树冠检测` (remote sensing tree crown detection)

English queries:
- `palm tree detection`
- `oil palm`
- `tree crown aerial`

Expectation: Low probability of finding palm-specific pretrained models on ModelScope. If found, document; if not, record "Probed — no palm/tree-crown models found" in Sources Probed appendix.

**OpenMMLab / MMDetection:** [CITED: WebSearch — no palm-specific MMDetection checkpoint found] The MMDetection model zoo contains 100+ detection architectures pretrained on COCO/ImageNet — none are palm-specific. Community models (not in official zoo) would need a GitHub search for `mmdetection oil palm`. Executor should search GitHub for `mmdetection oil palm` or `mmdetection tree crown` and check if any pretrained checkpoint `.pth` files are released. If none found: document as "Probed — no palm/tree-crown fine-tuned MMDetection checkpoints found."

**TorchGeo:** [CITED: torchgeo.readthedocs.io/en/stable] TorchGeo provides geospatial **backbone encoders** (ResNet, ViT, Swin, DOFA, Prithvi, ScaleMAE, etc.) pretrained on satellite imagery — but NO detection head pretrained on tree crown or palm data. TorchGeo does NOT have a model equivalent to detectree2 or deepforest with pretrained detection weights for tree crowns. Executor should confirm this at torchgeo.readthedocs.io/en/stable/api/models.html, then document as "Backbone encoders only — no palm/tree-crown detection pretrained weights in TorchGeo."

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Report table formatting | Custom markdown template | Phase 3 03-CANDIDATE-REPORT.md style | Consistency; planner already knows the schema |
| GSD estimation | Custom calculation | Read from paper/README directly | GSD from paper is more reliable than estimating from drone altitude without sensor data |
| Roboflow weight download | curl/wget to universe.roboflow.com | roboflow Python SDK model.download() | SDK handles auth headers and format correctly |
| Source URL validation | curl -I HEAD requests | Direct browser visit + WebFetch | Roboflow/HuggingFace may redirect; need to see the actual content |

**Key insight:** Phase 5 is a documentation and discovery phase. The executor should spend time on direct URL validation rather than reasoning from training knowledge about what likely exists.

---

## Source-by-Source Search Strategy

### Source L: SelvaBox / CanopyRS (NEW — not in Phase 3)

**Goal:** Confirm pretrained weights are publicly accessible; get format and download URL.

**Primary URL:** https://github.com/hugobaudchon/CanopyRS

**Action sequence:**
1. Visit `github.com/hugobaudchon/CanopyRS` — read README for download instructions
2. Visit `hugobaudchon.github.io/CanopyRS/user-guide/presets/` — Model Zoo with specific checkpoint names
3. Check GitHub Releases page for .pt/.pth/.safetensors files
4. Check HuggingFace: search `huggingface.co/models?search=canopyrs` or `huggingface.co/models?search=selvabox`
5. Note architecture: DINO-Swin-L is the main backbone (transformer — ONNX export requires torch.onnx.export + opset 16+; verify Python 3.12 compatibility)
6. Read SelvaBox paper section on multi-resolution training — confirm GSD range

**Expected outcome:** HIGH confidence of finding downloadable weights based on paper stating "dataset, code, and pre-trained weights are made public." [CITED: arxiv.org/pdf/2507.00170]

---

### Source M: VHRTrees (RSandAI) (NEW — not in Phase 3)

**Goal:** Download YOLOv8m checkpoint from Google Drive; confirm ONNX export path.

**Primary URL:** https://github.com/RSandAI/VHRTrees

**Action sequence:**
1. Visit repo — find the experiment table with Google Drive links
2. For YOLOv8m (best performer): attempt to access the Google Drive link — confirm whether it requires Google sign-in or is publicly shared
3. Record GSD: 0.5 m/px confirmed from Frontiers paper
4. Note: all YOLO variants in this repo use standard ultralytics architecture → ONNX export via `ultralytics model.export(format='onnx')` is straightforward
5. Confirm license from README or paper

**GSD note:** 0.5 m/px GSD maps perfectly to Canvas test raster (0.5 m/px). Perak (5 cm) and Rupat (8.8 cm) are out of range — mark ✗.

---

### Source N: arXiv re-probe for IEEE Xplore papers (D-08)

**Goal:** Find arXiv preprints of IEEE-paywalled palm/tree detection papers with linked public GitHub + weights.

**Queries to run on arxiv.org:**

```
https://arxiv.org/search/?searchtype=all&query=oil+palm+detection+deep+learning&start=0
https://arxiv.org/search/?searchtype=all&query=palm+tree+detection+UAV+satellite&start=0
https://arxiv.org/search/?searchtype=all&query=tree+crown+detection+pretrained&start=0
```

**Filter criteria:**
- Publication year: 2023, 2024, 2025
- Must have GitHub link in paper (check abstract or HTML body for `github.com` mentions)
- GitHub repo must have a Releases page or explicit model download link

**Key papers to investigate directly (already found in this session):**

| Paper | arXiv ID | GitHub found? | Notes |
|-------|----------|---------------|-------|
| From Orthomosaics to Raw UAV | 2509.12400 | github.com/Zippppo/PRISM | Weights status unknown — check Releases |
| SelvaBox | 2507.00170 | github.com/hugobaudchon/CanopyRS | Weights claimed public |
| PalmProbNet (Ecuador) | 2403.03161 | Unknown | ACM SE Conference; check for supplemental repo |
| PRISM (Ecuador palms, 2502.13023) | 2502.13023 | IJCAI 2025 | Already in Phase 3 excluded list — re-verify weights |
| PalmDSNet (2410.11124) | 2410.11124 | Unknown | Phase 3 excluded (no weights) — re-verify |
| Coconut YOLOv7 (2412.11949) | 2412.11949 | Unknown | Phase 3 excluded (no weights) — re-verify |

**Action for each paper:** Visit arxiv.org/abs/[ID] → check HTML version for GitHub link → visit GitHub → check Releases for .pt/.pth files.

---

### Source O: MDPI Remote Sensing / ISPRS 2024–2025

**Goal:** Find open-access 2024–2025 papers with linked GitHub repos and downloadable checkpoints.

**Queries:**

MDPI Remote Sensing direct search:
```
https://www.mdpi.com/search?q=oil+palm+detection&journal=remotesensing&article_type=research-article&year_from=2024&year_to=2025
https://www.mdpi.com/search?q=tree+crown+detection&journal=remotesensing&year_from=2024&year_to=2025
```

ISPRS Journal:
```
https://www.sciencedirect.com/journal/isprs-journal-of-photogrammetry-and-remote-sensing
(search: "oil palm" OR "palm tree" OR "tree crown" in 2024–2025 issues)
```

**Specific MDPI paper to probe:** "Automatic Detection of Ceroxylon Palms by Deep Learning in a Protected Area in Amazonas (NW Peru)" — MDPI Forests, 2025. [CITED: WebSearch result]. Check for GitHub link with weights.

**Filter criteria:** Open access only (MDPI is fully open access); GitHub link must be in the paper; pretrained checkpoint must be downloadable without login.

---

### Source P: ModelScope (Alibaba)

**Goal:** Search for palm/oil palm detection pretrained models.

**Primary URL:** https://www.modelscope.cn/models

**Action sequence:**
1. Navigate to modelscope.cn/models — search with queries listed in "Priority LOW" section above
2. If no palm models: search for general aerial/remote sensing detection models that might transfer
3. Record all relevant finds or explicitly record "Probed — no palm models found"

**Expected outcome:** Low probability [ASSUMED based on general knowledge that ModelScope hosts more NLP/CV-classification models than specialized agricultural detection models]. Worth probing given SE Asia coverage of Chinese agricultural AI.

---

### Source Q: OpenMMLab / MMDetection community

**GitHub search queries:**
```
site:github.com mmdetection oil palm
site:github.com mmdetection "palm tree"
site:github.com mmdetection "tree crown"
```

Or via GitHub directly: https://github.com/search?q=mmdetection+oil+palm&type=repositories

**Expected outcome:** Low probability of finding palm-specific fine-tuned MMDetection checkpoints. The official MMDetection zoo [CITED: WebSearch] has no palm-specific entries.

---

### Source R: CVPR / ICCV 2024 Proceedings

**Goal:** Find tree crown or palm detection papers with public code released at CVPR/ICCV 2024.

**Search strategy:**
1. Visit https://cvpr.thecvf.com/virtual/2024/papers.html — search page for "palm", "tree crown", "canopy", "aerial detection"
2. Check https://github.com/DmitryRyumin/CVPR-2023-24-Papers (community tracking repo with code links)
3. Check https://github.com/52CV/CVPR-2024-Papers

**Expected outcome:** Low-moderate probability. CVPR 2024 had papers on remote sensing detection but no known palm-specific papers with code. Tree crown papers tend to appear at domain-specific venues (ISPRS, MDPI) more than CVPR. If nothing found: document "Probed — no palm/tree-crown detection papers with public code at CVPR/ICCV 2024."

---

### Source S: Roboflow R1/R2 re-probe + new R4–R8 (D-05, D-06)

**Goal:** Determine if `roboflow_api_key` (from QGIS global var) enables weight download.

**Critical background finding:** [CITED: docs.roboflow.com/deploy/download-roboflow-model-weights]

Raw .pt weight download requires a **paid Core plan**. Free API keys only provide API-hosted inference. The project's existing key (used in `roboflow_algorithm.py` for the oil-palm-aerial-detection/1 API call) is a free inference key, not a paid weight-download key.

**Action sequence:**
```python
import roboflow
rf = roboflow.Roboflow(api_key=<read from QGIS global var roboflow_api_key>)
# Try R1
project_r1 = rf.workspace("manfred-michael").project("oil-palm-detection")
version_r1 = project_r1.version(11)  # latest version
model_r1 = version_r1.model
model_r1.download()  # will return 403/error if free plan
```

**Expected outcome:** 403 or "Core plan required" error. If this occurs: document R1 and R2 as "API inference only, weights not downloadable (free tier key)."

**For R4–R8:** After R1/R2 probe, probe R4 (Rio Bastian, 210 images) as a representative of smaller Roboflow palm models. If the key grants download for any model, document. Otherwise, the "API inference only" classification applies to all Roboflow Universe models not on the R's workspace.

---

### Source T: Palm counting / density models

**Goal:** Find counting/density tier models (D-01 through D-04) with pretrained weights.

**Queries:**
```
arXiv: "oil palm counting" "pretrained" site:github.com
GitHub: "palm" "density estimation" "pretrained" weights
GitHub: "tree counting" "remote sensing" "pretrained" model checkpoint
```

**Known leads to probe:**
- `pinakinathc/oil-palm-detection` (E4) — verify if counting model with weights
- `PSGCNet` (arXiv:2012.03597) — pyramidal scale counting for remote sensing; check for GitHub with weights [ASSUMED to exist based on paper context]
- Any arXiv 2024–2025 paper for palm density or counting model with weights

**Expected outcome for density models:** Low probability of finding UAV-native density-map models specifically for oil palm with public weights. Most density estimation research uses generic crowd-counting datasets (ShanghaiTech, UCF-CC-50) and the agricultural aerial application is rare.

---

## Common Pitfalls

### Pitfall 1: Confusing "dataset" repos with "model" repos

**What goes wrong:** Many GitHub repos advertise oil palm detection but provide only training datasets (images + annotations) without pretrained weights.

**Why it happens:** Agricultural RS papers often release datasets as the primary artifact; models are trained by readers.

**How to avoid:** Check specifically for: (a) a `Releases` tab with .pt/.pth/.onnx files, (b) explicit "Download pretrained model" in README, (c) a HuggingFace model card link, (d) a Google Drive / Zenodo link for weights. If only dataset found: add to Excluded Candidates with reason "Dataset only; no pretrained weights."

**Warning signs:** README says "train with" or "use our dataset" but no model download link. File tree shows only `data/`, `scripts/`, no `weights/` or `checkpoints/` directory.

---

### Pitfall 2: Confusing GSD between satellite and UAV sources

**What goes wrong:** A satellite paper may say "0.5 m resolution" (50 cm/px), while a UAV paper at the same verbal resolution means 5 cm/px when flying at 100 m AGL.

**Why it happens:** The word "high-resolution" in remote sensing is context-dependent. "High resolution satellite" = 0.5–2 m/px. "High resolution UAV" = 5–30 cm/px.

**How to avoid:** Always document GSD in cm/px (not "high resolution"). Derive from: (a) paper statement in cm/px, (b) UAV altitude + sensor specs, (c) satellite sensor (e.g., Google Earth download at stated zoom level), (d) "Sentinel-2" = 10 m/px, "WorldView-3" = 0.3 m/px.

**VHRTrees specific note:** Paper says "GSD of 0.5 m or better" — this is 50 cm/px (MEDIUM confidence satellite, Google Earth source). It matches the Canvas 0.5 m raster but not Perak (5 cm) or Rupat (8.8 cm).

---

### Pitfall 3: Roboflow API key does not unlock weight download

**What goes wrong:** Executor assumes the existing `roboflow_api_key` (used for API inference in `roboflow_algorithm.py`) will also download raw .pt weights.

**Why it happens:** The Roboflow API has separate permissions for inference vs. weight download. Inference keys are freely available; weight download requires a paid Core plan.

**How to avoid:** Run the download probe first (≤10 min). If it fails: immediately classify all Roboflow Universe models as "API inference only, weights not downloadable" and move on. Do not spend more than 30 minutes on Roboflow weight-download attempts.

---

### Pitfall 4: DINO/Swin-L models may not export to ONNX cleanly

**What goes wrong:** Large transformer backbones (DINO-Swin-L) may have dynamic shapes, attention map operators, or conditional computation that makes ONNX export fail or produce a model incompatible with onnxruntime.

**Why it happens:** ONNX export works well for CNN-family models (YOLO, RetinaNet, Faster R-CNN) but transformer backbones with window attention and positional encoding variations can hit opset compatibility issues.

**How to avoid:** Phase 5 does NOT perform ONNX export — only documents checkpoint availability and format. The "ONNX-exportable" criterion for the Phase 6 shortlist is marked as ASSUMED for transformer models until Phase 6 tests it. Document the architecture type and flag "ONNX export: verify in Phase 6" in the shortlist section.

**Warning signs:** Architecture names: DINO, Swin, ViT, Mask2Former, SAM. These require Phase 6 validation before shortlist inclusion is confirmed.

---

### Pitfall 5: Over-expanding Watch List at expense of checkpoint probing

**What goes wrong:** Executor finds many 2024–2025 papers without weights and writes long Watch List entries instead of allocating time to probe the concrete leads above.

**How to avoid:** Prioritize checkpoint-access probing over paper reading. Watch List entries should be brief (3–4 fields each). Stop adding Watch List entries after 8–10 papers unless new leads emerge. Time budget: ≥60% of executor time on source probing, ≤40% on Watch List.

---

## Code Examples

### Pattern 1: Roboflow weight-download probe

```python
# Source: docs.roboflow.com/deploy/download-roboflow-model-weights
import roboflow

# Read key from QGIS global var: qgis.utils.QgsSettings().value("roboflow_api_key")
# For testing outside QGIS, set manually
api_key = "<roboflow_api_key from QGIS global var>"

rf = roboflow.Roboflow(api_key=api_key)

# R1: Manfred Michael oil-palm-detection (version 11 is latest as of Phase 3)
project = rf.workspace("manfred-michael").project("oil-palm-detection")
version = project.version(11)
model = version.model
# This will raise HTTP 403 if not on Core plan:
model.download()  # Downloads 'weights.pt' if authorized

# R2: UiTM oil-palm-aerial-detection (version 1)
project2 = rf.workspace("uitm-14tb6").project("oil-palm-aerial-detection")
version2 = project2.version(1)
version2.model.download()
```

**Expected output if free tier:** HTTP 403 Forbidden or SDK error mentioning Core plan requirement.

**Document outcome as:** "API inference only, weights not downloadable (free tier roboflow_api_key)" per D-06.

---

### Pattern 2: arXiv HTML search for GitHub links

```python
# Pattern: Find GitHub repo links in arXiv HTML pages
# Example for paper 2509.12400
import requests
from bs4 import BeautifulSoup

url = "https://arxiv.org/html/2509.12400v2"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'html.parser')
# Find all links containing 'github.com'
github_links = [a['href'] for a in soup.find_all('a', href=True)
                if 'github.com' in a.get('href', '')]
print(github_links)
```

For executor: use WebFetch on the arxiv.org/html/[ID] URL with the prompt "List all GitHub repository links mentioned in the paper."

---

### Pattern 3: VHRTrees Google Drive access check

```python
# Pattern: Confirm Google Drive link is publicly accessible (no login required)
# Google Drive links format: https://drive.google.com/file/d/{FILE_ID}/view
# Test if accessible via wget or curl without authentication:
import requests
drive_url = "<URL from VHRTrees README experiment table>"
resp = requests.head(drive_url, allow_redirects=True)
# If status 200 and no redirect to Google login: accessible
print(resp.status_code, resp.url)
```

For executor: use WebFetch on the Google Drive link with prompt "Is this file downloadable without Google login? What is the file size and name?"

---

## Report Structure Recommendation

### 05-EXTENDED-REPORT.md Layout

```markdown
# Phase 5 Extended Report — Palm / Tree-Crown Detection Model Candidates

**Generated:** [date]
**Phase:** 05-extended-palm-detection-model-research
**Purpose:** Addendum to 03-CANDIDATE-REPORT.md. Documents new candidates NOT in Phase 3 (B1–N4). Phase 3 baseline: B1–N3 (see .planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md).

---

## Main Candidate Catalog (Phase 5 additions)

[Table with columns: Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm | Canvas 0.5m | Output type | QGIS path]

---

## Restricted / API-Only Access

[Same format as Phase 3 "Restricted Access" section: Roboflow R1/R2 re-probe result + R4–R8 status]

---

## Excluded Candidates (No Pretrained Weights / Out of Scope)

[Same format as Phase 3: candidate | reason excluded]

---

## Watch List (2024–2025 Papers Without Public Checkpoints)

[Format: Model name | Architecture | GSD | Why interesting | Check date for checkpoint release]

---

## Phase 6 Shortlist

Top 5 candidates meeting ALL D-14 criteria:
1. ONNX-exportable
2. SE Asia domain match
3. qgis_gdal_env Python 3.12 compatible (no Detectron2, no C++ extensions)
4. Localization output (bbox or centroid)

[Ordered table or ranked list with rationale per candidate]

---

## Sources Probed (Phase 5)

[Appendix: one row per source, same pattern as Phase 3 Sources Probed table]
Sources: L (SelvaBox/CanopyRS) | M (VHRTrees) | N (arXiv/IEEE re-probe) | O (MDPI/ISPRS) | P (ModelScope) | Q (OpenMMLab) | R (CVPR/ICCV 2024) | S (Roboflow re-probe) | T (counting/density)
```

### Phase 6 Shortlist Evaluation Criteria (D-14)

Apply this checklist to each main-table candidate to determine shortlist eligibility:

```
Candidate: [Name]
1. ONNX-exportable? [YES / NO / ASSUMED — verify in Phase 6]
   - YOLOv5/v7/v8/v9/v11/v12: YES (via ultralytics)
   - RT-DETR: POSSIBLE (via ultralytics with caveats)
   - DINO/Swin-L: ASSUMED — needs Phase 6 verification
   - Mask R-CNN (Detectron2): NO (blocked same as N1 detectree2)
   - TensorFlow SavedModel: NO (cannot use onnxruntime without explicit ONNX export)

2. SE Asia domain match? [YES / PARTIAL / NO]
   - YES: trained on Malaysia/Indonesia oil palm data
   - PARTIAL: tropical forest crowns (not oil palm specific but similar canopy)
   - NO: temperate forest, different hemisphere

3. qgis_gdal_env Python 3.12 compatible? [YES / NO / UNKNOWN]
   - YOLO variants: YES (ultralytics is pip-installable, no C++ ext required)
   - DeepForest: UNKNOWN (may have scipy/rasterio version conflicts)
   - Detectron2 any: NO

4. Localization output (bbox or centroid)? [YES / NO]
   - bbox / centroid: YES
   - density-map / count-only: NO
   - pixel probability: NO
```

---

## Validation Architecture

No automated testing applies to this phase. This is a research/documentation phase. Validation criteria are:

### Research Completeness Checks

| Check | How to Verify | Pass Condition |
|-------|--------------|----------------|
| All 9 sources probed (L–T) | "Sources Probed" appendix in 05-EXTENDED-REPORT.md lists all sources | Each source has a status (candidates found / probed-none-found / skipped-with-reason) |
| Every main-table candidate has a checkpoint URL | Scan the main table "Download URL" or "Format" column | No "TBD" or blank in URL column |
| Phase 6 shortlist has ≤5 entries | Count rows in shortlist | 0–5 entries (0 is valid if no candidates meet all D-14 criteria) |
| Watch List entries have no checkpoint URL | Watch List is not the main table | Every Watch List entry has "No public checkpoint as of [date]" |
| Roboflow probe documented | Sources Probed row for Source S | Either "weights downloaded: [file]" or "API inference only, weights not downloadable (free tier)" |
| Phase 3 models not re-documented | Check 05-EXTENDED-REPORT.md | No rows for B1/B2/B3/B4/H1/H2/H3/N1/N2/N3 in main table |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CNN-based object detection only (YOLOv5/v8) | Foundation model detection (DINO-Swin, SAM-based) | 2024 | Larger models; better zero-shot; ONNX export harder |
| Single-resolution training | Multi-resolution pipeline (3–10 cm/px joint training) | 2025 (SelvaBox) | Better generalization across GSD tiers |
| Oil-palm-specific datasets only | Pan-tropical crown datasets (83k+ crowns) | 2025 (SelvaBox) | Better tropical domain generalization |
| Roboflow API keys give weight download | Roboflow API keys = inference only; weight download = paid Core plan | 2023+ (current policy) | R1/R2 weights remain inaccessible on free tier |

**Deprecated/outdated:**
- `Papers With Code` as a search source: redirects to HuggingFace trending (Phase 3 finding) — use arXiv directly instead

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | CanopyRS pretrained weights are publicly downloadable (paper states "made public") | E1 candidate lead | Executor spends time on dead URL; add to Watch List instead |
| A2 | pinakinathc/oil-palm-detection has no pretrained checkpoint (search result said "no releases") | E4 candidate lead | A checkpoint exists in the repo files but was missed; executor should check README files directly |
| A3 | roboflow_api_key is a free-tier inference key that does not allow weight download | Source S re-probe | If it is a paid key, R1/R2 weights might be downloadable — test before concluding |
| A4 | DINO-Swin-L backbone (CanopyRS) is hard to export to ONNX | Common Pitfalls | If CanopyRS provides ONNX weights directly, it becomes a top shortlist candidate |
| A5 | TorchGeo has no palm/tree-crown detection pretrained weights (only backbone encoders) | Source priority LOW | A community model or new release in 0.9.0 could include detection heads |
| A6 | VHRTrees Google Drive weight links are publicly accessible without Google login | E2 executor action | If login required, weights are effectively blocked |
| A7 | PRISM (Zippppo/github.com) has not released pretrained weights | E3 candidate lead | Paper is Sep 2025 — weights may have been released since; executor must check |
| A8 | MDPI/ISPRS 2024–2025 palm papers have linked GitHub repos with weights | Source O strategy | Most papers may have GitHub code but no pretrained checkpoint download |
| A9 | ModelScope has no palm-specific pretrained detection models | Source P priority LOW | Chinese agricultural AI sector may have models not indexed by English-language web search |
| A10 | GSD for pinakinathc/oil-palm-detection is 5–15 cm/px (UAV drone) | E4 candidate lead | Could be ground-level photography; check dataset sample images |

---

## Open Questions

1. **Does CanopyRS/SelvaBox provide ONNX weights directly, or only PyTorch?**
   - What we know: Paper states weights are public; architecture is DINO-Swin-L.
   - What's unclear: Whether the Model Zoo provides an ONNX-ready export or only .pt/.pth.
   - Recommendation: Executor visits the Model Zoo documentation first; if only .pt, document architecture and flag "ONNX export: Phase 6 verification required."

2. **Is VHRTrees GSD 0.5 m/px (matching Canvas) or 0.5 km/px (too coarse)?**
   - What we know: Paper says "GSD of 0.5 m or better" and imagery is from Google Earth. [CITED: frontiersin.org WebFetch]
   - What's unclear: The initial WebFetch of the GitHub README mentioned "GSD of 0.5 km" which may have been a text extraction artifact.
   - Recommendation: Executor reads the Frontiers paper directly (WebFetch on frontiersin.org/articles/10.3389/ffgc.2024.1495544/full) and confirms GSD in the dataset description section. Expected answer: 0.5 m/px (satellite VHR), not 0.5 km.

3. **Will the Roboflow API key unlock R1 or R2 weight download?**
   - What we know: Roboflow documentation says weight download requires paid Core plan.
   - What's unclear: The project's key may have been provisioned at a higher tier than free.
   - Recommendation: Executor runs the download probe (Pattern 1 above) first, spends max 15 minutes, documents outcome, moves on.

4. **How many new main-table candidates will Phase 5 find?**
   - What we know: Research session found 3 high-confidence leads (E1 SelvaBox, E2 VHRTrees, E3 PRISM TBD) and several counting-tier / API-only entries.
   - What's unclear: ModelScope, MDPI/ISPRS, CVPR/ICCV probes may yield additional candidates.
   - Recommendation: Target ≥5 new main-table entries (comparable to Phase 3's 10 entries). If fewer are found, document thoroughly in Watch List and Sources Probed.

5. **Is the Google Forest Data Partnership community palm model ONNX-compatible?**
   - What we know: Format is TensorFlow SavedModel. Output is pixel probability at 10 m/px.
   - What's unclear: Whether a PyTorch port exists that could be ONNX-exported.
   - Recommendation: Document as TF SavedModel; classify as "not applicable" for QGIS path (10 m/px and no localization output). Phase 6 shortlist ineligible.

---

## Environment Availability

Step 2.6 SKIPPED — Phase 5 is a documentation/research phase with no external tool dependencies beyond web search. No new Python packages or CLI tools are required by the executor.

---

## Security Domain

Security enforcement not applicable to this phase. Phase 5 is a research/documentation phase that performs no authentication (beyond the existing `roboflow_api_key` read from QGIS global var), no data storage, and no inference execution.

---

## Sources

### Primary (HIGH confidence)
- Frontiers in Forests and Global Change — VHRTrees article (WebFetch verified): GSD, weight availability, YOLO architectures
- arxiv.org/html/2507.00170 — SelvaBox paper: dataset size, tropical scope, weight release statement
- arxiv.org/html/2509.12400v2 — PRISM paper: GitHub repo, dataset on Zenodo, architecture list
- docs.roboflow.com/deploy/download-roboflow-model-weights — Weight download: paid plan required (WebFetch verified)
- Google Earth Engine catalog — Community Palm Model: 10 m/px, SE Asia coverage, TF format, CC-BY 4.0 NC

### Secondary (MEDIUM confidence)
- github.com/RSandAI/VHRTrees README (WebFetch): 8 Google Drive weight links, YOLOv5/v7/v8/v9
- github.com/hugobaudchon/CanopyRS (WebFetch): architectures listed, Model Zoo referenced at external docs site
- github.com/google/forest-data-partnership (WebFetch): /models directory with downloadable TF models

### Tertiary (LOW confidence / ASSUMED)
- OpenMMLab MMDetection zoo: no palm-specific checkpoints (based on WebSearch; not directly verified against zoo index)
- TorchGeo: backbone encoders only, no detection heads (based on WebSearch of documentation; not directly verified at models.html)
- ModelScope: no palm models found (WebFetch returned only site header; full search not possible without platform login)
- pinakinathc/oil-palm-detection: no releases (WebSearch summary; not directly verified against repo file tree)

---

## Metadata

**Confidence breakdown:**
- Candidate leads (E1–E7): MEDIUM — found via web search and partial WebFetch; checkpoint access not confirmed until executor visits
- Source-by-source strategy: HIGH — based on verified search findings and platform documentation
- Report structure: HIGH — directly derived from locked decisions D-01 to D-16 and Phase 3 style guide
- Plan structure recommendation: HIGH — research-execute pattern with clear wave dependency is standard

**Research date:** 2026-06-19
**Valid until:** 2026-09-01 (model zoo URLs change; Roboflow pricing policy is stable; arXiv papers are permanent)
