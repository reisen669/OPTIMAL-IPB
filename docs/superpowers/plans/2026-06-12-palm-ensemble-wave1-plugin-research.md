# Palm Ensemble — Wave 1: Plugin Research, Install & Test

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Find, install, and individually verify two QGIS-compatible palm detection plugins that each produce a point or polygon layer from a satellite raster, so Wave 2 can ensemble their outputs.

**Architecture:** Sequential gate — research ranks candidates, then each candidate is installed and smoke-tested on the same test raster one at a time. Wave 2 does not begin until exactly two plugins are confirmed working independently.

**Tech Stack:** QGIS 3.44, Python 3.12, conda env `qgis_gdal_env` at `C:\Users\suily\miniconda3\envs\qgis_gdal_env`, QGIS plugins folder `C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md` | Create | Records research output, install results, pass/fail for each candidate |
| `.planning/phases/02-palm-ensemble/02-01-SUMMARY.md` | Create | Final confirmation of Plugin A and Plugin B selections |

---

### Task 1: Research — Rank Top-3 QGIS Palm/Tree Detection Candidates

**Files:**
- Create: `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md`

- [ ] **Step 1: Web-search QGIS palm/tree detection plugins**

Search the following sources and collect candidates:
- QGIS Plugin Repository: https://plugins.qgis.org — search "tree detection", "palm detection", "object detection", "deep learning"
- GitHub search: `qgis plugin tree detection satellite`
- Known candidates to evaluate:
  1. **Deepness** (`deepness` on QGIS plugin repo) — deep learning inference plugin; accepts custom ONNX models, produces polygon/point output, QGIS 3.x compatible
  2. **DeepForest** (Python package `deepforest`) — tree crown detection using RetinaNet; not a QGIS plugin itself but wrappable as a Processing algorithm
  3. **SAMGeo QGIS** / **Segment Geospatial** — Segment Anything Model plugin for QGIS; detects objects in imagery including vegetation

For each candidate, capture:
- Plugin name and install method (QGIS Plugin Manager / pip / conda)
- Output type (point / polygon / raster)
- Python version compatibility (must be 3.12)
- Windows compatibility
- License
- Active maintenance (last commit / release date)

- [ ] **Step 2: Rank candidates by suitability**

Score each candidate on:
- Install complexity (1=simple pip/conda, 3=complex build)
- Output type suitability (1=point layer ready, 2=polygon needs centroid step, 3=raster only)
- Palm suitability (aerial/satellite RGB imagery support)
- Python 3.12 / QGIS 3.44 confirmed compatibility

Select top 3. Write results to `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md`:

```markdown
# Palm Detection Candidate Log

## Research date: 2026-06-12

## Ranked candidates

### C1: [Name]
- Install: `[command]`
- Output: [point/polygon/raster]
- P312 compatible: [yes/no/unknown]
- License: [license]
- Notes: [notes]

### C2: [Name]
- Install: `[command]`
- Output: [point/polygon/raster]
- P312 compatible: [yes/no/unknown]
- License: [license]
- Notes: [notes]

### C3: [Name]
- Install: `[command]`
- Output: [point/polygon/raster]
- P312 compatible: [yes/no/unknown]
- License: [license]
- Notes: [notes]

## Results
Plugin A: [TBD after testing]
Plugin B: [TBD after testing]
```

- [ ] **Step 3: Commit candidate log**

```powershell
git add .planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md
git commit -m "chore: add palm detection candidate research log"
```

---

### Task 2: Install and Test Candidate C1

**Files:**
- Modify: `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md` (append result)

This task is a **gate** — if C1 passes, it becomes Plugin A and Task 3 tests C2 for Plugin B. If C1 fails, C2 is tried for Plugin A.

#### 2a — Install

- [ ] **Step 1: Install C1 into qgis_gdal_env (if pip/conda package)**

If C1 requires a Python package (e.g. `deepforest`, `deepness` dependencies):
```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\Scripts\conda.exe" install -n qgis_gdal_env [package-name] -y
# OR
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -m pip install [package-name]
```

If C1 is a QGIS plugin installed via Plugin Manager:
1. Open QGIS 3.44
2. Plugins → Manage and Install Plugins → All
3. Search "[plugin name]"
4. Click Install

If C1 must be cloned manually:
```powershell
git clone [repo-url] "C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\[plugin-name]"
```

- [ ] **Step 2: Verify Python dependencies import cleanly**

```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -c "import [main_module]; print([main_module].__version__)"
```

Expected: version string, no ImportError.

#### 2b — QGIS Smoke Test

- [ ] **Step 3: Restart QGIS and enable C1 plugin**

1. Close and reopen QGIS 3.44
2. Plugins → Manage and Install Plugins → Installed
3. Enable C1 plugin
4. Check View → Panels → Log Messages for any Python tracebacks

Expected: Plugin appears in Processing Toolbox, no red errors in Log Messages.

- [ ] **Step 4: Run C1 on test raster**

1. Load a test raster with visible palm trees (use any .tif file from your project area)
2. Open C1's processing algorithm from the Toolbox
3. Configure inputs (raster input, any required model or threshold)
4. Run the algorithm

Expected: Output layer produced with point or polygon geometry.

