# Phase 3: Research palm counting/detection models for aerial/satellite imagery - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Catalog publicly available palm counting/detection projects that have pretrained downloadable checkpoints (any format, not ONNX-only), document their suitable GSD range (min–max cm/px), and produce a structured summary report with a recommended shortlist for Phase 4 model selection. Sources to probe expand on Phase 2's 5 categories to include Papers With Code, Kaggle, arXiv/IEEE Xplore, and Google Dataset Search.

Phase 2 (02-04-SOURCES.md) already probed Deepness zoo, HuggingFace, Roboflow, GitHub, and Zenodo and found 0 new ONNX models. Phase 3 starts from those findings and extends the search.

</domain>

<decisions>
## Implementation Decisions

### Search Scope
- **D-01:** Expand beyond Phase 2's 5 source categories. New sources: Papers With Code, Kaggle (datasets + notebooks), arXiv + IEEE Xplore (papers with linked repos), Google Dataset Search / agricultural AI datasets.
- **D-02:** Include general tree-crown / tropical canopy detection models — not only oil-palm-specific. Flag domain gap (non-palm) where applicable.
- **D-03:** SE Asia-trained models (Malaysia, Indonesia, Thailand) flagged as higher priority due to visual domain match. Global models (Africa, PNG, Colombia, Ecuador) included as secondary.

### Checkpoint Availability
- **D-04:** Publicly downloadable without login or API key. HuggingFace public repos (.pt files via git clone or direct link) are included. Roboflow pages that return 403 / require API key are excluded from the main catalog. Train-from-scratch candidates (code + dataset only, no pretrained weights) are excluded.
- **D-05:** Any checkpoint format counts: .pt, .pth, .safetensors, .onnx, .h5. ONNX-ready is not a prerequisite — Phase 4 handles conversion. Report the format found; do not document conversion commands (Phase 4 scope).

### GSD Documentation
- **D-06:** Determine GSD by reading the paper abstract, dataset section, README, capture altitude, or sensor specs. State as "inferred ~X cm/px from [source]" (e.g., "inferred ~10 cm/px from capture altitude 120 m AGL in paper"). When truly undetermined, mark as "unknown (check paper)" — do not guess.
- **D-07:** Express GSD as a min–max suitable range (e.g., "5–30 cm/px, optimal ~10 cm/px"), not just training GSD. Range should reflect what resolution the model is likely to handle based on crown size at training.
- **D-08:** Add per-model raster compatibility columns for our 3 downloaded GeoTIFFs: oam_perak_01E2b (5 cm/px), oam_rupat_indonesia (8.8 cm/px), oam_leuhan_aceh (50 cm/px). Mark ✓ (within GSD range), ✗ (out of range), or ? (range unknown) per model row.

### Report Structure
- **D-09:** Report lives in `.planning/phases/03-research-palm-counting-detection-models-for-aerial-satellite/` only. File: `03-CANDIDATE-REPORT.md` (alongside RESEARCH.md).
- **D-10:** Structured table + narrative sections. Main table columns: Name | Architecture | GSD range (cm/px) | Format | License | SE Asia? | Perak 5cm ✓/✗/? | Rupat 8.8cm ✓/✗/? | Aceh 50cm ✓/✗/?. Followed by narrative: sources probed + candidates by GSD tier.
- **D-11:** Include a "Recommended Shortlist for Phase 4" section: top 3–5 candidates with rationale, organized by GSD tier (VHR ≤15 cm, HR 15–100 cm, MR 0.5–2 m). Each entry: model name + why recommended + which of our test rasters it suits.

### Claude's Discretion
- Exact grouping/ordering within the candidate table (alphabetical, by architecture, or by GSD) — researcher's choice.
- Whether to add a "Sources Probed" appendix documenting all URLs checked (consistent with 02-04-SOURCES.md pattern).
- Confidence labeling on GSD values (HIGH / MEDIUM / LOW per 02-RESEARCH.md pattern).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 2 baseline — what's already been found
- `.planning/phases/02-palm-ensemble/02-04-SOURCES.md` — full Phase 2 source probe results (11 categories, 22+ model/TIF entries); starting point — do not re-probe sources already marked as checked here, build on them
- `.planning/phases/02-palm-ensemble/02-RESEARCH.md` — Deepness ONNX format spec, known Roboflow candidates (Manfred Michael, UiTM, Personal Utility), ONNX export workflow for YOLOv8/v9, environment availability table

### Test imagery (for compatibility columns)
- `tif_online_samples/oam_perak_01E2b_0.05mpx.tif` — 5 cm/px, Perak Malaysia, 30 MB
- `tif_online_samples/oam_rupat_indonesia_0.088mpx.tif` — 8.8 cm/px, Rupat Riau Indonesia, 5 MB
- `tif_online_samples/oam_leuhan_aceh_0.5mpx.tif` — 50 cm/px, Aceh Barat Indonesia, 0.83 MB

### Project planning
- `.planning/ROADMAP.md` — Phase 3 goal and context; Phase 4 will use the shortlist from this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `models/` — existing models already present: Google-Resnet101.onnx (~50 cm/px RetinaNet), Geoeye-Resnet101.onnx, Pleiades-Resnet101.onnx, tree_tops_yolov9.onnx (10 cm/px YOLOv9). New Phase 4 candidates would be placed here.
- `tif_online_samples/` — 3 GeoTIFFs at 3 distinct GSD tiers already downloaded; compatibility columns reference these.

### Established Patterns
- Phase 2 source reports (02-04-SOURCES.md) use a structured table per source category. The CANDIDATE-REPORT.md should follow the same style for consistency.
- GSD notation from Deepness model zoo: `resolution` metadata key in cm/px. Use same unit throughout.

### Integration Points
- Phase 4 will read `03-CANDIDATE-REPORT.md` to select models to download/convert for testing. The "Recommended Shortlist" section is the primary handoff artifact.

</code_context>

<specifics>
## Specific Ideas

- Phase 2 found 3 HuggingFace candidates already: `tribber93/yolov11-palm-oil-tree` (YOLOv11, .pt), `grediiiii/Yolov8n-GhostNet-CBAM-Oil-Palm` (YOLOv8n custom, .pt, MIT), `firdhokk/palm-tree-detection-with-rtdetr` (.safetensors — not easily convertible, likely low priority). These go directly into the catalog without re-fetching.
- tree_tops_yolov9.onnx is already present and compatible with Perak (5 cm) and Rupat (8.8 cm) rasters. It should be included in the catalog as a baseline.
- The 3 RetinaNet models (Google/Geoeye/Pleiades-Resnet101) are ~50 cm/px and compatible with the Aceh raster. Include them as the "MR tier" baseline.
- Roboflow Manfred Michael (4,063 imgs) and UiTM (8,532 imgs) are known but 403-blocked. Document as "exists, API key required" in a separate "restricted access" section — not in the main catalog.

</specifics>

<deferred>
## Deferred Ideas

- Empirical inference testing on our 3 GeoTIFFs per model — deferred to Phase 4 (too many models to test in Phase 3; shortlist first, then test).
- ONNX conversion commands per model (e.g., `ultralytics model.export(format='onnx')`) — deferred to Phase 4 plan.
- Fine-tuning or retraining any model on SE Asia data — out of scope for this project phase.

</deferred>

---

*Phase: 03-research-palm-counting-detection-models-for-aerial-satellite*
*Context gathered: 2026-06-18*
