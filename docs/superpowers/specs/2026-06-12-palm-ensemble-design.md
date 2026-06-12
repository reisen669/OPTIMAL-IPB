# Palm Detection Ensemble — Phase 2 Design
**Date:** 2026-06-12
**Project:** optimal-ipb QGIS plugin
**Status:** Approved

---

## Goal

Extend the optimal-ipb plugin with a two-phase workflow:

1. **Find and verify two palm detectors** (any combination — OPTIMAL-IPB counts as one candidate among others, not a fixed anchor)
2. **Build a detector-agnostic ensemble merge algorithm** that combines any two palm centroid layers into a single confidence-scored output layer

The ensemble enables validation (cross-check two methods), replacement evaluation (compare any pair), and higher-confidence detection (keep only palms both methods agree on).

---

## Architecture

### Two waves

**Wave 1 — Research, install, individual testing**

- Research agent surveys the QGIS plugin ecosystem for palm/tree detectors compatible with QGIS 3.44 / Python 3.12 / Windows
- Ranks top-3 candidates by: install complexity, output format (must produce point or polygon layer), palm suitability, license
- OPTIMAL-IPB is included in the candidate pool — it is one option, not a fixed slot
- Selects the best two (Plugin A and Plugin B) — these may or may not include OPTIMAL-IPB
- Tests each candidate **sequentially, one at a time**, gate on success before moving to the next:

```
Research → rank [C1, C2, C3, ...]
    ↓
C1: install → test on test raster → pass? → assign as Plugin A, try next for Plugin B
                                  → fail? → try C2
    ↓
C2: install → test on test raster → pass? → assign as Plugin A or B (whichever slot is open)
                                  → fail? → try C3
    ...continue until two passing plugins found...
    ↓
If fewer than 2 passing plugins found → report, revise candidates
```

No ensemble work begins until exactly two plugins are confirmed working independently on the same test raster.

**Wave 2 — Ensemble merge algorithm**

Gated on Wave 1: only begins when Plugin A and Plugin B are both confirmed working.

Adds `PalmEnsembleAlgorithm` to the existing plugin provider — a second entry in the Processing Toolbox. The algorithm is fully detector-agnostic: it accepts any two point layers regardless of which plugin produced them.

---

## Ensemble Merge Algorithm

### Inputs

| Parameter | Type | Default |
|-----------|------|---------|
| Layer A (any palm detector output) | Vector point layer | — |
| Layer B (any palm detector output) | Vector point layer | — |
| Match distance threshold | Number (map units) | 10.0 |
| Layer A name | String | "detector_a" |
| Layer B name | String | "detector_b" |

The threshold is in map units (metres for projected CRS). At typical satellite resolutions (0.5–2 m/px) and palm crown diameter of 3–8 m, 10 m covers reasonable centroid offset between two models.

Layer name parameters populate the `source` field values so the user knows which detector each point came from, regardless of which plugins were used.

### Merge logic

1. For each point in Layer A, find the nearest point in Layer B within the threshold
2. **Match found** → emit one merged centroid (midpoint of A + B positions), `confidence=1.0`, `source="both"`
3. **Point in A, no match** → emit as-is, `confidence=0.5`, `source=<layer_a_name>`
4. **Point in B, no match** → emit as-is, `confidence=0.5`, `source=<layer_b_name>`

### Output layer fields

| Field | Type | Values |
|-------|------|--------|
| `confidence` | Double | 1.0 (both agree) / 0.5 (one method only) |
| `source` | String | `"both"` / layer A name / layer B name |
| `score_a` | Double | Score from Layer A (NULL if source = layer B name) |
| `score_b` | Double | Score from Layer B (NULL if source = layer A name) |

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
  ├─→ Plugin A (any detector)  → Point layer A  (any score field)
  └─→ Plugin B (any detector)  → Point layer B  (any score field)
                                        ↓
                            PalmEnsembleAlgorithm
                         (Layer A, Layer B, threshold,
                          layer_a_name, layer_b_name)
                                        ↓
                          Merged centroid layer
                          (confidence, source, score_a, score_b)
```

The user runs the two detectors **separately first**, then feeds both outputs into the ensemble algorithm. Each step is independently inspectable. The algorithm works for any pair: OPTIMAL-IPB vs Deepness, Deepness vs DeepForest, OPTIMAL-IPB vs SAMGeo, etc.

---

## Testing

### Wave 1 acceptance criteria

- Two plugin candidates install without errors (tested one at a time, gate on success)
- Each plugin dialog opens in QGIS 3.44 with no Python errors
- Each plugin produces a point or polygon output on the same test raster
- Visual inspection confirms detections align with visible palm crowns
- Both plugins confirmed working independently before Wave 2 begins

### Wave 2 acceptance criteria

- `PalmEnsembleAlgorithm` appears in the Processing Toolbox
- Ensemble of two identical point layers → all points at `confidence=1.0`
- Ensemble with one empty layer → all points at `confidence=0.5`
- `source` field values reflect the user-supplied layer names, not hardcoded plugin names
- Ensemble on real Plugin A + Plugin B outputs → `confidence=1.0` points cluster on visible palms
- Syntax check passes
- No crash on zero-detection input from either layer

---

## What is not in scope

- Training or fine-tuning any model
- Automated accuracy metrics (precision/recall against ground truth)
- More than two detectors in a single ensemble run
- Cloud-based detection services
- GUI changes to the OPTIMAL-IPB detection dialog itself
- Hardcoding OPTIMAL-IPB as a required participant in any ensemble

---

## Open decisions (for Wave 1 research agent)

- Which two plugins win as Plugin A and Plugin B (research agent decides)
- Exact Score field name in each plugin's output (ensemble algorithm reads it at runtime via user-configurable field selector, or auto-detects the first numeric field)
- Whether either plugin installs into `qgis_gdal_env` or needs a separate environment
