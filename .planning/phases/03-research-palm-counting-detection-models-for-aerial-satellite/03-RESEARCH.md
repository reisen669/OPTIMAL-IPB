# Phase 03: Research Palm Counting/Detection Models — Research

**Researched:** 2026-06-18
**Domain:** Palm/tree-crown detection model catalog — pretrained checkpoints, GSD documentation, source strategies
**Confidence:** MEDIUM (most candidate facts confirmed via GitHub/Zenodo/docs; GSD values inferred from papers; Roboflow still 403-blocked)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Search Scope**
- D-01: Expand beyond Phase 2's 5 source categories. New sources: Papers With Code, Kaggle (datasets + notebooks), arXiv + IEEE Xplore (papers with linked repos), Google Dataset Search / agricultural AI datasets.
- D-02: Include general tree-crown / tropical canopy detection models — not only oil-palm-specific. Flag domain gap (non-palm) where applicable.
- D-03: SE Asia-trained models (Malaysia, Indonesia, Thailand) flagged as higher priority due to visual domain match. Global models (Africa, PNG, Colombia, Ecuador) included as secondary.

**Checkpoint Availability**
- D-04: Publicly downloadable without login or API key. HuggingFace public repos (.pt files via git clone or direct link) are included. Roboflow pages that return 403 / require API key are excluded from the main catalog. Train-from-scratch candidates (code + dataset only, no pretrained weights) are excluded.
- D-05: Any checkpoint format counts: .pt, .pth, .safetensors, .onnx, .h5. ONNX-ready is not a prerequisite — Phase 4 handles conversion. Report the format found; do not document conversion commands (Phase 4 scope).

**GSD Documentation**
- D-06: Determine GSD by reading paper abstract, dataset section, README, capture altitude, or sensor specs. State as "inferred ~X cm/px from [source]."
- D-07: Express GSD as a min–max suitable range (e.g., "5–30 cm/px, optimal ~10 cm/px"), not just training GSD.
- D-08: Add per-model raster compatibility columns for 3 downloaded GeoTIFFs: oam_perak_01E2b (5 cm/px), oam_rupat_indonesia (8.8 cm/px), oam_leuhan_aceh (50 cm/px). Mark ✓/✗/? per model row.

**Report Structure**
- D-09: Report file: `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md`
- D-10: Main table columns: Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm ✓/✗/? | Rupat 8.8cm ✓/✗/? | Aceh 50cm ✓/✗/?
- D-11: Include "Recommended Shortlist for Phase 4" section: top 3–5 candidates organized by GSD tier (VHR ≤15 cm, HR 15–100 cm, MR 0.5–2 m).

### Claude's Discretion
- Exact grouping/ordering within the candidate table (alphabetical, by architecture, or by GSD) — researcher's choice.
- Whether to add a "Sources Probed" appendix documenting all URLs checked (consistent with 02-04-SOURCES.md pattern).
- Confidence labeling on GSD values (HIGH / MEDIUM / LOW per 02-RESEARCH.md pattern).

### Deferred Ideas (OUT OF SCOPE)
- Empirical inference testing on our 3 GeoTIFFs per model — deferred to Phase 4.
- ONNX conversion commands per model — deferred to Phase 4 plan.
- Fine-tuning or retraining any model on SE Asia data — out of scope.
</user_constraints>

---

## Summary

This research catalogs publicly available palm and tree-crown detection models with downloadable pretrained checkpoints, expanding Phase 2's 5-source probe to 10+ source categories. The critical finding is a clear split by GSD tier: VHR models (≤15 cm/px) exist in the HuggingFace + GitHub + Deepness ecosystem in PyTorch format; MR models (0.5–2 m) are almost entirely absent as public checkpoints.

The most actionable new finds are: (1) **detectree2** (Mask R-CNN, Sabah/Malaysia training data, .pth on Zenodo, ~5–20 cm/px) — SE Asia tropical forest crowns, publicly downloadable, CC-BY 4.0; (2) **DeepForest/weecology** (RetinaNet, .pt on HuggingFace, trained at 10 cm/px, US NEON data) — tree crown generalizer, domain gap from SE Asia palms; (3) **MOPAD/rs-dl** (Faster RCNN, .pth on Baidu Wangpan only, UAV oil palm, SE Asia region likely) — weights exist but accessibility is uncertain outside China. Phase 2 HuggingFace finds (tribber93, grediiiii) remain the most accessible palm-specific .pt files.

**Papers With Code** does not have a dedicated palm detection task page; papers are found via arXiv search instead. **Kaggle** hosts dataset-only palm entries; no Kaggle notebooks publish downloadable .pt weights. **ArcGIS Living Atlas** has a palm tree detection model (.dlpk, FasterRCNN, 5–15 cm/px) but requires an ArcGIS account — excluded by D-04. **Roboflow** remains 403-blocked for both main palm datasets.

