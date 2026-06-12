# Phase 02 — Palm Ensemble Context

## Goal

Extend the OPTIMAL-IPB plugin with a two-phase ensemble workflow:
1. Find and verify two working palm detectors (any combination — OPTIMAL-IPB is one candidate, not a fixed anchor)
2. Add `PalmEnsembleAlgorithm` that merges any two palm centroid layers into a confidence-scored output

## Spec

Full design: `docs/superpowers/specs/2026-06-12-palm-ensemble-design.md`

## Gate

Wave 2 (PalmEnsembleAlgorithm) MUST NOT begin until Wave 1 produces `02-01-SUMMARY.md` confirming exactly two passing plugins (Plugin A and Plugin B).

## Technical context

- QGIS 3.44, Python 3.12
- qgis_gdal_env at `C:\Users\suily\miniconda3\envs\qgis_gdal_env`
- QGIS plugins folder: `C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
- No new pip dependencies required for Wave 2 (pure PyQGIS)
- Provider: `optimal_ipb_provider.py` — `loadAlgorithms()` registers all algorithms

## Files (Wave 2)

| File | Action |
|------|--------|
| `palm_ensemble_algorithm.py` | Create — PalmEnsembleAlgorithm class |
| `optimal_ipb_provider.py` | Modify — register ensemble; fix inspect.getfile icon bug |
| `test/test_ensemble_algorithm.py` | Create — _get_score() unit tests |

## Depends on

Phase 01-qgis-312-compat (complete)
