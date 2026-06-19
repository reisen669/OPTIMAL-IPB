# Phase 5: Extended palm / tree-crown detection model research — beyond Phase 3 catalog - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-19
**Phase:** 05-extended-palm-detection-model-research
**Areas discussed:** Counting/density tier, Blocked source re-probe, New search territories, Phase 6 shortlist intent

---

## Counting/density tier

### Q1: Should density-map-only models be included in EXT-02's counting tier?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — document all counting approaches | Include heatmap/density models even if they can't produce QGIS point output; note 'no localization — count-only' | ✓ |
| Localization required | Only counting models that output individual palm detections | |
| You decide | Researcher makes the call | |

**User's choice:** Yes — document all counting approaches

---

### Q2: How should counting/density models be presented in the report?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate section, not in the main table | Different columns, separate section after main detection catalog | |
| Same table, extra column | Add 'output type' column to the Phase 3-style table | ✓ |
| Appendix only | Brief appendix, not integrated | |

**User's choice:** Same table, extra column
**Notes:** User added: "note whether it is qgis plugin or independent model/script etc" — so the table gets TWO extra columns: Output type AND QGIS path (QGIS plugin / standalone script / not applicable).

---

### Q3: Specific counting/density approaches to look for?

| Option | Description | Selected |
|--------|-------------|----------|
| General: whatever they find | Any palm/tree counting with pretrained weights (CSRNet, MCNN, P2PNet, regression heads, etc.) | ✓ |
| SE Asia UAV-specific only | Only SE Asia palm UAV counting models | |
| QGIS-compatible scripts only | Only approaches runnable inside QGIS | |

**User's choice:** General — whatever they find

---

### Q4: If 2024–2025 paper has no public checkpoint, how to handle?

| Option | Description | Selected |
|--------|-------------|----------|
| Document as 'no weights' — same as Phase 3 excluded table | Record in excluded-style list | |
| Skip entirely | Don't mention papers without weights | |
| Separate 'watch list' section | Architecture, GSD, why interesting, check for future releases | ✓ |

**User's choice:** Separate 'watch list' section

---

## Blocked source re-probe

### Q1: Roboflow R1/R2 — try existing API key to download weights?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — get a free Roboflow key and try | Free tier key acquisition | |
| No — document as still-blocked | Re-probe just confirms 403 | |
| Use existing key from QGIS var | Try the roboflow_api_key QGIS global variable | ✓ |

**User's choice:** Use existing key from QGIS var (option 3)
**Notes:** User asked "why phase 3 models visited? just to update status?" — clarified that the goal is to check if the existing key unlocks weight download, not just update status. R1/R2 become candidates if weights become accessible.

---

### Q2: ArcGIS Living Atlas R3 — create a free account?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — create a free account and check | Determine if .dlpk weights are downloadable | |
| No — ArcGIS ecosystem is out of scope | .dlpk requires ArcGIS Pro; incompatible with QGIS/onnxruntime | ✓ |
| You decide | Researcher judges based on .dlpk→ONNX feasibility | |

**User's choice:** No — ArcGIS ecosystem is out of scope

---

### Q3: IEEE Xplore re-probe strategy?

| Option | Description | Selected |
|--------|-------------|----------|
| Search arXiv for preprint versions | If preprint links to public GitHub with weights, it's a valid find | ✓ |
| Skip — Phase 3 already noted PARTIAL | No change from Phase 3 | |
| Check paper DOIs for supplemental data | Look for Zenodo/GitHub supplemental repos on IEEE papers | |

**User's choice:** Search arXiv for preprint versions

---

### Q4: If Roboflow key gives API inference only (not weight download)?

| Option | Description | Selected |
|--------|-------------|----------|
| Document as 'API inference only, weights not downloadable' | Distinct from BLOCKED | ✓ |
| Mark as still-BLOCKED | Same treatment as Phase 3 | |
| You decide | Researcher notes what they find | |

**User's choice:** Document as 'API inference only, weights not downloadable'

---

## New search territories

### Q1: Which new source categories to prioritize?

| Option | Description | Selected |
|--------|-------------|----------|
| ModelScope (Alibaba) | Chinese HuggingFace equivalent; high SE Asia relevance | ✓ |
| OpenMMLab / MMDetection zoo | Fine-tuned detection models; check for palm-specific entries | ✓ |
| TorchGeo | Geospatial PyTorch models; check for palm/tropical canopy | ✓ |
| CVPR / ICCV 2024 proceedings | Top vision conferences; palm/tree papers with public code | ✓ |

