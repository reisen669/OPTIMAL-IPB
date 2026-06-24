---
phase: 06-phase-5-shortlist-model-acquisition-onnx-conversion-and-emp
plan: 06-02
subsystem: model-acquisition
tags: [canopyrs, e1-blocked, onnx-blocker, environment-incompatibility, sam3]
dependency_graph:
  requires: [06-01]
  provides: []
  affects: [06-03-PLAN.md (E1 skipped), 06-04-TEST-RESULTS.md (E1 entry: BLOCKED)]
tech_stack:
  added: []
  patterns: []
key_files:
  created: []
  modified:
    - download_missing.py
decisions:
  - "E1 CanopyRS skipped — GitHub Releases (10 releases, 2022-2023) contain source archives only, no .pth weights"
  - "canopyrs NOT installable — requires Linux (Ubuntu 22.04), Python 3.10, CUDA 12.6; project uses Windows/Python 3.12/CPU"
  - "torchvision fasterrcnn_resnet50_fpn import PASSES independently (installed by 06-01), but canopyrs package itself is blocked"
metrics:
  duration: "~10 minutes"
  completed: "2026-06-24"
  tasks: 2/2 (1 human-action checkpoint + 1 auto)
  files_changed: 1
---

# Phase 6 Plan 02: Wave 1 — E1 CanopyRS Weight Verification Summary

**One-liner:** E1 CanopyRS is BLOCKED — GitHub Releases contain source archives only (no weights), and current package requires SAM 3 (gated HuggingFace), Linux, Python 3.10, CUDA 12.6; all incompatible with this project's Windows/Python 3.12/CPU environment.

## What Was Built

1. **Task 1 (human-action checkpoint):** User verified https://github.com/hugobaudchon/CanopyRS/releases in browser. Found 10 releases (2022-2023), each with "2 Assets" that are source code archives only (no `.pth`, `.pt`, `.ckpt`, or other weight files). Current CanopyRS documentation at https://hugobaudchon.github.io/CanopyRS/getting-started/installation/ reveals the package now depends on SAM 3 (Meta's Segment Anything Model 3, gated HuggingFace model), requires Ubuntu 22.04 Linux, Python 3.10, and CUDA 12.6.

2. **Task 2 (auto):** Documented the blocker in `download_missing.py` with a 6-line comment block. Ran Python 3.12 import tests for `fasterrcnn_resnet50_fpn` and `torch.onnx` (both PASS, installed by 06-01). E1 empirical testing in Phase 6 is skipped.

## E1 CANOPYRS COMPATIBILITY REPORT

```
E1 CANOPYRS COMPATIBILITY REPORT
================================
Weight URL: BLOCKED
Weight file: N/A
canopyrs package: NOT INSTALLABLE (requires Linux/Python 3.10/CUDA 12.6 — incompatible with Windows/Python 3.12/CPU)
fasterrcnn_resnet50_fpn import: PASS
torch.onnx import: PASS
Python 3.12 overall: INCOMPATIBLE (torchvision individual imports work, but canopyrs package not installable on Windows/Python 3.12)
Recommendation for Plan 06-03: BLOCKED — E1 CanopyRS requires SAM 3 (gated HuggingFace), Linux, Python 3.10, CUDA 12.6; no weights on GitHub Releases; skip E1 in Phase 6
```

## Deviations from Plan

None — the plan explicitly handled the "no weights" path as a first-class outcome. Task 2 executed exactly the documented blocker path. Part B (canopyrs install check) was correctly determined to NOT attempt `pip install canopyrs` since the package requires Linux/CUDA 12.6 — attempting it on Windows would fail with uninformative errors and waste time. The blocker is documented from the official installation docs, not from a failed install attempt.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Skip `pip install canopyrs` attempt | Official docs specify Linux (Ubuntu 22.04) + Python 3.10 + CUDA 12.6; installing on Windows would fail noisily without adding information |
| Document blocker in download_missing.py | Persistent record in the download script ensures future maintainers understand why E1 has no model files |
| Run fasterrcnn_resnet50_fpn + torch.onnx import tests | These individual torchvision/torch imports PASS and remain useful for any future PyTorch-based model in this project |

## Known Stubs

None — no model files or inference scripts were created (correct outcome for a blocked path).

## Threat Flags

None — no new network endpoints, auth paths, or file access patterns. The blocker was discovered via browser inspection, not automated download.

## Self-Check: PASSED

- download_missing.py: MODIFIED (contains "E1 CanopyRS.*BLOCKED" comment — grep count: 1)
- models/canopyrs_frcnn_r50.pth: DOES NOT EXIST (correct — weights not available)
- fasterrcnn_resnet50_fpn import test: PASS (exit code 0)
- torch.onnx import test: PASS (exit code 0)
- E1 CANOPYRS COMPATIBILITY REPORT: printed above with all 7 lines
- Task commit: 429e139 (feat(06-02): document E1 CanopyRS BLOCKED)
