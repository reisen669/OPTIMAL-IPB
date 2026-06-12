---
phase: 01-qgis-312-compat
plan: "01"
subsystem: dependency-env
tags: [conda, onnxruntime, qgis_gdal_env, inference-runtime]
dependency_graph:
  requires: []
  provides: [onnxruntime-in-qgis_gdal_env]
  affects: [optimal_ipb_algorithm.py, __init__.py]
tech_stack:
  added: [onnxruntime==1.24.4]
  patterns: [conda-install, sys.path-injection]
key_files:
  created: []
  modified: []
decisions:
  - "Installed CPU+CUDA build onnxruntime-1.24.4 via conda defaults channel (not conda-forge); this is the Microsoft-maintained build and satisfies the CPU-only runtime requirement since CUDAExecutionProvider is deferred"
  - "No plugin source files changed — onnxruntime is exposed to the plugin via the existing sys.path.insert(0, _site_pkgs) in __init__.py"
metrics:
  duration: "~5 minutes (conda solve + 193 MB download)"
  completed: "2026-06-12"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 0
---

# Phase 01 Plan 01: Install onnxruntime into qgis_gdal_env Summary

onnxruntime 1.24.4 installed into `C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages` via `conda install`, making it importable through the existing sys.path injection in `__init__.py`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Install onnxruntime via conda into qgis_gdal_env | (env-only, no source files) | conda env site-packages |

## Verification Output

```
ort version: 1.24.4
ort location: C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages\onnxruntime
```

Import verified using `sys.path.insert(0, conda_site)` pattern — identical to what `__init__.py` does at plugin load time.

## onnxruntime Version Installed

- **Package:** onnxruntime 1.24.4
- **Build variant:** `py312hf2804ad_1_cuda` (conda defaults channel)
- **Location:** `C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages\onnxruntime`
- **Additional packages installed:** coloredlogs, cuda-version, gmp, gmpy2, humanfriendly, mpc, mpfr, mpmath, packaging, protobuf, pyreadline3, python-flatbuffers, sympy (all runtime dependencies of onnxruntime)

## Solver Conflicts

None. The conda solver resolved cleanly without any conflicts or pinning required. The `onnxruntime=1.*` pin from the threat model (T-01-02) was not needed.

## How the Plugin Sees It

`__init__.py` line 37 inserts `C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages` at `sys.path[0]`. Because the conda env site-packages is at position 0, `import onnxruntime` within QGIS will always resolve to the conda env version, even though a user-level onnxruntime exists at `C:\Users\suily\AppData\Roaming\Python\Python312\site-packages\onnxruntime`.

## Deviations from Plan

None — plan executed exactly as written. onnxruntime was not previously installed in the conda env (was installed at user level only); conda install placed it correctly in qgis_gdal_env.

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Conda package integrity is verified by conda's built-in SHA verification (T-01-01 accepted disposition).

## Self-Check: PASSED

- [x] `C:\Users\suily\miniconda3\envs\qgis_gdal_env\Lib\site-packages\onnxruntime` directory exists
- [x] `import onnxruntime as ort; print('ort version:', ort.__version__)` prints `ort version: 1.24.4` with no error
- [x] PLUG-05 satisfied: qgis_gdal_env has onnxruntime installed
