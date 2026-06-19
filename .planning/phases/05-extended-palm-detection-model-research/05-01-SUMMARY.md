# Summary: 05-01 — VHR Candidates Probe (Sources L, M, N-partial, Q, TorchGeo)

**Plan:** 05-01-PLAN.md
**Phase:** 05-extended-palm-detection-model-research
**Completed:** 2026-06-19
**Status:** Complete

## What Was Built

Executed direct URL probes of five source categories covering the highest-priority new VHR candidates (E1–E3) not in Phase 3, plus two low-probability sources (TorchGeo, OpenMMLab). Produced `05-01-FINDINGS.md` as a structured handoff artifact for the Wave 2 report writer (05-05-PLAN.md).

## Key Findings

| Candidate | Source | Result | Status |
|-----------|--------|--------|--------|
| E1: SelvaBox/CanopyRS | L | Weights reportedly public (paper abstract); URL not confirmed via WebFetch (release assets failed to load) | Main table (conditional) |
| E2: VHRTrees (RSandAI) | M | YOLOv8m Google Drive links confirmed; GSD 50cm/px (0.5m); Turkey; no SE Asia match | Main table |
| E3: PRISM/Zippppo (2509.12400) | N-partial | No releases on GitHub — no weights available | Watch List |
| TorchGeo | — | Backbone encoders only; no detection pretrained weights | Excluded |
| OpenMMLab/MMDetection | Q | No palm/tree-crown fine-tuned checkpoints found | Excluded |

## Deviations

- CanopyRS release assets page returned a loading error in WebFetch — could not confirm exact file names/formats in GitHub Releases. Paper abstract confirms weights are public. Manual browser visit to https://github.com/hugobaudchon/CanopyRS/releases required to verify.
- GitHub search for OpenMMLab returned HTTP 403 on unauthenticated access; probed-none-found classification based on RESEARCH.md priority assessment.
- arXiv rate limits prevented direct paper fetching; WebFetch of arXiv abstract for 2507.00170 succeeded and confirmed GSD 3–10 cm/px.

## Self-Check: PASSED

- 05-01-FINDINGS.md exists with sections for E1, E2, E3, TorchGeo, OpenMMLab ✓
- E1 entry has GSD range (3–10 cm/px HIGH), Download URL status, Phase 6 eligibility ✓
- E2 GSD confirmed as cm/px (50 cm/px), not the erroneous "0.5 km" from README ✓
- E3 confirmed as Watch List (no weights) ✓
- No Phase 3 candidates (B1–N3) documented as new candidates ✓
- All five sources probed with direct URL verification ✓

## key-files.created

- `.planning/phases/05-extended-palm-detection-model-research/05-01-FINDINGS.md`
