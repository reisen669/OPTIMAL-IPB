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
- [ ] 02-04-PLAN.md — Find model checkpoints (10 cm/px–1.0 m/px) and GeoTIFF palm samples; write source report (ENS-01, ENS-02) — Wave 4

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

---
