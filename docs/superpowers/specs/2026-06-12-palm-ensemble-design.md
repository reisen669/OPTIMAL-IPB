# Palm Detection Ensemble — Phase 2 Design
**Date:** 2026-06-12
**Project:** optimal-ipb QGIS plugin
**Status:** Approved

---

## Goal

Extend the optimal-ipb plugin with a two-phase workflow:

1. **Find and verify a second palm detector** that runs in QGIS 3.44 on Windows / Python 3.12
2. **Build an ensemble merge algorithm** that combines OPTIMAL-IPB output with the verified alternative into a single confidence-scored centroid layer

The ensemble enables validation (cross-check OPTIMAL-IPB), potential replacement (if the alternative is clearly better), and higher-confidence detection (only keep palms both methods agree on).

---

## Architecture

### Two waves

**Wave 1 — Research, install, individual testing (this phase)**

- Research agent surveys the QGIS plugin ecosystem for palm/tree detectors compatible with QGIS 3.44 / Python 3.12 / Windows
- Ranks top-3 candidates by: install complexity, output format (must produce point or polygon layer), palm suitability, license
- Attempts candidates sequentially — gate on success before moving to the next:

```
Research → rank [B1, B2, B3]
    ↓
B1: install → test on test raster → pass? → use as Plugin B
                                  → fail? → try B2
    ↓
B2: install → test on test raster → pass? → use as Plugin B
                                  → fail? → try B3
    ↓
B3: install → test on test raster → pass? → use as Plugin B
                                  → fail? → report, revise candidates
```

Plugin A (OPTIMAL-IPB) is already verified from Phase 1 UAT and is tested on the same test raster at the start of Wave 1 to establish the baseline.

**Wave 2 — Ensemble merge algorithm**

Gated on Wave 1: only begins when both Plugin A and Plugin B are confirmed working on the same test raster.

Adds `OptimalIpbEnsembleAlgorithm` to the existing plugin provider — a second entry in the Processing Toolbox.

---

## Ensemble Merge Algorithm

### Inputs

| Parameter | Type | Default |
|-----------|------|---------|
| Layer A (OPTIMAL-IPB centroids) | Vector point layer | — |
| Layer B (alternative detector centroids) | Vector point layer | — |
| Match distance threshold | Number (map units) | 10.0 |

The threshold is in map units (metres for projected CRS). At typical satellite resolutions (0.5–2 m/px) and palm crown diameter of 3–8 m, 10 m covers reasonable centroid offset between two models.

### Merge logic

1. For each point in Layer A, find the nearest point in Layer B within the threshold
2. **Match found** → emit one merged centroid (midpoint of A + B positions), `confidence=1.0`, `source="both"`, carry `score_a` and `score_b`
3. **Point in A, no match** → emit as-is, `confidence=0.5`, `source="optimal_ipb"`, `score_b=NULL`
4. **Point in B, no match** → emit as-is, `confidence=0.5`, `source="alternative"`, `score_a=NULL`

### Output layer fields

| Field | Type | Values |
|-------|------|--------|
| `confidence` | Double | 1.0 (both agree) / 0.5 (one method only) |
| `source` | String | `"both"` / `"optimal_ipb"` / `"alternative"` |
| `score_a` | Double | Score from OPTIMAL-IPB (NULL if source=alternative) |
| `score_b` | Double | Score from alternative detector (NULL if source=optimal_ipb) |

Filtering `confidence = 1.0` gives intersection behaviour. No filtering gives union behaviour. The user controls precision/recall at query time.

### Error handling

| Condition | Behaviour |
|-----------|-----------|
| Either input layer is empty | Return the other layer wholesale at `confidence=0.5`, log warning |
| Mismatched or missing CRS | Abort with clear error message in QGIS Log Messages |
| No matches at chosen threshold | Return full union at `confidence=0.5`, suggest increasing threshold via log |

---

## Data flow

```
Test raster
  ├─→ OPTIMAL-IPB algorithm  → Point layer A  (Score field)
  └─→ Alternative detector   → Point layer B  (any score field)
                                        ↓
                          OptimalIpbEnsembleAlgorithm
                              (distance threshold)
                                        ↓
                          Merged centroid layer
                          (confidence, source, score_a, score_b)
```

The user runs the two detectors **separately first** (existing workflow), then feeds both outputs into the ensemble algorithm. Each step is independently inspectable.

---

## Testing

### Wave 1 acceptance criteria

- Plugin B candidate installs without errors into `qgis_gdal_env`
- Plugin B dialog opens in QGIS 3.44 with no Python errors
- Plugin B produces a point or polygon output on the test raster
- Visual inspection confirms detections align with visible palm crowns
- Both Plugin A and Plugin B tested on the same test raster before Wave 2 begins

### Wave 2 acceptance criteria

- `OptimalIpbEnsembleAlgorithm` appears in the Processing Toolbox
- Ensemble of two identical point layers → all points at `confidence=1.0`
- Ensemble with one empty layer → all points at `confidence=0.5`
- Ensemble on real Plugin A + Plugin B outputs → `confidence=1.0` points cluster on visible palms in QGIS
- Syntax check passes
- No crash on zero-detection input from either layer

---

## What is not in scope

- Training or fine-tuning any model
- Automated accuracy metrics (precision/recall against ground truth)
- More than two detectors in the ensemble
- Cloud-based detection services
- GUI changes to the OPTIMAL-IPB dialog itself

---

## Open decisions (for Wave 1 research agent)

- Which plugin wins as Plugin B (research agent decides)
- Exact Score field name in Plugin B output (ensemble algorithm reads it at runtime)
- Whether Plugin B installs into `qgis_gdal_env` or needs a separate environment