- [ ] **Step 5: Inspect output**

1. Open attribute table of output layer
2. Verify geometry type is Point or Polygon (not raster)
3. Visual check: do detections overlap with visible palm crowns?
4. Note the score/confidence field name (e.g. "Score", "confidence", "prob") — needed for Wave 2

#### 2c — Record result

- [ ] **Step 6: Update candidate log**

Append to `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md`:

```markdown
## C1 Install & Test Result

- Install date: 2026-06-12
- Install command: [command used]
- Install outcome: [SUCCESS/FAIL — describe any errors]
- QGIS load: [SUCCESS/FAIL]
- Output on test raster: [SUCCESS/FAIL — describe output]
- Score field name: [field name or N/A]
- Decision: [ASSIGN as Plugin A / FAIL — try C2]
```

- [ ] **Step 7: Commit result**

```powershell
git add .planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md
git commit -m "chore: C1 install and test result"
```

---

### Task 3: Install and Test Candidate C2

**Files:**
- Modify: `.planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md`

Same procedure as Task 2 but for Candidate C2. C2 fills the next open slot (Plugin A if C1 failed, Plugin B if C1 passed).

- [ ] **Step 1: Install C2** (same procedure as Task 2, Step 1, using C2's install command)

- [ ] **Step 2: Verify Python dependencies**

```powershell
& "C:\Users\suily\miniconda3\envs\qgis_gdal_env\python.exe" -c "import [c2_main_module]; print([c2_main_module].__version__)"
```

- [ ] **Step 3: Restart QGIS and enable C2 plugin**

1. Close and reopen QGIS 3.44
2. Enable C2 plugin in Plugins Manager
3. Check Log Messages panel for errors

- [ ] **Step 4: Run C2 on the same test raster used in Task 2**

This is the same raster used in Task 2 — both detectors must run on the same image.

- [ ] **Step 5: Inspect output** (same as Task 2, Step 5)

- [ ] **Step 6: Record result and update candidate log**

```markdown
## C2 Install & Test Result

- Install date: 2026-06-12
- Install command: [command used]
- Install outcome: [SUCCESS/FAIL]
- QGIS load: [SUCCESS/FAIL]
- Output on test raster: [SUCCESS/FAIL]
- Score field name: [field name or N/A]
- Decision: [ASSIGN as Plugin A or B / FAIL — try C3]
```

- [ ] **Step 7: Commit result**

```powershell
git add .planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md
git commit -m "chore: C2 install and test result"
```

---

### Task 4: (Conditional) Install and Test Candidate C3

Only run this task if fewer than two plugins have passed after Tasks 2 and 3.

- [ ] **Step 1: Check gate condition**

If two plugins have passed (C1 and C2 both PASS, or one of them passed and C2 passed), skip to Task 5.

If fewer than two passed, run the same install/test procedure for C3 as in Tasks 2–3.

---

### Task 5: Confirm Plugin A and Plugin B, Write Wave 1 Summary

**Files:**
- Create: `.planning/phases/02-palm-ensemble/02-01-SUMMARY.md`

**Gate condition:** Exactly two plugins must have passed before writing this summary. If fewer than two pass after C1, C2, C3, stop and report — do not begin Wave 2.

- [ ] **Step 1: Confirm Plugin A and Plugin B are both passing**

Both of the following must be true:
- Plugin A: QGIS loads it, runs on test raster, produces point/polygon output
- Plugin B: QGIS loads it, runs on the same test raster, produces point/polygon output

- [ ] **Step 2: Update CANDIDATE-LOG.md with final decision**

```markdown
## Final Decision

Plugin A: [name] — score field: [field name]
Plugin B: [name] — score field: [field name]
Test raster: [path to .tif used]
```

- [ ] **Step 3: Create Wave 1 summary**

Write `.planning/phases/02-palm-ensemble/02-01-SUMMARY.md`:

```markdown
---
phase: 02-palm-ensemble
plan: 01
status: complete
completed: 2026-06-12
---

## Wave 1 Complete

Plugin A: [name and version]
Plugin B: [name and version]

Both plugins confirmed:
- Install: SUCCESS
- QGIS 3.44 load: no Python errors
- Output on test raster: point/polygon features produced
- Visual inspection: detections align with palm crowns

Score field names:
- Plugin A score field: [name]
- Plugin B score field: [name]

Ready for Wave 2 (PalmEnsembleAlgorithm implementation).
```

- [ ] **Step 4: Commit summary**

```powershell
git add .planning/phases/02-palm-ensemble/02-CANDIDATE-LOG.md .planning/phases/02-palm-ensemble/02-01-SUMMARY.md
git commit -m "feat: Wave 1 complete — Plugin A and Plugin B confirmed working"
```

---

## Wave 1 Acceptance Criteria

- [ ] Exactly two plugin candidates install without errors
- [ ] Each plugin dialog opens in QGIS 3.44 with no Python tracebacks
- [ ] Each plugin produces a point or polygon output on the same test raster
- [ ] Visual inspection confirms detections align with visible palm crowns
- [ ] `02-01-SUMMARY.md` exists and names Plugin A and Plugin B
- [ ] Both plugins confirmed working **independently** before Wave 2 begins