**User's choice:** All four — ModelScope, OpenMMLab/MMDetection zoo, TorchGeo, CVPR/ICCV 2024

---

### Q2: Check MDPI Remote Sensing / ISPRS journals for 2024–2025 papers?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — 2024–2025 papers with linked GitHub | Open access; high agricultural RS publication volume | ✓ |
| No — arXiv covers this | Most papers also appear on arXiv | |
| You decide | Researcher judges value | |

**User's choice:** Yes — specifically 2024–2025 papers with linked GitHub repos

---

### Q3: Scope for 2024–2025 papers?

| Option | Description | Selected |
|--------|-------------|----------|
| Oil palm specific only | Only papers naming Elaeis guineensis | |
| Oil palm + tropical tree crown | Same scope as Phase 3 | |
| Any tree crown detection (specify usage) | Broadest scope; document design target and SE Asia domain gap per candidate | ✓ |

**User's choice:** Any tree crown detection
**Notes:** User added: "but must specify usage of each case" — researcher must document what each model was designed for (species, region, sensor) and the expected SE Asia oil palm domain gap.

---

### Q4: Check ESA/Copernicus ML repos?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — include as new source category | ESA phi-lab may have satellite-native models | |
| No — Sentinel resolution is too coarse | 10–60 m/px incompatible with our 5–50 cm/px rasters | ✓ |
| You decide | Researcher judges GSD vs raster compatibility | |

**User's choice:** No — Sentinel resolution is too coarse

---

## Phase 6 shortlist intent

### Q1: What will the Phase 6 shortlist be used for?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 4 extended — test new models on OAM rasters | Same as Phase 4 but with new candidates | |
| Provider integration — register new algorithms in QGIS | Phase 6 = QGIS Processing Toolbox algorithm registration | ✓ |
| Not decided yet | Phase 6 planned later | |

**User's choice:** Provider integration (option 2)
**Notes:** User added: "do not discard models unsuitable for qgis integration. also, in qgis, test on canvas_0.5mpx layer" — non-integrable models stay in the full table; Phase 6 test raster = `sample_data_qgis/canvas_0.5mpx.tif`.

---

### Q2: Phase 6 shortlist criteria?

| Option | Description | Selected |
|--------|-------------|----------|
| ONNX-exportable | Convertible to ONNX via ultralytics or torch.onnx.export | ✓ |
| SE Asia domain match | Trained on or near Malaysia/Indonesia palm | ✓ |
| Runs in qgis_gdal_env Python 3.12 | No Detectron2, no special C++ extensions | ✓ |
| Localization output (bbox or centroid) | Produces individual palm detections, not count-only | ✓ |

**User's choice:** All four criteria required for shortlist inclusion

---

### Q3: Phase 6 shortlist size?

| Option | Description | Selected |
|--------|-------------|----------|
| Top 3 (lean) | Three best candidates | |
| Top 5 (Recommended) | Enough for VHR + MR tier + one counting model | ✓ |
| All viable candidates | No hard cap | |

**User's choice:** Top 5

---

### Q4: Should 05-EXTENDED-REPORT.md be self-contained or an addendum?

| Option | Description | Selected |
|--------|-------------|----------|
| Self-contained (repeat Phase 3 summary table) | Reader doesn't need to open Phase 3 | |
| Addendum only — reference Phase 3, don't repeat | No duplication; Phase 3 models referenced not re-documented | ✓ |
| You decide | Researcher formats the report | |

**User's choice:** Addendum only — reference Phase 3, don't repeat

---

## Claude's Discretion

- Exact column ordering in the extended candidate table
- Whether to include a "Sources Probed" appendix
- GSD confidence labeling convention (follow Phase 3 HIGH/MEDIUM/LOW pattern)
- Grouping/ordering within the main table (by GSD tier, architecture, or source)
- How many Watch List entries are "enough" before stopping paper search

## Deferred Ideas

- ONNX conversion of Phase 5 candidates — Phase 6 scope
- Empirical inference testing on rasters — Phase 6 scope (test on canvas_0.5mpx.tif)
- Fine-tuning candidates on SE Asia data — out of scope
- ArcGIS Living Atlas R3 conversion — ecosystem incompatible
