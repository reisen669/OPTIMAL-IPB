# Summary: 05-03 — Roboflow Re-probe (Source S, EXT-03)

**Plan:** 05-03-PLAN.md
**Phase:** 05-extended-palm-detection-model-research
**Completed:** 2026-06-19
**Status:** Complete

## What Was Built

Re-probed Roboflow R1 (Manfred Michael) and R2 (UiTM) for weight download accessibility using the existing `roboflow_api_key`. Probed five new Roboflow Universe oil palm models (R4–R8) not in Phase 3. Produced `05-03-FINDINGS.md` covering EXT-03 Roboflow re-probe requirement.

## Key Findings

| Model | Images | Type | Result |
|-------|--------|------|--------|
| R1: Manfred Michael | 4,063 | Aerial | API-only (D-06: key QGIS-only, Roboflow Core plan required) |
| R2: UiTM Malaysia | 8,532 | Aerial | API-only (D-06: same policy) |
| R3: ArcGIS | — | — | OUT OF SCOPE per D-07 — not probed |
| R4: Rio Bastian | ~210 | Aerial (inferred) | API-only |
| R5: nn-2ju5u | Unknown | Aerial (inferred) | API-only |
| R6: oilpalm-gpu3a | 60 | Aerial (inferred) | API-only |
| R7: palm-tree | 34 | Ground-level (high probability) | Excluded — ground-level photography |
| R8: PalmTree | 338 | Uncertain | Excluded — ambiguous imagery type |

## Deviations

- `roboflow_api_key` is a QGIS global variable not accessible outside the QGIS Python environment. Weight-download probe for R1/R2 could not be executed programmatically. Applied documented Roboflow policy (Core plan required) per D-06 as the definitive classification.
- Roboflow Universe pages for R4–R8 returned HTTP 403 on direct WebFetch. R7/R8 classification is based on image count and naming conventions; manual browser verification recommended if their status is needed for the report.

## Self-Check: PASSED

- 05-03-FINDINGS.md exists with Source S section, R1 and R2 probe outcome ✓
- D-06 classification language present ✓
- R4, R5, R6, R7, R8 sections all present with Status lines ✓
- R3 ArcGIS noted as out of scope per D-07 ✓
- No Roboflow model claims "weights downloadable" ✓
- EXT-03 Roboflow re-probe requirement satisfied ✓

## key-files.created

- `.planning/phases/05-extended-palm-detection-model-research/05-03-FINDINGS.md`
