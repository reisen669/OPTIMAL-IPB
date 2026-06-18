# Phase 3: Research palm counting/detection models - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 03-research-palm-counting-detection-models-for-aerial-satellite
**Areas discussed:** Search scope — new sources, Checkpoint availability threshold, GSD documentation strategy, Report output format & location

---

## Search Scope — New Sources

| Option | Description | Selected |
|--------|-------------|----------|
| Expand to new sources | Add Papers With Code, Kaggle, arXiv+IEEE Xplore, Google Dataset Search | ✓ |
| Deepen existing sources only | Revisit HuggingFace with broader terms, retry Roboflow with API | |
| Both — new + deepen | Broader coverage but more time | |

**User's choice:** Expand to new sources (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Papers With Code | ML papers + code + datasets index | ✓ |
| Kaggle datasets & notebooks | Aerial imagery competitions | ✓ |
| arXiv + IEEE Xplore | Academic papers with linked models | ✓ |
| Google Dataset Search / agricultural AI | CropHarvest, national portals | ✓ |

**User's choice:** All four new source categories
**Notes:** User explicitly added "can be non-onnx checkpoint, which would then be converted to onnx later" — this informed D-05 (any format counts).

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — include transferable tree models | General crown detection may generalize to palms | ✓ |
| Oil palm only | Strict scope, fewer candidates | |

**User's choice:** Yes — include transferable tree models (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| SE Asia focus preferred but global included | Flag SE Asia as higher priority | ✓ |
| Any region — no geographic filter | No priority weighting | |

**User's choice:** SE Asia focus preferred but global included (Recommended)

---

## Checkpoint Availability Threshold

| Option | Description | Selected |
|--------|-------------|----------|
| Publicly downloadable without login | Direct link or git clone, no API key | ✓ |
| Any documented checkpoint | Include API-key-gated with note | |
| Free account required is OK | Registration acceptable, paid excluded | |

**User's choice:** Publicly downloadable without login (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| No — skip train-from-scratch | No weights = excluded from catalog | ✓ |
| Yes, include as 'trainable candidates' | Separate section for code+dataset | |
| Include if dataset + code are public | Training effort estimate | |

**User's choice:** No — skip train-from-scratch (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — include conversion command per entry | Exact ultralytics/onnx command per model | |
| Note conversion framework only | Flag 'needs ultralytics export' | |
| No — just note the format | Format only; conversion is Phase 4 | ✓ |

**User's choice:** No — just note the format

---

## GSD Documentation Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Infer from paper/dataset description | Read paper for altitude, sensor, examples | ✓ |
| Mark as 'unknown' and document evidence | If not stated, mark unknown | |
| Test empirically on our 3 GeoTIFFs | Run inference per model on our imagery | |

**User's choice:** Infer from paper/dataset description (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Range: min–max cm/px suitable | e.g., "5–30 cm/px, optimal ~10 cm/px" | ✓ |
| Training GSD only | Exact training value only | |
| GSD category | VHR / HR / MR / LR buckets | |

**User's choice:** Range: min–max cm/px suitable (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — add compatibility column per model | ✓/✗/? for each of 3 GeoTIFFs | ✓ |
| Note it in the summary only | Summary section, no per-model column | |
| No — GSD range is enough | Let Phase 4 map compatibility | |

**User's choice:** Yes — add compatibility column per model (Recommended)

---

## Report Output Format & Location

| Option | Description | Selected |
|--------|-------------|----------|
| .planning/phases/03-*/ only | Standard GSD pattern, planning-only | ✓ |
| Also export to HOW_TO_USE.md | Adds 'Compatible Models' section | |
| Create a new docs/ file | Permanent reference outside planning tree | |

**User's choice:** .planning/phases/03-*/ only (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Structured table + narrative sections | Table + sources probed + top candidates by GSD tier | ✓ |
| Pure table only | Dense, scannable, no prose | |
| Narrative only with embedded tables | Prose-first with tables as support | |

**User's choice:** Structured table + narrative sections (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — top 3–5 candidates with rationale | Shortlist organized by GSD tier | ✓ |
| No — catalog only | Neutral, let Phase 4 decide | |

**User's choice:** Yes — top 3–5 candidates with rationale (Recommended)

---

## Claude's Discretion

- Exact grouping/ordering within the candidate table (alphabetical, by architecture, or by GSD)
- Whether to add a "Sources Probed" appendix (consistent with 02-04-SOURCES.md pattern)
- Confidence labeling on GSD values (HIGH / MEDIUM / LOW per 02-RESEARCH.md pattern)

## Deferred Ideas

- Empirical inference testing on GeoTIFFs per model — Phase 4 scope
- ONNX conversion commands per model — Phase 4 scope
- Fine-tuning or retraining on SE Asia data — out of scope
