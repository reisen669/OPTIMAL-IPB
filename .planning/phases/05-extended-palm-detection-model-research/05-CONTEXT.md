# Phase 5: Extended palm / tree-crown detection model research — beyond Phase 3 catalog - Context

**Gathered:** 2026-06-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Find palm and tree-crown detection models with publicly downloadable pretrained checkpoints NOT catalogued in Phase 3 (B1–B4, H1–H3, N1–N3). Search new source categories (ModelScope, OpenMMLab, TorchGeo, CVPR/ICCV 2024, MDPI Remote Sensing, ISPRS 2024–2025). Re-probe Phase 3 PARTIAL/BLOCKED sources (IEEE via arXiv preprints; Roboflow R1/R2 via existing API key; ArcGIS excluded as out of scope). Cover any tree-crown detection scope (not oil-palm-only) but document usage case and SE Asia domain gap for each candidate. Include a separate counting/density tier in the main candidate table. Document GSD range, output type, QGIS integration path, and SE Asia applicability. Produce `05-EXTENDED-REPORT.md` as an addendum to `03-CANDIDATE-REPORT.md` with a Phase 6 shortlist of top 5 candidates for QGIS provider integration.

**In scope:**
- Any tree-crown / palm detection model with a publicly downloadable pretrained checkpoint NOT in Phase 3 catalog
- Palm counting / density-estimation models (including heatmap/density-map-only approaches)
- 2024–2025 publications from arXiv, MDPI Remote Sensing, ISPRS J Photogrammetry, CVPR/ICCV — with linked public repos
- New source categories: ModelScope (Alibaba), OpenMMLab/MMDetection zoo, TorchGeo, CVPR/ICCV 2024 proceedings
- Re-probe Roboflow R1/R2 using existing `roboflow_api_key` QGIS global variable
- Re-probe IEEE Xplore via arXiv preprint search
- 2024–2025 "watch list" papers without public checkpoints (separate section)
- `05-EXTENDED-REPORT.md` with Phase 6 shortlist (top 5 candidates)

**Out of scope:**
- Phase 3 models (B1–B4, H1–H3, N1–N3) — don't re-document; reference 03-CANDIDATE-REPORT.md
- ArcGIS Living Atlas R3 — .dlpk format requires ArcGIS Pro; incompatible with QGIS/onnxruntime pipeline
- ESA/Copernicus ML repos — Sentinel 10–60 m/px resolution is too coarse for our test rasters (5–50 cm/px)
- ONNX conversion commands or inference code — Phase 6 scope
- Training or fine-tuning
- Empirical inference testing on rasters — Phase 6 scope

</domain>

<decisions>
## Implementation Decisions

### Counting / Density Tier (EXT-02)
- **D-01:** Include density-map-only models (heatmaps, Gaussian kernel, no bounding boxes / no localization) in the counting tier. Document each with note: "no localization — count-only; cannot produce QGIS vector layer directly."
- **D-02:** Counting/density models go in the SAME main candidate table as detection models. Add two extra columns to the Phase 3-style table: **Output type** (bbox / centroid / density-map / count-only) and **QGIS path** (QGIS plugin / standalone script / not applicable). Do NOT create a separate table.
- **D-03:** No architecture constraint — any palm/tree counting approach with pretrained weights is in scope (CSRNet, MCNN, P2PNet, regression heads, etc.).
- **D-04:** Papers from 2024–2025 with no public checkpoint → **Watch List** section in the report. Format: model name, architecture, GSD, why interesting, note to check for future checkpoint releases. Not in the main candidate table.

