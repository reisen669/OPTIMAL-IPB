# ROADMAP — optimal-ipb

## Project
QGIS 3.44 plugin for oil palm tree detection using RetinaNet. Runs inside QGIS's Python 3.12 environment.

---

### Phase 1: QGIS 3.12 Compatibility & ONNX Inference
**Goal:** Make the plugin fully functional on QGIS 3.44 / Python 3.12 — replace the Keras/TF inference path with onnxruntime, fix known bugs, and ensure qgis_gdal_env is the single source of runtime dependencies.
**Mode:** standard

**Requirements:**
- PLUG-01: Plugin loads in QGIS 3.44 without import errors
- PLUG-02: onnxruntime replaces tf_keras for inference
- PLUG-03: detect_palm() indexing bug fixed
- PLUG-04: Model selector lists .onnx files
- PLUG-05: qgis_gdal_env has onnxruntime installed
- PLUG-06: Old cp37 .pyd artifact removed

**Plans:** 3 plans

Plans:
- [x] 01-01-PLAN.md — Install onnxruntime into qgis_gdal_env (PLUG-05) — COMPLETE (2026-06-12, onnxruntime 1.24.4)
- [x] 01-02-PLAN.md — Replace tf_keras inference with onnxruntime, fix detect_palm() bugs, update model selector (PLUG-01, PLUG-02, PLUG-03, PLUG-04) — COMPLETE (2026-06-12, commits a32cefe + f8ace04)
- [x] 01-03-PLAN.md — Delete cp37 .pyd artifact and commit all Phase 1 changes (PLUG-06) — COMPLETE (2026-06-12, filesystem deletion, no git-tracked counterpart)

**Success Criteria:**
1. QGIS loads plugin with no Python errors in the message log
2. Running the algorithm on a test raster produces detection output (points/boxes)
3. No tensorflow import at plugin load time
4. models/ dropdown shows Google-Resnet101.onnx
5. detect_palm() correctly iterates image_boxes without index-out-of-bounds

**Depends on:** (none)

---

### Phase 2: Palm Detection Ensemble
**Goal:** Find and verify two working palm detection plugins, then add a detector-agnostic `PalmEnsembleAlgorithm` to the Processing Toolbox that merges any two palm centroid layers into a confidence-scored union output.
**Mode:** standard

**Requirements:**
- ENS-01: Two QGIS-compatible palm detection plugins installed and individually verified (Plugin A and Plugin B)
- ENS-02: Both plugins produce point or polygon output on the same test raster
- ENS-03: PalmEnsembleAlgorithm registered in OPTIMAL-IPB Processing provider
- ENS-04: Ensemble output has fields: confidence (1.0/0.5), source (both/layer_name), score_a, score_b
- ENS-05: No crash on empty input from either layer; CRS mismatch raises clear error

**Plans:** 4 plans (wave-gated)

Plans:
- [ ] 02-01-PLAN.md — Research + sequential install/test of palm detection candidates (ENS-01, ENS-02) — Wave 1
- [ ] 02-02-PLAN.md — PalmEnsembleAlgorithm implementation (ENS-03, ENS-04, ENS-05) — Wave 2 (gate: 02-01-SUMMARY.md must exist)
- [ ] 02-03-PLAN.md — Deepness Plugin B: dependency fix, Tree-Tops ONNX download, QGIS run, centroid extraction (ENS-01, ENS-02) — Wave 1 (parallel with 02-01)
- [x] 02-04-PLAN.md — Find model checkpoints (10 cm/px–1.0 m/px) and GeoTIFF palm samples; write source report (ENS-01, ENS-02) — Wave 4 — COMPLETE (2026-06-16, 0 new ONNX / 3 OAM TIFs; commits 7ece01c + 78103b2)