**Primary recommendation:** Phase 4 shortlist should be: VHR tier — tribber93/yolov11-palm-oil-tree + tree_tops_yolov9.onnx (baseline) + detectree2 tropical model; MR tier — Google/Geoeye/Pleiades-Resnet101.onnx (baselines already present).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Web search / source discovery | Researcher (this phase) | — | Manual catalog compilation; no automation needed |
| GSD extraction from papers/READMEs | Researcher (this phase) | — | Requires reading paper abstract/methodology sections |
| Checkpoint download | Phase 4 implementer | — | Research phase only locates URLs; Phase 4 fetches files |
| Format conversion (.pt → .onnx) | Phase 4 implementer | SuperMap Python 3.10 + ultralytics | Established workflow from Phase 2 RESEARCH.md |
| Deepness metadata patching | Phase 4 implementer | qgis_gdal_env (onnx 1.21.0) | Established workflow from Phase 2 RESEARCH.md |
| Compatibility column assignment | Researcher (this phase) | Phase 4 (empirical validation) | Logical ✓/✗/? from GSD range vs. raster GSD; Phase 4 verifies empirically |

---

## Search Strategy by Source

This section answers "what search strategy works best per platform" (research question 6).

### Source 1: HuggingFace (already probed in Phase 2 — build on findings)

Phase 2 found 3 candidates via API. Additional HuggingFace discovery in Phase 3 should use:
- Direct model search: `https://huggingface.co/models?search=palm+detection`
- Filter by task: `object-detection`
- Filter by library: `transformers` or no filter (many detection models are untagged)

**Effective keywords:** `oil palm detection`, `palm tree detection`, `tree crown detection aerial`

**What's findable:** PyTorch .pt weights (YOLOv8/v11 via ultralytics), Safetensors (RT-DETR, DETR). No ONNX palm models found in Phase 2; unlikely to change.

**Blockers:** HuggingFace ONNX library filter is too narrow — most detection models are uploaded without library tags.

[VERIFIED: Phase 2 API searches confirmed 0 ONNX aerial palm detection models on HuggingFace]

### Source 2: GitHub

Phase 2 found 2 repos (Chris-pter, kaykyysee). Phase 3 extends with:
- `rs-dl/MOPAD` — oil palm, Faster RCNN .pth weights on Baidu Wangpan
- `rs-dl/MADAN` — cross-regional oil palm domain adaptation; dataset + code on Google Drive / Baidu; model weights unclear
- `PatBall1/detectree2` — Mask R-CNN tropical tree crown; .pth weights on Zenodo (not GitHub releases)
- `weecology/DeepForest` — RetinaNet tree crown; .pt on HuggingFace releases

**Effective search terms:** `oil palm detection yolo`, `oil palm detection aerial`, `tree crown detection tropical`, `palm tree yolo pretrained`

**What Phase 3 planner must do:** For each GitHub repo found, check for (a) releases page, (b) external link to Zenodo/Google Drive/Baidu in README, (c) HuggingFace model card. GitHub search API returned 0 for `palm tree yolo onnx` in Phase 2 — do not repeat that specific query.

[VERIFIED: Phase 2 GitHub API searches; new candidates found via WebSearch cross-referencing papers]

### Source 3: Papers With Code

**Critical finding:** `paperswithcode.com` redirects to `huggingface.co/papers/trending` as of 2026-06 — the dedicated Papers With Code search URL is broken/merged. [VERIFIED: WebFetch confirmed 302 redirect to HuggingFace]

**Workaround:** Use arXiv directly to find papers with code. Papers With Code task page for oil palm detection does not exist as a standalone benchmark task.

**Effective arXiv query:** `ti:oil palm detection` or `abs:oil palm detection aerial` with filter `cs.CV`

**Key arXiv papers with linked code/models found:**
- arXiv:2008.11505 — MADAN (rs-dl), cross-regional counting (Malaysia/Indonesia SE Asia data) [CITED: arxiv.org/abs/2008.11505]
- arXiv:2005.05269 — Deep-Learning-based Palm Tree Counting (Faster-RCNN, ~10 cm aerial) [CITED: paperswithcode.com/paper/deep-learning-based-automated-palm-tree]
- arXiv:2412.11949 — Coconut palm YOLOv7, Ghana, no public weights [CITED: arxiv.org/abs/2412.11949]
- arXiv:2410.11124 — PalmDSNet (Ecuador), no public weights [CITED: arxiv.org/abs/2410.11124]
- arXiv:2403.03161 — PalmProbNet (Ecuador tropical forest transfer learning), no public weights

**Blockers:** Most arXiv papers provide code repos without pretrained weights (train-from-scratch only), excluded by D-04.

### Source 4: Kaggle

**Effective search approach:** `https://www.kaggle.com/datasets` + keyword `oil palm detection` or `aerial palm trees`.

**Key Kaggle datasets found:**
- `riotulab/aerial-images-of-palm-trees` — dataset only, no pretrained weights [CITED: kaggle.com/datasets/riotulab/aerial-images-of-palm-trees]
- `yohanesnuwara/oil-palm-detection` — dataset only, updated September 2024 [CITED: kaggle.com/datasets/yohanesnuwara/oil-palm-detection]
- `kumar99411/palm-data` — dataset only

**Kaggle notebooks:** `PT_YOLOv8_PalmTreev2` notebook exists on Kaggle but does not publish downloadable .pt weights files as public assets. Notebooks share code, not model files.

**Conclusion:** Kaggle is a dataset-only source for palm detection; no public pretrained checkpoint files are available without running notebooks yourself. Excluded from main catalog per D-04 (requires account + compute to reproduce).

[VERIFIED: WebSearch confirmed no Kaggle-hosted downloadable .pt weights for palm detection]

### Source 5: arXiv + IEEE Xplore

