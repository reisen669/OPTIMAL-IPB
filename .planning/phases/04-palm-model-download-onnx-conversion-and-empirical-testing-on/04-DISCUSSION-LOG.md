# Phase 4: Palm model download, ONNX conversion, and empirical testing on OAM rasters - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 04-palm-model-download-onnx-conversion-and-empirical-testing-on
**Areas discussed:** Phase scope & goal, Provider integration, Empirical testing protocol, Roboflow algorithm scope

---

## Phase scope & goal

**Pre-discussion finding:** Significant untracked work already exists — tribber93_yolov11_palm.onnx converted, MOPAD model downloaded (242 MB), mopad_algorithm.py and roboflow_algorithm.py written, optimal_ipb_algorithm.py improved. ROADMAP Phase 4 goal was "[To be planned]".

### Q1: What should Phase 4 deliver?

| Option | Description | Selected |
|--------|-------------|----------|
| Commit + test existing work | Organize + commit what's built; register algorithms; run on OAM rasters; document results | ✓ |
| Add remaining shortlist candidates too | Same + download detectree2 (N1) and deepforest (N2) | |
| Testing only (skip new downloads) | No new downloads; just register + test what's in models/ | |

**User's choice:** Commit + test existing work
**Notes:** Phase 4 scope is bounded to what's already on disk. No new model downloads.

### Q2: Geoeye/Pleiades ONNX provenance

| Option | Description | Selected |
|--------|-------------|----------|
| Via keras23_env (Python 3.7 + TF 2.3) | Converted via Option 1 in MODEL_CONVERSION_STATUS.md | |
| Downloaded from upstream repo | Retrieved from original OPTIMAL-IPB GitHub | |
| Not sure / may be broken | Files present but unverified — run verify_onnx_models.py first | ✓ |

**User's choice:** Not sure / they may be broken
**Notes:** Verification must precede testing. If verify fails, exclude from test run.

### Q3: MOPAD model confidence

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — downloaded and looks valid | Include as first-class VHR candidate | ✓ |
| Downloaded but not yet verified | Verify first before committing to tests | |
| Uncertain — treat as stretch goal | Don't block on MOPAD | |

**User's choice:** Yes — downloaded and looks valid

### Q4: Requirements format

| Option | Description | Selected |
|--------|-------------|----------|
| Goal statement is enough | Planner derives tasks from goal + CONTEXT.md | |
| Light requirements (3–5 IDs) | Define MOD-01 through MOD-05 | ✓ |

**User's choice:** Light requirements (3–5 IDs)

---

## Provider integration

### Q1: Register new algorithms in provider?

| Option | Description | Selected |
|--------|-------------|----------|
| Register both in optimal_ipb_provider.py | MOPAD + Roboflow appear in Processing Toolbox | |
| Register MOPAD only | MOPAD is local ONNX; Roboflow is API-dependent | |
| Keep as standalone scripts for now | Use for testing only; defer provider integration | ✓ |

**User's choice:** Keep as standalone scripts
**Notes:** Provider integration explicitly deferred to a future phase.

### Q2: Commit optimal_ipb_algorithm.py changes?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — commit as Phase 4 task 1 | Edge clamping fix is Phase 4 deliverable | ✓ |
| Yes, but separately from Phase 4 | Standalone bugfix commit before Phase 4 | |
| You decide | Let planner slot it | |

**User's choice:** Yes — commit as Phase 4 task 1

### Q3: File locations for new scripts?

| Option | Description | Selected |
|--------|-------------|----------|
| Root of plugin directory | Same level as optimal_ipb_algorithm.py | |
| scripts/ subdirectory | Move utility scripts to scripts/ | |
| Leave as-is | Current locations with file paths for reference | ✓ |

**User's choice:** Leave as-is — include file paths for reference in CONTEXT.md
**Notes:** mopad_algorithm.py, roboflow_algorithm.py, verify_onnx_models.py, download_missing.py all stay at plugin root.

---

## Empirical testing protocol

### Q1: What output from each model run?

| Option | Description | Selected |
|--------|-------------|----------|
| Detection count + confidence distribution | Quantitative only | |
| Visual inspection in QGIS | Qualitative only | |
| Both — quantitative counts + visual check | Detection counts + QGIS visual sanity check | ✓ |

**User's choice:** Both

### Q2: Which rasters per model?

| Option | Description | Selected |
|--------|-------------|----------|
| Per-model compatible rasters | Follow Phase 3 GSD compatibility matrix | ✓ |
| All models on all rasters | Every model × every raster | |
| One raster per tier | Simpler; Perak only for VHR, Aceh only for MR | |

**User's choice:** Per-model compatible rasters

### Q3: Results location?

| Option | Description | Selected |
|--------|-------------|----------|
| 04-TEST-RESULTS.md in phase directory | Dedicated results table | ✓ |
| Inline in CONTEXT.md or VERIFICATION.md | Fold into existing artifacts | |
| You decide | Planner chooses | |

**User's choice:** 04-TEST-RESULTS.md in phase directory

### Q4: Success criterion?

| Option | Description | Selected |
|--------|-------------|----------|
| All models run + results table written | Phase done when all runs recorded | |
| At least one VHR model produces plausible palm detections | Functional success threshold | ✓ |
| You decide | Planner defines | |

**User's choice:** At least one VHR model produces plausible palm detections on Perak or Rupat

---

## Roboflow algorithm scope

### Q1: In scope for Phase 4?

| Option | Description | Selected |
|--------|-------------|----------|
| In scope — commit and test it | Commit + test on Perak/Rupat | ✓ |
| Commit but don't test (no key available) | Code only; skip empirical testing | |
| Defer to a later phase | Prototype code; don't commit yet | |

**User's choice:** In scope — commit and test it

### Q2: API key availability?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — key is available | Testing can proceed | |
| No key yet — need to get one | Get free tier key first | |
| Will use environment variable instead | Prefer env var ROBOFLOW_API_KEY | |

**User's choice:** Key already in QGIS global variable `roboflow_api_key`
**Notes:** No prerequisite step needed — key is ready.

---

## Claude's Discretion

- Wave structure and ordering of commits within Phase 4
- Exact column layout and formatting of 04-TEST-RESULTS.md
- Score threshold values used for each model (use defaults from each algorithm's code)
- Whether to use a Python script or QGIS Processing Toolbox runner for model testing
- Git-LFS vs .gitignore strategy for large ONNX files

## Deferred Ideas

- Provider integration for MOPAD + Roboflow algorithms — future phase after Phase 4 confirms results
- detectree2 (N1) — Sabah-trained Detectron2 model — requires separate inference path, deferred
- deepforest (N2) — US NEON domain gap, skip unless all VHR candidates fail
- MADAN (N4) — Google Drive/Baidu access unconfirmed
- Confidence threshold tuning — use defaults in Phase 4; calibration is future work