**Success Criteria:**
1. Two confirmed plugins (Plugin A and Plugin B) each produce detections on the same test raster
2. PalmEnsembleAlgorithm appears in Processing Toolbox under OPTIMAL-IPB
3. Matched palm pairs (within threshold) output at confidence=1.0, source="both"
4. Unmatched palms output at confidence=0.5 with source=layer name
5. Empty input handled without crash; Log Messages shows warning
6. No hardcoded reference to OPTIMAL-IPB as a required ensemble participant

**Depends on:** Phase 01-qgis-312-compat

**Spec:** docs/superpowers/specs/2026-06-12-palm-ensemble-design.md
**Detail plans:** docs/superpowers/plans/2026-06-12-palm-ensemble-wave1-plugin-research.md, docs/superpowers/plans/2026-06-12-palm-ensemble-wave2-algorithm.md

### Phase 3: Research palm counting/detection models for aerial/satellite imagery — brainstorm candidate projects with pretrained checkpoints; document GSD per model

**Goal:** Catalog publicly available palm/tree-crown detection models with downloadable pretrained checkpoints, document their GSD range, and produce 03-CANDIDATE-REPORT.md with a recommended shortlist for Phase 4 model selection.
**Requirements:** CAND-01 (main catalog table), CAND-02 (restricted/Baidu section), CAND-03 (Phase 4 shortlist)
**Depends on:** Phase 2
**Plans:** 1 plan

Plans:
- [x] 03-01-PLAN.md — Write 03-CANDIDATE-REPORT.md: complete model catalog (10 candidates, 9 columns) + Recommended Shortlist for Phase 4 (CAND-01, CAND-02, CAND-03)

### Phase 4: Palm model download, ONNX conversion, and empirical testing on OAM rasters

**Goal:** Commit and verify all existing palm detection models (ONNX + Roboflow API); run empirical tests on OAM rasters (Perak 5cm, Rupat 8.8cm, Aceh 50cm); document quantitative and visual results in 04-TEST-RESULTS.md. Phase succeeds when at least one VHR model produces plausible palm detections on Perak or Rupat (D-11).
**Requirements:** MOD-01, MOD-02, MOD-03, MOD-04, MOD-05
**Depends on:** Phase 3
**Plans:** 6 plans

Plans:
- [ ] 04-01-PLAN.md — Wave 0: .gitignore, verify_onnx_models.py patch, mopad error-message fix, commit all code files (MOD-01, MOD-02)
- [ ] 04-02-PLAN.md — Wave 1: Run verify_onnx_models.py, record tensor names and pass/fail for all 6 ONNX models (MOD-02)
- [ ] 04-03-PLAN.md — Wave 2: VHR model tests — B1 tree_tops, H1 tribber93, MOPAD on Rupat and Perak (MOD-03)
- [ ] 04-04-PLAN.md — Wave 3: MR model tests — B2 Google, B3 Geoeye, B4 Pleiades on Aceh 50cm (MOD-04)
- [ ] 04-05-PLAN.md — Wave 4: Roboflow API tests on Rupat and Perak; confirm roboflow_api_key (MOD-05)
- [ ] 04-06-PLAN.md — Wave 5: Results finalization, D-11 evaluation, ROADMAP.md update, final commit (MOD-01, MOD-03, MOD-04, MOD-05)

---

### Phase 5: Extended palm / tree-crown detection model research — beyond Phase 3 catalog

**Goal:** Find palm and tree-crown detection models with publicly downloadable pretrained checkpoints NOT catalogued in Phase 3, with emphasis on satellite-native GSD models, palm counting / density-estimation approaches, recent 2024–2025 publications, and sources Phase 3 marked PARTIAL or BLOCKED. Document GSD (cm/px) range for each candidate, download status, and inference path. Produce 05-EXTENDED-REPORT.md as a structured addendum to 03-CANDIDATE-REPORT.md.
**Requirements:**
- EXT-01: All new candidates documented with architecture, GSD range (cm/px), format, license, download URL, and SE Asia applicability
- EXT-02: Palm counting / density-estimation models covered as a separate tier (distinct from detection/bounding-box models)
- EXT-03: Sources from Phase 3 marked PARTIAL/BLOCKED re-probed (IEEE Xplore, Baidu Wangpan, ArcGIS Living Atlas)
- EXT-04: 05-EXTENDED-REPORT.md produced with summary table and Phase 6 shortlist addendum
**Depends on:** Phase 3
**Plans:** 5 plans