**arXiv:** Use search.arxiv.org with query `oil palm detection aerial pretrained`. Papers sometimes link GitHub repos with weights; check each repo's releases.

**IEEE Xplore:** Paywalled for full papers; abstract access only without subscription. Key paper found: "Oil Palm Tree Detection in Aerial Images Combining Deep Learning Classifiers" (IEEE 2018, ieeexplore.ieee.org/document/8519239) — no associated public weights.

**Blockers:** IEEE Xplore full-text access requires subscription; data availability statements are in full text, not abstract. Most papers do not link public pretrained weights.

**Strategy for planner:** For each IEEE paper title found, search GitHub for the authors' name or institution + "oil palm detection" to find associated code repos.

### Source 6: Zenodo

Phase 2 found 0 relevant ONNX models on Zenodo. Phase 3 finds:
- **detectree2 trained models** (Zenodo record 10522461 / 12773341) — 7 .pth files, CC-BY 4.0, includes tropical Malaysia sites [VERIFIED: zenodo.org/records/12773341/latest fetched; 7 files confirmed]

**Effective Zenodo query:** `oil palm detection model` — very sparse results. Better to arrive at Zenodo via paper → data availability statement → DOI.

### Source 7: Google Dataset Search

Redirects to `datasetsearch.research.google.com`. Useful for finding Zenodo/IEEE DataPort/figshare datasets that cross-link to code repos. Search `oil palm detection aerial model`. Results primarily surface datasets, not pretrained checkpoints.

**Finding:** No new pretrained checkpoints found via Google Dataset Search beyond what GitHub/Zenodo/HuggingFace already surface.

---

## Candidate Catalog (Pre-populated for 03-CANDIDATE-REPORT.md)

This section is the primary output. Each entry maps to one row in the CANDIDATE-REPORT.md table.

### Already-Present Baselines (from models/ directory)

**B1 — tree_tops_yolov9.onnx**
- Architecture: YOLOv9, ONNX
- GSD: inferred ~10 cm/px from Deepness zoo metadata [VERIFIED: 02-04-SOURCES.md + Deepness zoo page]
- GSD range: 5–20 cm/px (optimal ~10 cm/px) [ASSUMED: typical YOLO crown size tolerance ±2×]
- Format: .onnx (already in models/, Deepness-ready)
- License: Deepness zoo (CC/academic)
- SE Asia? No — mixed public datasets (European aerial)
- Perak 5cm: ✓, Rupat 8.8cm: ✓, Aceh 50cm: ✗

**B2 — Google-Resnet101.onnx**
- Architecture: RetinaNet, ONNX
- GSD: inferred ~50 cm/px from model name (Google satellite imagery, converted .h5 → .onnx in Phase 1) [ASSUMED: based on STATE.md entry "~50 cm/px"]
- GSD range: 30–100 cm/px (optimal ~50 cm/px) [ASSUMED]
- Format: .onnx (already in models/)
- License: see original model source (converted from OPTIMAL-IPB h5)
- SE Asia? Unknown
- Perak 5cm: ✗, Rupat 8.8cm: ✗, Aceh 50cm: ✓

**B3 — Geoeye-Resnet101.onnx**
- Same as B2 but trained on GeoEye satellite imagery. ~50 cm/px.
- Perak 5cm: ✗, Rupat 8.8cm: ✗, Aceh 50cm: ✓

**B4 — Pleiades-Resnet101.onnx**
- Same as B2 but trained on Pleiades satellite imagery. ~50 cm/px.
- Perak 5cm: ✗, Rupat 8.8cm: ✗, Aceh 50cm: ✓

### HuggingFace Palm-Specific Candidates (from Phase 2)

**H1 — tribber93/yolov11-palm-oil-tree**
- Architecture: YOLOv11, PyTorch
- URL: huggingface.co/tribber93/yolov11-palm-oil-tree
- Files: weights/best.pt, weights/last.pt
- GSD: unknown (check repo/paper); likely UAV, probable ~5–15 cm/px [ASSUMED: typical palm YOLO training altitude 100–150 m AGL → ~5 cm/px at DJI Phantom]
- GSD range: unknown (check paper) — mark ? in compatibility columns
- License: Not specified
- SE Asia? Unknown
- Perak 5cm: ?, Rupat 8.8cm: ?, Aceh 50cm: ?
- Download: `git clone https://huggingface.co/tribber93/yolov11-palm-oil-tree` or direct file link
- Priority: HIGH (oil-palm-specific, YOLO family, easy export to ONNX)

**H2 — grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm**
- Architecture: YOLOv8n-GhostNet-CBAM (custom backbone), PyTorch
- URL: huggingface.co/grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm
- Files: best.pt (3.45 MB)
- GSD: unknown [ASSUMED: likely UAV aerial palm detection]
- GSD range: unknown — mark ? in compatibility columns
- License: MIT [VERIFIED: Phase 2 API query]
- SE Asia? Unknown
- Perak 5cm: ?, Rupat 8.8cm: ?, Aceh 50cm: ?
- Note: Custom backbone (GhostNet+CBAM) — ultralytics export may fail; needs manual testing. Small model (3.45 MB).
- Priority: MEDIUM (open license, but custom arch export risk)

