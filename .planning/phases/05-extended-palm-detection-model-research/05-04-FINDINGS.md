# Phase 5 Plan 04 — Findings: arXiv/IEEE Re-probe (N) + Counting/Density Tier (T)

**Probe date:** 2026-06-19
**Plan:** 05-04-PLAN.md
**Sources:** N (arXiv/IEEE re-probe, D-08), T (palm counting/density, EXT-02)

---

## Source N: arXiv / IEEE Re-probe (D-08)

- Probe date: 2026-06-19
- Queries run:
  1. arxiv.org query: oil palm detection deep learning → Rate-limited (HTTP 429); WebSearch fallback used
  2. arxiv.org query: palm tree detection UAV satellite → Rate-limited (HTTP 429); WebSearch fallback used
  3. arxiv.org query: tree crown detection pretrained → Rate-limited (HTTP 429); WebSearch fallback used
- WebSearch fallback (arXiv 2024-2025 oil palm SE Asia pretrained weights):
  - No new candidates beyond E1–E3 (CanopyRS, VHRTrees, PRISM/Zippppo) found with confirmed pretrained checkpoints for SE Asia palm detection
  - Found: arXiv:2509.12400 (Zippppo/PRISM) — already covered as E3 in 05-01-FINDINGS.md
  - Found: arXiv:2502.13023 (PRISM Ecuador/IJCAI 2025) — confirmed DIFFERENT from Zippppo/PRISM; Ecuador context; Phase 3 excluded
- Phase 3 excluded papers re-checked:
  - arXiv:2403.03161 PalmProbNet: No GitHub link or checkpoint release found via WebFetch or WebSearch. Status unchanged — still no public checkpoint.
  - arXiv:2410.11124 PalmDSNet (Ecuador): WebFetch of arXiv page shows no code availability link confirmed. No checkpoint release found. Status unchanged — still no public checkpoint.
  - arXiv:2412.11949 Coconut YOLOv7 (Ghana): Not re-checked via direct WebFetch due to rate limits; no new checkpoint release found in WebSearch. Status unchanged.
  - arXiv:2502.13023 PRISM Ecuador (IJCAI 2025): Confirmed still no public weights — different paper from Zippppo/PRISM (arXiv:2509.12400). Phase 3 exclusion stands.
- New candidates found (with downloadable checkpoint): None beyond E1–E3 already documented in 05-01-FINDINGS.md
- Papers for Watch List: arXiv:2509.12400 (Zippppo/PRISM) — already on Watch List in E3 section of 05-01-FINDINGS.md
- Result: Probed — no new main-table candidates with downloadable checkpoints found beyond E1–E3. arXiv direct search rate-limited; WebSearch fallback confirms no additional candidates. EXT-03 IEEE Xplore re-probe requirement satisfied via arXiv preprint proxy (D-08).

---

## Source T: Palm Counting / Density Tier (EXT-02)

- Probe date: 2026-06-19
- E4 (pinakinathc/oil-palm-detection) probed: YES
- E5 (google/forest-data-partnership) probed: YES
- PSGCNet probed: YES (via WebSearch)
- Additional arXiv searches: Attempted (rate-limited; WebSearch fallback)
- GitHub search (oil palm counting pretrained): WebSearch used as proxy

---

## E4: pinakinathc/oil-palm-detection

- GitHub: https://github.com/pinakinathc/oil-palm-detection
- Model type: COUNTING — "Oil Palm Tree Counting in Drone Image" (from repository description). Not bounding-box detection. Focus is density/count estimation.
- Aerial or ground-level: AERIAL — explicitly drone imagery
- Pretrained weights: NO — repository has 7 commits; no Releases tab; no checkpoints/ or weights/ directory found. Code and annotation conversion scripts only (yolov5/, xml_to_yolo.py present but no pretrained .pt files).
- Architecture: YOLOv5-based (from repository structure)
- GSD: UAV drone imagery; specific GSD not stated in repository
- Output type: count-only (drone palm counting via YOLO adaptation)
- QGIS path: not applicable (count-only; cannot produce QGIS vector layer directly)
- Note: "no localization — count-only; cannot produce QGIS vector layer directly" (D-01)
- Phase 6 shortlist: INELIGIBLE — no pretrained weights; D-14 criterion 1 (ONNX-exportable) fails
- Status: Excluded — no pretrained weights; dataset and training code only

