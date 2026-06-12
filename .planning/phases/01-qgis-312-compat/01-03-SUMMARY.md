---
phase: 01-qgis-312-compat
plan: "03"
subsystem: binary-artifacts
tags: [cleanup, binary-artifact, python-3.7, tech-debt]
dependency_graph:
  requires: [onnxruntime-inference-path]
  provides: [clean-utils-dir-no-cp37]
  affects: [keras_retinanet/utils/]
tech_stack:
  added: []
  patterns: [platform-tag-matching]
key_files:
  created: []
  modified:
    - keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd (deleted from disk)
decisions:
  - "Deleted compute_overlap.cp37-win_amd64.pyd from disk; file was never git-tracked so no git rm step was needed"
  - "cp37 artifact was untracked in git — only the filesystem deletion was required to satisfy PLUG-06"
metrics:
  duration: "~3 minutes"
  completed: "2026-06-12"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
---

# Phase 01 Plan 03: Delete cp37 .pyd Artifact Summary

Deleted `keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd` from the plugin directory. The stale Python 3.7 compiled extension is gone; only the Python 3.12 artifact (`compute_overlap.cp312-win_amd64.pyd`) and the pure-Python fallback (`compute_overlap.py`) remain in `keras_retinanet/utils/`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Delete cp37 .pyd artifact | filesystem-only (file was untracked in git) | compute_overlap.cp37-win_amd64.pyd (deleted) |

## Verification Output

```
cp37 artifacts: []
cp312 artifacts: ['...keras_retinanet\utils\compute_overlap.cp312-win_amd64.pyd']
PASS: cp37 deleted, cp312 present
```

## Final State of keras_retinanet/utils/ compute_overlap Files

| File | Status |
|------|--------|
| compute_overlap.cp37-win_amd64.pyd | DELETED (was 50,176 bytes) |
| compute_overlap.cp312-win_amd64.pyd | PRESENT (56,320 bytes) |
| compute_overlap.py | PRESENT (1,456 bytes) |
| compute_overlap.pyx | PRESENT (Cython source, 1,655 bytes) |
| compute_overlap.c | PRESENT (Cython-generated C, 510,211 bytes) |

## Deviations from Plan

### Deviation 1: git rm step not needed (Rule 1 — clarification)

- **Found during:** Task 1 Step 3
- **Issue:** The plan called for `git rm keras_retinanet/utils/compute_overlap.cp37-win_amd64.pyd` but the file was never tracked by git (`git ls-files keras_retinanet/` returns empty). Only `.planning/` files and `optimal_ipb_algorithm.py` are tracked.
- **Fix:** Skipped `git rm`; filesystem deletion via `Remove-Item` was sufficient. The requirement PLUG-06 is satisfied by the file's absence on disk.
- **Impact:** None — git history is clean; the file was never committed.

### Deviation 2: No new git commit for source change (informational)

- **Issue:** The plan's composite commit message was designed to bundle all Phase 1 changes, but `optimal_ipb_algorithm.py` was already committed at `f8ace04` in plan 01-02. The cp37 file deletion has no git-tracked counterpart.
- **Fix:** The SUMMARY + STATE/ROADMAP update commit (docs commit) serves as the atomic task record for plan 01-03.

## Phase 1 Complete — Git Commit History

| Commit | Message | Plan |
|--------|---------|------|
| 9ca9d53 | docs(01-01): complete onnxruntime install into qgis_gdal_env | 01-01 |
| 00af403 | chore(01-01): update STATE.md and ROADMAP.md after plan 01-01 completion | 01-01 |
| a32cefe | feat(01-02): replace keras imports with onnxruntime, update model selector to .onnx | 01-02 |
| f8ace04 | feat(01-02): rewrite detect_palm() for onnxruntime, fix indexing bug, fix parameterAsEnum | 01-02 |
| 59ef8d1 | docs(01-02): complete plan 01-02 summary, update STATE.md and ROADMAP.md | 01-02 |
| (this) | docs(01-03): delete cp37 artifact, complete Phase 1 | 01-03 |

## Known Stubs

None. All inference paths are wired to `compute_overlap.cp312-win_amd64.pyd` (via Python platform tag matching) or the pure-Python fallback.

## Threat Surface Scan

No new network endpoints or trust boundaries introduced. File deletion operation is purely local. Threat T-03-01 (accidental deletion of cp312) was mitigated: verified cp312 exists before deleting cp37.

## Self-Check: PASSED

- [x] `compute_overlap.cp37-win_amd64.pyd` does not exist on disk
- [x] `compute_overlap.cp312-win_amd64.pyd` present (56,320 bytes)
- [x] `compute_overlap.py` present (1,456 bytes)
- [x] Automated verification script printed "PASS: cp37 deleted, cp312 present"
- [x] PLUG-06 requirement satisfied