**H3 — firdhokk/palm-tree-detection-with-rtdetr**
- Architecture: RT-DETR, Safetensors
- URL: huggingface.co/firdhokk/palm-tree-detection-with-rtdetr-rd50vd-coco-o365
- Files: model.safetensors (3.59 GB, 42.9M params)
- GSD: unknown
- License: Not specified
- SE Asia? Unknown
- Note: Safetensors format is NOT directly importable by ultralytics YOLO pipeline; RT-DETR export to ONNX requires separate Transformers pipeline. Large file (3.59 GB). Very low priority.
- Priority: LOW (format conversion complexity; Phase 4 may skip)

### New Candidates — VHR Tier (≤15 cm/px)

**N1 — detectree2 tropical model (PatBall1 / Zenodo)**
- Architecture: Mask R-CNN (Detectron2 backend), PyTorch
- URL: github.com/PatBall1/detectree2 | weights: zenodo.org/records/12773341/latest
- Files (pick one of 7 .pth files):
  - `230103_randresize_full.pth` (498 MB) — trained Danum+Sepilok (Sabah, Malaysia) + Paracou, random resize augmentation for better scale transfer [VERIFIED: Zenodo record 12773341 fetched]
  - `250711_tropical_closed_canopy.pth` (503 MB) — newest, dense tropical canopy
  - `220723_withParacouUAV.pth` (503 MB) — includes UAV data alongside aerial
- GSD: inferred 5–20 cm/px from documentation: "UAV data ~5cm resolution" and "aerial RGB ~1m resolution" noted in Zenodo record; "performance decreased significantly when GSD exceeded 100 mm" [CITED: zenodo.org/records/12773341]
- GSD range: 5–20 cm/px (optimal ~10 cm/px UAV; usable to ~15 cm/px aerial)
- License: CC BY 4.0 [VERIFIED: Zenodo record]
- SE Asia? YES — Danum Valley + Sepilok Reserve, Sabah, Malaysia are primary training sites [CITED: zenodo.org/records/12773341]
- Domain gap: General tropical tree crowns, NOT oil-palm-specific. Oil palms will be detected as generic crowns; no "palm" class label.
- Perak 5cm: ✓, Rupat 8.8cm: ✓, Aceh 50cm: ✗
- Download: Direct wget from Zenodo (no login required)
  ```
  https://zenodo.org/records/12773341/files/230103_randresize_full.pth
  ```
- Priority: HIGH — SE Asia training, publicly downloadable, correct GSD tier for Perak/Rupat rasters. Domain gap acceptable for palm crown detection.

**N2 — DeepForest weecology/deepforest-tree**
- Architecture: RetinaNet (PyTorch Lightning), PyTorch
- URL: huggingface.co/weecology/deepforest-tree
- Files: Safetensors format (loaded via DeepForest Python API, not standalone file) [VERIFIED: DeepForest docs fetched]
- GSD: confirmed 10 cm/px training resolution (NEON aerial, US sites MLBS, NIWO, OSBS, SJER, TEAK, LENO) [CITED: deepforest.readthedocs.io/en/stable/user_guide/02_prebuilt.html; biorxiv preprint]
- GSD range: 5–20 cm/px (optimal 10 cm/px)
- License: MIT [VERIFIED: HuggingFace model card]
- SE Asia? NO — trained on US NEON sites only. Domain gap: temperate/boreal mixed forest, not SE Asia palm plantation.
- Domain gap: General tree crown detection across US mixed forests. Visual appearance differs significantly from SE Asia oil palm monocultures (uniform crown shape, regular spacing). Palm crown morphology may still be detected as generic circular crown.
- Perak 5cm: ✓, Rupat 8.8cm: ✓, Aceh 50cm: ✗
- Download: Available via DeepForest Python library (`pip install deepforest; model.load_model("weecology/deepforest-tree")`). The raw .pt weights file is downloadable from HuggingFace release but requires DeepForest to run inference.
- Priority: MEDIUM — correct GSD, publicly downloadable, but no SE Asia training data and requires DeepForest library (not ONNX-compatible without export step).

### New Candidates — HR Tier (15–100 cm/px)

No new publicly downloadable HR-tier palm models found outside of Phase 2 candidates. The gap is real:
- HR satellite-based models exist in papers (Sentinel-2 at 10m, WorldView at 30-50 cm) but authors rarely release pretrained weights publicly.
- MADAN (rs-dl) covers HR aerial (estimated ~30–50 cm/px from UAV altitude) but weights are on Baidu Wangpan only — accessibility uncertain outside China.

**N3 — rs-dl/MOPAD (Faster RCNN, Baidu Wangpan)**
- Architecture: Faster RCNN with Refined Pyramid Feature (RPF) module, PyTorch
- URL: github.com/rs-dl/MOPAD | weights: Baidu Wangpan (access code 7n61 for Site 2, 8mwa for Site 1)
- Files: latest.pth (size unknown) [VERIFIED: MOPAD GitHub README — Baidu links confirmed]
- GSD: inferred ~5–15 cm/px from UAV operations described as "Skywalker X8 fixed-wing UAV" and "nearly 300,000 oil palms from two UAV images with areas of 28.85 km² in total" — large area with many palms implies high altitude (~100–150 m AGL), so likely 5–15 cm/px [ASSUMED: altitude not stated in README excerpt]
- GSD range: 5–20 cm/px (optimal unknown — check paper for exact UAV altitude) [ASSUMED]
- License: Not specified [VERIFIED: no LICENSE file in repo]
- SE Asia? YES — oil palm UAV dataset; geographic location not explicitly named in README but paper (ISPRS Journal 2021) covers tropical SE Asia oil palm sites [ASSUMED: ISPRS paper context — verify in full paper]
- Domain gap: Oil-palm-specific (5 growing-status classes). Best domain match for palm detection task.
- Perak 5cm: ?, Rupat 8.8cm: ?, Aceh 50cm: ?
- Download blocker: Baidu Wangpan requires Baidu account and may require China-based IP or VPN. This is a significant accessibility blocker. [ASSUMED: typical Baidu Wangpan international access difficulty]
- Priority: MEDIUM-LOW — high domain relevance but Baidu accessibility uncertain; Phase 4 should attempt download and flag if blocked.