Plans:
- [x] 05-01-PLAN.md — Wave 1: VHR candidates — SelvaBox/CanopyRS (E1), VHRTrees (E2), PRISM/Zippppo (E3), TorchGeo, OpenMMLab (EXT-01) — COMPLETE (2026-06-19)
- [x] 05-02-PLAN.md — Wave 1: ModelScope, MDPI/ISPRS 2024–2025, CVPR/ICCV 2024 (EXT-01) — COMPLETE (2026-06-19)
- [x] 05-03-PLAN.md — Wave 1: Roboflow R1/R2 re-probe + R4–R8 new models (EXT-03) — COMPLETE (2026-06-19)
- [x] 05-04-PLAN.md — Wave 1: arXiv/IEEE re-probe + palm counting/density tier (EXT-02, EXT-03) — COMPLETE (2026-06-19)
- [x] 05-05-PLAN.md — Wave 2: Write 05-EXTENDED-REPORT.md — aggregate all findings, apply Phase 6 shortlist criteria (EXT-01, EXT-02, EXT-03, EXT-04) — COMPLETE (2026-06-19)

---

### Phase 6: Phase 5 shortlist model acquisition, ONNX conversion, and empirical testing

**Goal:** Download, convert to ONNX, and empirically test the two conditional candidates from Phase 5 shortlist (E1 CanopyRS, E2 VHRTrees) on appropriate GSD rasters. Verify weight accessibility, Python 3.12 compatibility, and ONNX export paths. Document quantitative results and domain gap assessment in 06-TEST-RESULTS.md.
**Requirements:**
- VHR-01: E2 VHRTrees YOLOv8m downloaded from Google Drive and converted to ONNX
- VHR-02: E1 CanopyRS weight download URL verified (manual browser check)
- VHR-03: E1 CanopyRS Faster R-CNN+R50 preset tested for Python 3.12 compatibility
- VHR-04: E1 CanopyRS detection preset ONNX export attempted (if dependencies permit)
- VHR-05: E2 VHRTrees tested on canvas_0.5mpx.tif and Aceh 50cm raster
- VHR-06: E1 CanopyRS tested on Perak 5cm and Rupat 8.8cm rasters (if export succeeds)
- VHR-07: 06-TEST-RESULTS.md produced with domain gap assessment and precision/recall estimates
**Depends on:** Phase 5
**Plans:** 3-4 plans (estimated)

Plans:
- [ ] 06-01-PLAN.md — Wave 1: E2 VHRTrees — download YOLOv8m .pt, ONNX export, test on Canvas/Aceh (VHR-01, VHR-05)
- [ ] 06-02-PLAN.md — Wave 1: E1 CanopyRS — verify weight URL, install canopyrs, test Python 3.12 compatibility (VHR-02, VHR-03)
- [ ] 06-03-PLAN.md — Wave 2: E1 CanopyRS — ONNX export attempt, test on Perak/Rupat if successful (VHR-04, VHR-06)
- [ ] 06-04-PLAN.md — Wave 3: Results finalization — write 06-TEST-RESULTS.md, domain gap assessment, ROADMAP update (VHR-07)

**Success Criteria:**
1. E2 VHRTrees ONNX file created and runs inference on canvas_0.5mpx.tif
2. E1 CanopyRS weight accessibility confirmed or blocker documented
3. At least one shortlist candidate produces detections on its target GSD raster(s)
4. Domain gap assessment documented (Turkey generic trees vs SE Asia oil palm for E2; tropical rainforest vs plantation for E1)
5. 06-TEST-RESULTS.md includes precision/recall estimates or qualitative assessment

---
