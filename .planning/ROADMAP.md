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
- [ ] 01-01-PLAN.md — Install onnxruntime into qgis_gdal_env (PLUG-05)
- [ ] 01-02-PLAN.md — Replace tf_keras inference with onnxruntime, fix detect_palm() bugs, update model selector (PLUG-01, PLUG-02, PLUG-03, PLUG-04)
- [ ] 01-03-PLAN.md — Delete cp37 .pyd artifact and commit all Phase 1 changes (PLUG-06)

**Success Criteria:**
1. QGIS loads plugin with no Python errors in the message log
2. Running the algorithm on a test raster produces detection output (points/boxes)
3. No tensorflow import at plugin load time
4. models/ dropdown shows Google-Resnet101.onnx
5. detect_palm() correctly iterates image_boxes without index-out-of-bounds

**Depends on:** (none)

---