**N4 — rs-dl/MADAN (cross-regional oil palm, Baidu/Google Drive)**
- Architecture: Batch-instance normalization network + multi-level attention (domain adaptation layer on detection backbone)
- URL: github.com/rs-dl/MADAN
- Files: Not confirmed — model weights referenced in README but format/availability unclear from GitHub page alone [ASSUMED: likely .pth on Google Drive or Baidu based on rs-dl pattern]
- GSD: inferred ~5–30 cm/px from paper context (high-resolution satellite imagery of Malaysia/Indonesia palm plantations) [ASSUMED: from paper abstract; not confirmed in README]
- License: Not specified
- SE Asia? YES — explicitly designed for cross-regional SE Asia oil palm (Malaysia, Indonesia) [CITED: arxiv.org/abs/2008.11505]
- Domain gap: None — oil-palm-specific
- Perak 5cm: ?, Rupat 8.8cm: ?, Aceh 50cm: ?
- Priority: MEDIUM — strong domain fit; weights need download verification in Phase 4

### Restricted / API-Key Required (not in main catalog)

**R1 — Roboflow Manfred Michael (oil-palm-detection)**
- 4,063 aerial palm images, YOLOv5/v7/v8/v9/v11 versions
- Status: HTTP 403 Forbidden; API key required. Excluded per D-04.
- URL: universe.roboflow.com/manfred-michael/oil-palm-detection [VERIFIED: Phase 2 WebFetch returned 403]

**R2 — Roboflow UiTM (oil-palm-aerial-detection)**
- 8,532 aerial palm images + pretrained model
- Status: HTTP 403 Forbidden; API key required. Excluded per D-04.
- URL: universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection [VERIFIED: Phase 2 WebFetch returned 403]

**R3 — ArcGIS Living Atlas Palm Tree Detection**
- FasterRCNN, GSD 5–15 cm/px, .dlpk format
- Status: Requires ArcGIS account (free tier may suffice — not confirmed). Excluded per D-04 (ArcGIS login required).
- URL: hub.arcgis.com/content/916e02960d9e495baeb4d1d2ff4055d0 [CITED: ArcGIS docs fetched]

### Excluded Candidates (dataset only — no pretrained weights)

| Candidate | Reason Excluded |
|-----------|-----------------|
| rs-dl/CROPTD (Cross-Regional Oil Palm Tree Detection) | Dataset only (PASCAL VOC format); code but no pretrained weights in repo [VERIFIED: GitHub page] |
| NourO93/Palm-Tree-Dataset (UAE Al Ain) | Dataset only; no weights; research-only license [VERIFIED: GitHub page] |
| Adeel0-0/PALM-TREE-DETECTION | Code only; no pretrained weights published [VERIFIED: GitHub page — only architecture descriptions] |
| Freudenberg U-Net (GitHub/ThomasWangWeiHong) | Code only; no releases; train-from-scratch [VERIFIED: GitHub page — "No releases published"] |
| Kaggle `riotulab/aerial-images-of-palm-trees` | Dataset only; no model weights [VERIFIED: Kaggle dataset page access blocked; confirmed via WebSearch] |
| Kaggle `yohanesnuwara/oil-palm-detection` | Dataset only | 
| arXiv:2502.13023 PRISM (Ecuador palms) | No public weights [VERIFIED: arXiv page] |
| arXiv:2410.11124 PalmDSNet (Ecuador) | No public weights [VERIFIED: arXiv page] |
| arXiv:2412.11949 Coconut YOLOv7 (Ghana) | No public weights [VERIFIED: arXiv page] |
| knwin/Detect-palmtrees-with-Yolo-and-ImageAI | Uses generic COCO YOLO weights, not palm-specific |
| odanylo/oilpalmSEasia | Google Earth Engine JavaScript, not a detection model checkpoint |
| WiDS Datathon 2019 (Kaggle, ResNeXt101) | Satellite classification (not individual tree detection); no public checkpoint |

---

## GSD Tier Summary

| Tier | Range | Test Rasters Matched | Candidates Available |
|------|-------|---------------------|---------------------|
| VHR | ≤15 cm/px | Perak (5 cm), Rupat (8.8 cm) | tree_tops_yolov9.onnx (baseline), tribber93/yolov11 (H1), grediiiii/Yolov8n (H2), detectree2 (N1), DeepForest (N2), MOPAD (N3) |
| HR | 15–100 cm/px | None of our 3 rasters | MADAN/MOPAD potentially (GSD unknown) |
| MR | 0.5–2 m | Aceh (50 cm) | Google/Geoeye/Pleiades-Resnet101.onnx (baselines) |