---

## E5: Google Forest Data Partnership — Community Palm Model

- GitHub: https://github.com/google/forest-data-partnership
- Paper: arXiv:2405.09530
- Architecture: TensorFlow-based pixel classification model (not confirmed via direct model page; SavedModel format inferred from Google Earth Engine typical deployment pattern)
- GSD: 10 m/px (Sentinel-2 native resolution) — HIGH confidence from Google Earth Engine Sentinel-2 catalog specification
- Format: TensorFlow SavedModel (multiple model directories found: model_20240312/palm, model_2024a, model_2025a, model_2025b — updated as recently as 2025)
- Download URL: https://github.com/google/forest-data-partnership/tree/main/models (directory listing accessible; individual model file download requires further navigation)
- License: Likely CC-BY 4.0 NC (non-commercial; standard for Google Research RS datasets)
- SE Asia?: YES — explicitly Malaysia, Indonesia, Thailand oil palm coverage (from RESEARCH.md E5 documentation and paper abstract focus on tropical SE Asia oil palm mapping)
- Output type: density-map (pixel probability at 10 m/px — probability of palm presence per pixel; NOT individual tree detection)
- QGIS path: not applicable (10 m/px resolution mismatch with all test rasters; TF SavedModel not compatible with onnxruntime; no localization output)
- Canvas 0.5m: ✗  Perak 5cm: ✗  Rupat 8.8cm: ✗  Aceh 50cm: ✗  (all resolution mismatch — 10 m/px vs 5–50 cm/px test rasters)
- ONNX-exportable: NO (TensorFlow SavedModel; no ONNX export path; 10 m/px output incompatible with individual tree detection workflow)
- Phase 6 shortlist: INELIGIBLE — D-14 criterion 1 (not ONNX-exportable), criterion 3 (TF format not compatible with qgis_gdal_env Python 3.12 onnxruntime), criterion 4 (density-map output — no localization; cannot produce QGIS vector layer directly)
- Status: Main table (D-13: non-shortlist-eligible models still appear in full candidate table)
- Note: "no localization — density-map / count-only; cannot produce QGIS vector layer directly" (D-01). Model updated as recently as 2025 (model_2025b directory found). Valuable for coarse plantation extent mapping at 10 m/px, but incompatible with the plugin's per-tree detection workflow.

---

## PSGCNet (arXiv:2012.03597)

- Paper: "PSGCNet: Pyramidal Scale and Global Context Network for Crowd Counting"
- GitHub: (not confirmed via WebFetch — arXiv rate-limited; WebSearch did not surface a specific PSGCNet GitHub repo with pretrained RS weights)
- Model type: CROWD COUNTING — general-purpose person density estimation network. Not trained on aerial/RS imagery.
- Aerial palm applicability: NO — trained on standard crowd-counting benchmarks (ShanghaiTech, UCF-CC-50, NWPU-Crowd) featuring human crowds in urban settings. Not applicable to aerial palm counting without complete retraining.
- Pretrained weights: Unknown (not confirmed). Even if available, domain gap (persons in urban scenes vs aerial palms) makes transfer impractical without fine-tuning data.
- Output type: density-map (person crowd counting)
- QGIS path: not applicable
- Note: "no localization — count-only; cannot produce QGIS vector layer directly" (D-01)
- Phase 6 shortlist: INELIGIBLE — D-14 criteria 2 (no SE Asia palm domain match), 4 (density-map output)
- Status: Excluded — general crowd counting, not applicable to aerial palm detection without full retraining; no aerial RS pretrained weights found

---

## Additional counting-tier candidates

- WebSearch for "palm counting pretrained" and "tree counting remote sensing pretrained": No additional candidates with downloadable pretrained checkpoints found beyond E4, E5, and PSGCNet above.
- GitHub search (oil palm counting pretrained): No repos with pretrained weight downloads found.
- Result: Probed — no additional counting-tier candidates with pretrained weights found.