### Blocked Source Re-probe (EXT-03)
- **D-05:** Roboflow R1 (Manfred Michael) and R2 (UiTM): re-probe using the existing `roboflow_api_key` stored in QGIS global variable (same key used by `roboflow_algorithm.py`). Goal is to determine if weights are downloadable — not just updating status.
- **D-06:** If Roboflow key gives API-hosted inference only (not direct weight download): document as **"API inference only, weights not downloadable"** — distinct category from BLOCKED (which means no access at all).
- **D-07:** ArcGIS Living Atlas R3 — **out of scope**. .dlpk format requires ArcGIS Pro for inference; incompatible with this project's QGIS + onnxruntime pipeline. Document as "ecosystem incompatible" and move on.
- **D-08:** IEEE Xplore re-probe: search arXiv for preprint versions of IEEE palm/tree detection papers (2023–2025). If a preprint links to a public GitHub repo with pretrained weights, that is a valid new candidate — the IEEE paywall doesn't block the find.

### New Search Territories
- **D-09:** Priority new source categories (in addition to Phase 3's A–K sources):
  - **ModelScope (Alibaba)** — Chinese academic/industry models, high SE Asia relevance
  - **OpenMMLab / MMDetection zoo** — fine-tuned detection models, check for palm-specific entries
  - **TorchGeo** — geospatial PyTorch models; check for palm or tropical canopy fine-tunes
  - **CVPR / ICCV 2024 proceedings** — top vision conferences; search for palm/tree detection papers with public code
  - **MDPI Remote Sensing (2024–2025)** — open-access journal; high agricultural RS publication volume
  - **ISPRS J Photogrammetry (2024–2025)** — look for papers with linked GitHub repos
- **D-10:** Coverage scope = **any tree crown detection** (temperate, tropical, palm-specific, all). For each candidate, researcher MUST specify: (a) what it was designed for (species, region, sensor), (b) expected SE Asia oil palm domain gap. No filtering by species during search — filter by access/checkpoint availability only.
- **D-11:** ESA/Copernicus ML repos (phi-lab, EO science hub) are **excluded** — Sentinel-2 native resolution (10–60 m/px) is incompatible with our VHR/MR test rasters.

### Phase 6 Shortlist
- **D-12:** Phase 6 goal = **QGIS provider integration** — register new model algorithms as QGIS Processing Toolbox algorithms (analogous to planned MOPAD/Roboflow provider integration). Phase 6 test raster: `sample_data_qgis/canvas_0.5mpx.tif` (0.5 m/px).
- **D-13:** Models that are NOT suitable for QGIS integration must still be documented in the full candidate table — do not discard them. Only the Phase 6 shortlist filters by integration suitability.
- **D-14:** Phase 6 shortlist criteria (ALL FOUR required for shortlist inclusion):
  1. ONNX-exportable (convertible via ultralytics, torch.onnx.export, or equivalent)
  2. SE Asia domain match (trained on or near Malaysia/Indonesia palm data, OR general tropical with low domain gap)
  3. Runs in `qgis_gdal_env` Python 3.12 (no Detectron2, no PyTorch C++ extensions, no special native build requirements)
  4. Localization output — produces individual detections (bbox or centroid), not count-only / density-map
- **D-15:** Phase 6 shortlist size = **top 5 candidates** meeting all four criteria.
- **D-16:** `05-EXTENDED-REPORT.md` is an **addendum only** — states "Phase 3 baseline: B1–N3 (see `03-CANDIDATE-REPORT.md`)" at the top; does not re-document Phase 3 models; covers only new candidates found in Phase 5.

### Claude's Discretion
- Exact table column ordering in the extended candidate table
- Whether to include a "Sources Probed" appendix (consistent with 03-CANDIDATE-REPORT.md pattern)
- GSD confidence labeling convention (HIGH/MEDIUM/LOW — follow Phase 3 pattern)
- Grouping/ordering of candidates within the main table (by architecture, GSD tier, or source)
- How many Watch List entries are "enough" before stopping the paper search

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 3 baseline — primary exclusion list and style guide
- `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CANDIDATE-REPORT.md` — full Phase 3 catalog (B1–B4, H1–H3, N1–N3, R1–R3, excluded list, sources A–K probed). Phase 5 MUST NOT re-document these candidates. Also defines the table structure and GSD confidence label convention to follow.
- `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/03-CONTEXT.md` — Phase 3 decisions (D-01 to D-11); defines what "publicly downloadable" means and GSD documentation convention.

### Phase 4 context — integration constraints to carry forward
- `.planning/phases/04-palm-model-download-onnx-conversion-and-empirical-testing-on/04-CONTEXT.md` — key integration constraints (detectree2 Detectron2 format, DeepForest library, H2 GhostNet ONNX export risk, H3 RT-DETR size/pipeline). Phase 5 must avoid recommending candidates with the same blockers unless there's a clear workaround.

### Test rasters (for GSD compatibility columns in report)
- `tif_online_samples/oam_perak_01E2b_0.05mpx.tif` — 5 cm/px, Perak Malaysia (VHR)
- `tif_online_samples/oam_rupat_indonesia_0.088mpx.tif` — 8.8 cm/px, Rupat Riau Indonesia (VHR)
- `tif_online_samples/oam_leuhan_aceh_0.5mpx.tif` — 50 cm/px, Aceh Barat Indonesia (MR)
- `sample_data_qgis/canvas_0.5mpx.tif` — 0.5 m/px, Phase 6 target test raster

### Planning
- `.planning/ROADMAP.md` — Phase 5 requirements EXT-01 to EXT-04; Phase 6 entry (TBD — to be planned after Phase 5)

### Roboflow API key
- QGIS global variable `roboflow_api_key` — already in use by `roboflow_algorithm.py`; try for R1/R2 weight download re-probe

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `models/` — current model files (B1–B4 + MOPAD); new Phase 5 candidates would go here if downloaded
- `tif_online_samples/` — 3 GeoTIFFs at VHR/MR tiers; `sample_data_qgis/canvas_0.5mpx.tif` for Phase 6
- `roboflow_algorithm.py` — already consumes `roboflow_api_key` QGIS global var; same key is used for R1/R2 re-probe

### Established Patterns
- Phase 3 table columns: Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm | Rupat 8.8cm | Aceh 50cm
- Phase 5 extends with: Output type | QGIS path (add these two columns to the Phase 3 schema)
- GSD confidence: HIGH (from paper/README) / MEDIUM (inferred from satellite provenance) / LOW (assumed from context)
- "Sources Probed" appendix pattern from 03-CANDIDATE-REPORT.md

### Integration Points
- Phase 6 planner will read `05-EXTENDED-REPORT.md` to select candidates for QGIS provider integration
- Phase 6 shortlist criteria (D-14) are the key handoff: ONNX-exportable + SE Asia match + qgis_gdal_env-compatible + localization output

</code_context>

<specifics>
## Specific Ideas

- Roboflow R1/R2 re-probe: use `roboflow_api_key` from QGIS global var to attempt direct weight download from `universe.roboflow.com`. If weights downloadable → promote to main catalog. If API-inference-only → document as "API inference only, weights not downloadable". If still 403 → BLOCKED unchanged.
- ModelScope probe: search `modelscope.cn` for oil palm / palm tree / 棕榈 (Chinese: palm) detection models. High value given SE Asia plantation context.
- Canvas raster (0.5 m/px) added as Phase 6 test raster (`sample_data_qgis/canvas_0.5mpx.tif`). GSD compatibility column in Phase 5 report should include Perak 5cm | Rupat 8.8cm | Aceh 50cm | Canvas 0.5m for completeness.
- Watch List: record papers with promising architectures but no public checkpoint — useful for Phase 6+ planning even if not immediately actionable.

</specifics>

<deferred>
## Deferred Ideas

- **ONNX conversion of Phase 5 candidates** — Phase 6 scope. Phase 5 only documents download URLs and formats.
- **Empirical inference testing on rasters** — Phase 6 scope (test on canvas_0.5mpx.tif after download and conversion).
- **Fine-tuning any candidate on SE Asia data** — out of scope for both Phase 5 and Phase 6 as currently defined.
- **ArcGIS Living Atlas R3 conversion to ONNX** — ecosystem is incompatible; not worth pursuing without ArcGIS Pro.

</deferred>

---

*Phase: 05-extended-palm-detection-model-research*
*Context gathered: 2026-06-19*