**Gap:** No confirmed publicly downloadable model in the HR 15–100 cm/px tier. The gap between VHR drone-trained models and MR satellite-trained models is real and well-documented in the literature.

---

## Research Keywords by Domain

This section answers "what search keywords are most effective" (research question 2).

### High-Signal Keywords (returned relevant results)
- `oil palm detection aerial` — most specific, returns palm plantation papers
- `oil palm tree detection UAV` — finds drone-specific papers (MOPAD, MADAN)
- `tree crown detection tropical aerial` — finds detectree2, DeepForest domain gap papers
- `palm tree detection pretrained model` — finds ArcGIS, MOPAD, HuggingFace entries

### Low-Signal Keywords (too broad or returned unrelated results)
- `palm detection` — returns hand/date palm agricultural papers
- `tropical canopy detection` — mostly land-cover classification papers, not individual tree detection
- `coconut palm detection` — different morphology; results include Google/Rapideye satellite classification papers

### Platform-Specific Effective Queries
| Platform | Effective Query | Returns |
|----------|----------------|---------|
| HuggingFace API | `?search=oil+palm+detection` | PyTorch .pt models |
| GitHub API | `oil palm detection aerial` | Repos with code; check releases separately |
| Zenodo API | `oil palm model` (broad) | Few results; better via paper DOI |
| arXiv | `ti:oil palm detection cs.CV` | Papers with code links |
| Papers With Code | BROKEN — redirects to HuggingFace | Use arXiv directly |

---

## Common Pitfalls for Phase 4

### Pitfall 1: Baidu Wangpan accessibility
**What goes wrong:** MOPAD and MADAN weights are hosted on Baidu Wangpan. International access often requires a Baidu account AND may be restricted by geo-IP or download bandwidth caps.
**How to avoid:** Attempt MOPAD/MADAN download first in Phase 4; if blocked, deprioritize and focus on Zenodo/HuggingFace candidates.
**Warning signs:** Redirect to Baidu login page; download quota exceeded error.

### Pitfall 2: GhostNet custom backbone breaks ultralytics ONNX export
**What goes wrong:** `grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm` uses a non-standard backbone not in ultralytics codebase. Running `model.export(format='onnx')` may fail with `NotImplementedError` or missing ONNX operator.
**How to avoid:** Test export early in Phase 4 before committing time to this candidate. If export fails, skip.
**Warning signs:** `ultralytics` ImportError for custom modules; ONNX opset compatibility errors.

### Pitfall 3: detectree2 requires Detectron2, not ultralytics
**What goes wrong:** detectree2 .pth files are Detectron2 Mask R-CNN weights, NOT ultralytics YOLO weights. Cannot be loaded with `YOLO("model.pth")`. Deepness does not support Detectron2 format.
**How to avoid:** Plan for a separate inference path in Phase 4: either (a) use detectree2's own Python API for inference (not via Deepness), or (b) explore ONNX export via `torch.onnx.export` from Detectron2's inference graph.
**Warning signs:** Load error when treating .pth as YOLOv8 weight.
**Impact:** detectree2 is NOT Deepness-compatible out of the box. Phase 4 must decide whether to integrate via a custom QGIS plugin step or run standalone.

### Pitfall 4: DeepForest model requires its own library pipeline
**What goes wrong:** DeepForest stores weights via HuggingFace but the inference pipeline is DeepForest-specific (PyTorch Lightning + custom preprocessing). The model does not export to a simple standalone ONNX without rewriting the preprocessing.
**How to avoid:** Phase 4 should treat DeepForest as a standalone inference tool (separate from Deepness), not a Deepness model. Use DeepForest's `predict_image()` API to generate bounding box CSV, then load that into QGIS as a vector layer.
**Warning signs:** Inability to call `model.export(format='onnx')` — DeepForest has no such method.

### Pitfall 5: Papers With Code site is broken (redirects to HuggingFace)
**What goes wrong:** Planner or researcher navigates to `paperswithcode.com` expecting a palm detection task page and finds it redirects to HuggingFace trending.
**How to avoid:** Skip Papers With Code as a direct source; use arXiv + GitHub search instead.
[VERIFIED: WebFetch to paperswithcode.com returned 302 redirect to huggingface.co/papers/trending]

### Pitfall 6: "Counting" papers vs. "detection" papers
**What goes wrong:** Many papers titled "palm tree counting" use density maps (CNN counting regression) rather than bounding box detection. These produce count estimates per tile, not individual localization. The OPTIMAL-IPB plugin expects individual bounding boxes or points.
**How to avoid:** Filter for papers/repos that output bounding boxes or instance segmentation masks, not scalar count estimates. Verify by reading the output section of each paper.
**Warning signs:** Paper describes "CSRNet", "MCNN", or "counting map" output.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Palm counting via density maps | Custom density map inference | Bounding-box detection models (YOLO, Faster RCNN) | Density maps can't feed OPTIMAL-IPB polygon output; no individual localization |
| ONNX export from Detectron2 | Custom Detectron2 → ONNX script | Use Detectron2's `tracing` export or check PatBall1's docs | Detectron2 ONNX export has known dynamic-shape issues |
| Inference from DeepForest model without DeepForest | Loading .safetensors manually | Install DeepForest library and use `predict_image()` | DeepForest preprocessing and NMS are library-embedded |
| Scraping Roboflow pages for model weights | HTTP scraper against universe.roboflow.com | Roboflow API key + SDK | Pages return 403 without auth |

