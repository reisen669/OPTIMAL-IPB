---
status: partial
phase: 06-phase-5-shortlist-model-acquisition-onnx-conversion-and-emp
source: [06-VERIFICATION.md]
started: 2026-06-24T00:00:00.000Z
updated: 2026-06-24T00:00:00.000Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. VHRTrees fine-tuned weight download and re-export
expected: Download `models/VHRTrees_yolov8m.pt` (fine-tuned VHRTrees weights, ~20-50 MB) from https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view (requires Google login), place at `models/VHRTrees_yolov8m.pt`, re-run `python models/export_e2_onnx.py`, then re-run `python scripts/test_inference_e2.py`. The fine-tuned model should produce detection counts on canvas_0.5mpx.tif and/or oam_leuhan_aceh_0.5mpx.tif that are higher than the base COCO result (0 and 1 detections respectively).
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
