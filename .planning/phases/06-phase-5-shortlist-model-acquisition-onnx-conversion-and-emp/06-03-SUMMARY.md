---
phase: 06-phase-5-shortlist-model-acquisition-onnx-conversion-and-emp
plan: 06-03
subsystem: model-acquisition
tags: [canopyrs, e1-blocked, onnx-skipped, inference-skipped, gate-pass-through]
dependency_graph:
  requires: [06-02]
  provides: []
  affects: [06-04-PLAN.md (E1 results: BLOCKED/SKIPPED)]
tech_stack:
  added: []
  patterns: []
key_files:
  created:
    - models/inspect_e1_checkpoint.py
    - models/export_e1_onnx.py
    - scripts/test_inference_e1.py
  modified: []
decisions:
  - "E1 ONNX export skipped — 06-02 gate confirmed BLOCKED (no weights, env incompatible)"
  - "test_inference_e1.py created as documented-skip with full inference pipeline code for future use"
metrics:
  duration: "~5 minutes"
  completed: "2026-06-24"
  tasks: 2/2
  files_changed: 3
---

# Phase 6 Plan 03: Wave 2 — E1 CanopyRS ONNX Export Attempt Summary

**One-liner:** E1 CanopyRS ONNX export and inference test both SKIPPED — 06-02 gate confirmed BLOCKED (no weights, Linux/Py3.10/CUDA 12.6 incompatible); documented-skip scripts created with full inference pipeline code for future use.

## What Was Built

**Task 06-03-01 (commit ea5ff4d):** Gate check on 06-02-SUMMARY.md returned BLOCKED. Created two scripts documenting the pass-through block:

- `models/inspect_e1_checkpoint.py`: Checkpoint structure inspector (SKIPPED path). Documents what the inspection script would do when weights become available. Prints the E1 CANOPYRS COMPATIBILITY REPORT from 06-02.
- `models/export_e1_onnx.py`: ONNX export script (SKIPPED path). Contains the full torchvision Faster R-CNN+R50 export template (ready for when weights are available). Prints the E1 ONNX EXPORT REPORT:
  ```
  E1 ONNX EXPORT REPORT
  =====================
  Option A (Faster R-CNN+R50): SKIPPED — Plan 06-02 determined E1 is BLOCKED
  Option B (DINO+Swin-L): NOT ATTEMPTED (Option A gate not cleared)
  ONNX file created: N/A
  onnxruntime verification: N/A
  Export blocker: No .pth weights available; environment incompatible
  ```

**Task 06-03-02 (commit 46fc70e):** Created `scripts/test_inference_e1.py` as a documented-skip version. The script:
- Checks for `models/canopyrs_frcnn_r50.onnx`; when absent (SKIPPED path), prints "E1 INFERENCE: SKIPPED — ONNX export was not completed" and exits 0
- Contains the full inference pipeline (preprocess_tile, infer_e1, sliding window) ready to execute when weights become available
- References both test rasters (oam_perak_01E2b_0.05mpx.tif — exists; oam_rupat_indonesia_0.088mpx.tif — exists)
- Prints DOMAIN GAP COMPARISON note (E1 MEDIUM gap vs E2 HIGH gap for SE Asia oil palm)
- Runs exit 0 without crash in SKIPPED mode

## E1 ONNX EXPORT REPORT (from running models/export_e1_onnx.py)

```
E1 ONNX EXPORT REPORT
=====================
Option A (Faster R-CNN+R50): SKIPPED — Plan 06-02 determined E1 is BLOCKED
  Reason: No pretrained weights on GitHub Releases (source archives only)
  Reason: canopyrs requires Linux/Python 3.10/CUDA 12.6 (incompatible with
          Windows/Python 3.12/CPU environment)
  Reason: Current CanopyRS depends on SAM 3 (gated HuggingFace)
Option B (DINO+Swin-L): NOT ATTEMPTED (Option A gate not cleared)
ONNX file created: N/A
onnxruntime verification: N/A
Export blocker: No .pth weights available; environment incompatible
  (See 06-02-SUMMARY.md for full E1 CANOPYRS COMPATIBILITY REPORT)
```

## Inference Test Result (SKIPPED)

```
E1 INFERENCE: SKIPPED — ONNX export was not completed
Raster oam_perak_01E2b_0.05mpx.tif: exists (not tested — no model)
Raster oam_rupat_indonesia_0.088mpx.tif: exists (not tested — no model)
Detection count: N/A
```

## Deviations from Plan

None — the plan explicitly provided a "GATE CHECK FIRST" block for both tasks: when 06-02-SUMMARY.md says BLOCKED, skip export steps and create documented-skip scripts. Both tasks followed exactly this SKIPPED path.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Follow SKIPPED path per gate check | 06-02-SUMMARY.md says "Recommendation for Plan 06-03: BLOCKED" — gate condition met |
| Include full inference pipeline in test_inference_e1.py | Script is ready to run when E1 weights become available in a future release |
| Include full export template in export_e1_onnx.py | Preserves the Faster R-CNN+R50 export pattern for future use (torchvision dynamic axes, opset 13) |

## Known Stubs

None — the scripts are correct documented-skip artifacts, not stubs. The inference pipeline code in test_inference_e1.py is complete implementation, not placeholder code.

## Threat Flags

None — no new network endpoints, auth paths, or file access patterns introduced.

## Self-Check: PASSED

- models/inspect_e1_checkpoint.py: EXISTS (created, commit ea5ff4d)
- models/export_e1_onnx.py: EXISTS (created, commit ea5ff4d)
- scripts/test_inference_e1.py: EXISTS (created, commit 46fc70e)
- E1 ONNX EXPORT REPORT header printed: PASS (verified by running export_e1_onnx.py)
- test_inference_e1.py exit 0 in SKIPPED mode: PASS (verified by running script)
- "E1 INFERENCE: SKIPPED" in script output: PASS
- "DOMAIN GAP COMPARISON" in script output: PASS
- oam_perak references in test_inference_e1.py: 4 occurrences
- oam_rupat references in test_inference_e1.py: 4 occurrences
- canopyrs_frcnn_r50.onnx references in test_inference_e1.py: 3 occurrences
- fasterrcnn_resnet50_fpn references in test_inference_e1.py: 1 occurrence
- Task 1 commit: ea5ff4d (feat(06-03): document E1 CanopyRS ONNX export SKIPPED)
- Task 2 commit: 46fc70e (feat(06-03): create test_inference_e1.py — documented skip)