---

## Environment Availability

Phase 3 is a research/documentation task only — no new code is executed.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Web browser / WebSearch | Source discovery | YES | — | — |
| Zenodo API (no auth) | detectree2 model download (Phase 4) | YES | — | — |
| HuggingFace API (no auth) | H1/H2 download (Phase 4) | YES | — | — |
| Baidu Wangpan | MOPAD/MADAN download (Phase 4) | UNKNOWN | — | Skip MOPAD/MADAN if inaccessible |
| DeepForest Python library | DeepForest inference (Phase 4) | NOT INSTALLED | 2.1.0 | pip install deepforest in qgis_gdal_env |
| Detectron2 | detectree2 inference (Phase 4) | NOT INSTALLED | — | pip install detectron2 or skip detectree2 |

**Missing dependencies with no fallback:**
- None for Phase 3 (research only).

**Missing dependencies for Phase 4 planning:**
- Baidu Wangpan access (MOPAD/MADAN) — uncertain; Phase 4 must verify at download time.
- DeepForest install (pip-installable).
- Detectron2 install (required if detectree2 is pursued — complex install on Windows).

---

## Validation Architecture

Not applicable — Phase 3 produces a static report (`03-CANDIDATE-REPORT.md`), not executable code. No test framework is needed. The "test" is human review of the candidate report before Phase 4 selection.

---

## Security Domain

Not applicable. Phase 3 is a research documentation phase. No user input, authentication, or network services are implemented.

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| YOLOv5/v7 oil palm models (2020–2022) | YOLOv8/v9/v11 Ultralytics (2023–2025) | Better export to ONNX; same Deepness DetectorType = YOLO_Ultralytics |
| TensorFlow/Keras palm detection (h5) | PyTorch (.pt/.pth) dominant | Conversion to ONNX via torch.onnx.export; tf2onnx path available but more complex |
| Single-region models | Cross-regional domain adaptation (MADAN, MOPAD) | Better generalization across SE Asia plantation regions |
| Bounding box detection only | Instance segmentation (detectree2 Mask R-CNN) | Better crown delineation; harder to integrate with Deepness (polygon not box) |
| Papers With Code dedicated task pages | Redirects to HuggingFace | Must use arXiv + GitHub search instead |

**Deprecated/outdated:**
- HuggingFace ONNX library filter for aerial detection: useless — almost no aerial detection models are tagged with library=onnx. Use unfiltered model search.
- Zenodo ONNX model search: useless for this domain — palm models are not published as ONNX on Zenodo.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | tribber93/yolov11-palm-oil-tree training GSD is ~5–15 cm/px (typical UAV at 100–150 m AGL) | Candidate H1 | If trained on satellite imagery at coarser GSD, Perak/Rupat compatibility may flip to ✗ |
| A2 | grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm training is aerial (not ground-level) | Candidate H2 | If ground-level, it cannot detect trees in raster tiles |
| A3 | MOPAD (rs-dl) dataset was collected in SE Asia oil palm plantations | Candidate N3 | ISPRS paper title says "individual oil palm trees using UAV" but geographic region not confirmed in README; may be non-SE Asia |
| A4 | MOPAD training GSD ~5–15 cm/px (UAV-derived from large-area survey) | Candidate N3 | If altitude was much higher (e.g., fixed-wing at 500 m), GSD could be 20–30 cm/px |
| A5 | Baidu Wangpan links for MOPAD/MADAN are accessible from non-China IP addresses | Sources / Environment | Common Baidu restriction; Phase 4 download step may fail |
| A6 | MADAN model weights are available (format and hosting not confirmed from README alone) | Candidate N4 | Weights may be behind Baidu paywall or unavailable since 2020 publication |
| A7 | Google-Resnet101.onnx / Geoeye / Pleiades training GSD is ~50 cm/px | Baselines B2/B3/B4 | STATE.md says "~50 cm/px"; original model provenance from OPTIMAL-IPB project; if training GSD differs, Aceh compatibility could change |
| A8 | detectree2 performance holds at 5–8.8 cm/px GSD (our test rasters) despite being trained at ~5cm UAV data | Candidate N1 | Model may underperform at 8.8 cm/px Rupat relative to 5 cm/px Perak; Zenodo docs say performance degrades above 100 mm |

---

## Open Questions

1. **What exact GSD and geographic region did tribber93 and grediiiii use to train their HuggingFace models?**
   - What we know: Files are .pt weights; repository has README but no paper link confirmed in Phase 2
   - What's unclear: Training altitude, sensor, geographic region
   - Recommendation: Phase 4 researcher reads the README carefully; check model card for dataset description before assigning compatibility columns

2. **Is Baidu Wangpan accessible from a non-China network for MOPAD/MADAN weights?**
   - What we know: Links exist (access codes 7n61 / 8mwa for MOPAD)
   - What's unclear: Whether download succeeds from Malaysia/Indonesia/global IP
   - Recommendation: Phase 4 attempts download first; if blocked, removes MOPAD/MADAN from shortlist

