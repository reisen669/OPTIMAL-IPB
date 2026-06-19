# Summary: 05-04 — arXiv/IEEE Re-probe (N) + Counting/Density Tier (T)

**Plan:** 05-04-PLAN.md
**Phase:** 05-extended-palm-detection-model-research
**Completed:** 2026-06-19
**Status:** Complete

## What Was Built

Executed arXiv re-probe for IEEE-paywalled palm/tree detection papers (Source N, D-08) and searched the counting/density tier (Source T, EXT-02). Produced `05-04-FINDINGS.md` as handoff for Wave 2.

## Key Findings

### Source N (arXiv/IEEE re-probe)

- arXiv direct queries rate-limited (HTTP 429); WebSearch fallback used.
- No new main-table candidates found beyond E1–E3 (already in 05-01-FINDINGS.md).
- Phase 3 excluded papers re-checked: PalmProbNet (2403.03161), PalmDSNet (2410.11124), Coconut YOLOv7 (2412.11949), PRISM Ecuador (2502.13023) — all still no public checkpoints.
- Confirmed: arXiv:2502.13023 (PRISM Ecuador, IJCAI 2025) is DIFFERENT from arXiv:2509.12400 (Zippppo/PRISM). Phase 3 exclusion of 2502.13023 stands.

### Source T (counting/density tier)

| Candidate | Type | GSD | SE Asia | Weights | QGIS path | Shortlist |
|-----------|------|-----|---------|---------|-----------|-----------|
| E4: pinakinathc/oil-palm-detection | Counting | UAV | Likely | NO | not applicable | INELIGIBLE |
| E5: Google Forest Data Partnership | Density-map | 10 m/px | YES | YES (TF SavedModel) | not applicable | INELIGIBLE (D-14 crit. 1,3,4) |
| PSGCNet (2012.03597) | Crowd counting | N/A | NO | Unknown | not applicable | INELIGIBLE |

All counting-tier models tagged per D-01: "no localization — count-only/density-map; cannot produce QGIS vector layer directly."

E5 (Google Forest Data Partnership) is the most significant finding: public weights, SE Asia YES (Malaysia/Indonesia/Thailand), regularly updated (model_2025b found). However, 10 m/px resolution makes it incompatible with all test rasters and the per-tree detection workflow.

## Deviations

- arXiv search rate-limited; WebSearch used as fallback for Source N coverage.
- PSGCNet GitHub repo not confirmed via direct fetch; general crowd counting classification from RESEARCH.md documentation and arXiv abstract.

## Self-Check: PASSED

- 05-04-FINDINGS.md exists with Source N and Source T sections ✓
- Source N documents 3 queries attempted, Phase 3 papers re-checked, no new candidates ✓
- E4 has "Pretrained weights: NO" and D-01 note ✓
- E5 has "GSD: 10 m/px", "SE Asia: YES", "ONNX-exportable: NO", "Phase 6 shortlist: INELIGIBLE" ✓
- E5 has "Status: Main table" per D-13 ✓
- All counting-only models tagged per D-01 ✓
- EXT-02 counting tier requirement satisfied ✓
- EXT-03 IEEE re-probe (Source N) satisfied ✓

## key-files.created

- `.planning/phases/05-extended-palm-detection-model-research/05-04-FINDINGS.md`
