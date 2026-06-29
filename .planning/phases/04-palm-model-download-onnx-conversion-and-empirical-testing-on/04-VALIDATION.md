---
phase: 4
slug: palm-model-download-onnx-conversion-and-empirical-testing-on
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing `setup.cfg`) |
| **Config file** | `setup.cfg` |
| **Quick run command** | `python -m pytest test/test_init.py -x` |
| **Full suite command** | `python -m pytest test/ -x` |
| **Estimated runtime** | ~5 seconds (metadata tests only) |

**Note:** Phase 4 is primarily a manual empirical testing phase. Automated tests verify
plugin metadata and environment. Per-requirement validation is via `verify_onnx_models.py`
(MOD-02) and manually-filled `04-TEST-RESULTS.md` (MOD-03/04/05).

---

## Sampling Rate

- **After every task commit:** Run `git status --short` to confirm only expected files staged
- **After Wave 0:** Run `python -m pytest test/ -x` — must be green before model testing
- **After Wave 1:** Check `verify_onnx_models.py` output — all 6 ONNX files must have [OK] or [FAIL] recorded
- **Before `/gsd-verify-work`:** `04-TEST-RESULTS.md` must exist with at least one VHR "Pass"
- **Max feedback latency:** 30 seconds (git/pytest); model inference 2-15 min per run

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-00-01 | 00 | 0 | MOD-01 | — | .gitignore excludes model binaries before any git add | smoke | `test -f .gitignore && grep -c "models/\*.onnx" .gitignore` | ✅ create new | ⬜ pending |
| 04-00-02 | 00 | 0 | MOD-02 | — | verify script covers MOPAD subdir | smoke | `grep -c "recursive=True" verify_onnx_models.py` | ✅ patch existing | ⬜ pending |
| 04-00-03 | 00 | 0 | MOD-01 | — | code files committed; no large binaries staged | smoke | `git status --short \| grep -vE "^\?\? (models\|tif_online)"` | N/A (git) | ⬜ pending |
| 04-01-01 | 01 | 1 | MOD-02 | — | all ONNX files load without error | automated | `python verify_onnx_models.py` (patched) | ✅ (after patch) | ⬜ pending |
| 04-02-01 | 02 | 2 | MOD-03 | — | VHR detections written to layer | manual | QGIS Console + `layer.featureCount()` | ❌ W0: 04-TEST-RESULTS.md | ⬜ pending |
| 04-03-01 | 03 | 3 | MOD-04 | — | MR detections written to layer | manual | QGIS Console + `layer.featureCount()` | ❌ W0: 04-TEST-RESULTS.md | ⬜ pending |
| 04-04-01 | 04 | 4 | MOD-05 | — | Roboflow API key valid; detections returned | manual+network | QGIS Console + log message count | ❌ W0: 04-TEST-RESULTS.md | ⬜ pending |
| 04-05-01 | 05 | 5 | MOD-03/04/05 | — | results table complete | smoke | `test -f .planning/phases/04-.../04-TEST-RESULTS.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.gitignore` — excludes models/*.onnx, models/**/*.onnx, models/**/*.pth, tif_online_samples/, Google-Resnet101-savedmodel/
- [ ] `verify_onnx_models.py` — patched to use `glob.glob('**/*.onnx', recursive=True)` covering MOPAD subdir
- [ ] `04-TEST-RESULTS.md` — stub table created (covers MOD-03, MOD-04, MOD-05)