3. **Does detectree2 output individual bounding boxes or only polygon masks?**
   - What we know: detectree2 is Mask R-CNN; produces instance segmentation masks
   - What's unclear: Whether bounding box output is also available (Detectron2 always produces both box + mask)
   - Recommendation: detectree2 produces both; centroid extraction from bounding box center is straightforward; same pattern as Deepness polygon → centroid in Phase 2 ensemble

4. **Can the DeepForest weecology model be exported to ONNX for use in Deepness?**
   - What we know: DeepForest uses RetinaNet (torchvision); in theory torch.onnx.export should work
   - What's unclear: Custom preprocessing (normalization, NMS) may not export cleanly; dynamic axes may be problematic
   - Recommendation: Phase 4 attempts `torch.onnx.export` on DeepForest model; if it fails, use DeepForest's standalone Python API as a parallel inference path outside Deepness

5. **Does rs-dl/MADAN publish actual pretrained weights or only code+dataset?**
   - What we know: GitHub README references dataset links on Google Drive and Baidu
   - What's unclear: Whether model weights (not just dataset) are downloadable
   - Recommendation: Phase 4 verifies by reading MADAN README completely and attempting Google Drive link

---

## Sources

### Primary (HIGH confidence)
- `.planning/phases/02-palm-ensemble/02-04-SOURCES.md` — Phase 2 source probe results (all Phase 2 sources verified)
- `zenodo.org/records/12773341/latest` — detectree2 trained models; 7 .pth files confirmed; CC-BY 4.0; Sabah Malaysia training sites confirmed [VERIFIED: WebFetch 2026-06-18]
- `deepforest.readthedocs.io/en/stable/user_guide/02_prebuilt.html` — DeepForest pretrained model list; MIT license; HuggingFace hosting confirmed [VERIFIED: WebFetch 2026-06-18]
- `doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-palm-tree-detection.htm` — ArcGIS palm model: FasterRCNN, 5–15 cm/px GSD, .dlpk, ArcGIS account required [VERIFIED: WebFetch 2026-06-18]
- `huggingface.co/weecology/deepforest-tree` — MIT license, Safetensors, loaded via DeepForest API [VERIFIED: WebFetch 2026-06-18]

### Secondary (MEDIUM confidence)
- `github.com/rs-dl/MOPAD` — pretrained weights on Baidu Wangpan confirmed from README; format .pth; access codes present [VERIFIED: WebFetch 2026-06-18 — but Baidu accessibility unverified]
- `github.com/PatBall1/detectree2` — Zenodo model link in README; Sabah training confirmed from paper; 13 releases [CITED: WebSearch + WebFetch]
- arXiv:2008.11505 (MADAN) — SE Asia cross-regional oil palm; code on rs-dl/MADAN; model availability not confirmed [CITED: arxiv.org]
- WebSearch: DeepForest training resolution "10 cm/px NEON"; NEON US sites confirmed; multiple sources agree [MEDIUM: cross-referenced biorxiv preprint + deepforest.org]

### Tertiary (LOW confidence — needs validation in Phase 4)
- tribber93/yolov11-palm-oil-tree — GSD unknown; geographic region unknown; ASSUMED aerial UAV
- grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm — GSD unknown; ASSUMED aerial
- MOPAD geographic region — confirmed UAV oil palm but exact country not stated in README excerpt
- MADAN model weights availability — GitHub page shows dataset links; weight files not confirmed

---

## Metadata

**Confidence breakdown:**
- Candidate identification: HIGH — sources verified via GitHub/Zenodo/HuggingFace direct fetch
- GSD values for known candidates: MEDIUM — inferred from papers/READMEs; not empirically measured
- GSD values for HuggingFace palm models (H1/H2): LOW — no paper or README with altitude/sensor specs
- Baidu Wangpan accessibility: LOW — unverified outside China
- Search strategy recommendations: HIGH — based on verified platform behavior (PaperswithCode redirect, Kaggle dataset-only pattern)

**Research date:** 2026-06-18
**Valid until:** 2026-09-18 (stable — new models appear monthly but the catalog shape is unlikely to change dramatically)

---

## Appendix: Source Categories Probed in Phase 3

| # | Category | Source | Palm Models Found | Status |
|---|----------|--------|-------------------|--------|
| A | Deepness zoo | chmura.put.poznan.pl | 0 new (already probed Phase 2) | SKIP |
| B | HuggingFace | huggingface.co | H1, H2, H3 (Phase 2); N2 (DeepForest) | DONE |
| C | Roboflow | universe.roboflow.com | R1, R2 (403 blocked) | BLOCKED |
| D | GitHub | github.com | N1 (detectree2), N3 (MOPAD), N4 (MADAN) | DONE |
| E | Zenodo | zenodo.org | N1 weights confirmed | DONE |
| F | Papers With Code | paperswithcode.com | BROKEN — redirects to HuggingFace | N/A |
| G | arXiv | arxiv.org | Papers found; most no public weights | DONE |
| H | IEEE Xplore | ieeexplore.ieee.org | Papers behind paywall; no public weights | PARTIAL |
| I | Kaggle | kaggle.com | Dataset-only; no pretrained weights | DONE |
| J | Google Dataset Search | datasetsearch.research.google.com | Redirects to other sources; nothing new | DONE |
| K | ArcGIS Living Atlas | hub.arcgis.com | R3 (ArcGIS account required) | BLOCKED |
