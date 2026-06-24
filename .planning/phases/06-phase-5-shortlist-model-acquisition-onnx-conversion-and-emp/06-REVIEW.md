---
phase: 06-phase-5-shortlist-model-acquisition-onnx-conversion-and-emp
reviewed: 2026-06-24T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - models/export_e2_onnx.py
  - models/verify_e2_onnx.py
  - scripts/test_inference_e2.py
  - download_missing.py
  - models/inspect_e1_checkpoint.py
  - models/export_e1_onnx.py
  - scripts/test_inference_e1.py
findings:
  critical: 3
  warning: 6
  info: 3
  total: 12
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-06-24T00:00:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Seven files were reviewed covering E1 (CanopyRS, blocked) and E2 (VHRTrees YOLOv8m) model
acquisition, ONNX export, verification, and inference. The E1 scripts are intentionally
skeletal (documented-blocker stubs), so most substantive logic is in the E2 and shared
download path. Three critical issues were found: a hardcoded developer-specific filesystem
path in `download_missing.py`, a behavioral divergence between the inline
`map_uint16_to_uint8` fallback and the canonical `helpers.py` implementation that silently
produces wrong pixel values instead of raising an error, and a partial-download corruption
risk during satellite imagery acquisition. Six warnings cover logic gaps in the inference
pipeline, missing cleanup on GDAL export failure, and robustness gaps.

---

## Critical Issues

### CR-01: Hardcoded developer machine path in `download_missing.py`

**File:** `download_missing.py:9`
**Issue:** `os.environ['PROJ_DATA']` is set to an absolute path that only exists on the
original developer's machine (`C:\Users\suily\miniconda3\...`). Any other user running
this script will silently set a non-existent PROJ path, causing GDAL projection operations
to fail at runtime with cryptic errors rather than an informative message.

The hardcoded `OUTPUT_DIR` on line 18 has the same problem — it encodes the developer's
QGIS profile path instead of deriving it from `__file__` as every other script in this
repo does.

**Fix:**
```python
# Replace lines 9 and 18 with path-relative equivalents:
import os, sys

# Derive plugin root from this file's location instead of hardcoding
PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PLUGIN_ROOT, 'sample_data_qgis', 'mys_lat3388N_lon10299E')

# Only set PROJ_DATA if the env var is not already set (let the user's env take precedence)
# For the conda env path, document it in comments instead of hardcoding:
# os.environ.setdefault('PROJ_DATA', r'C:\...\share\proj')  # remove or make optional
```

---

### CR-02: Inline `map_uint16_to_uint8` fallback silently produces wrong output when `lower_bound >= upper_bound`

**File:** `scripts/test_inference_e2.py:66-74`, `scripts/test_inference_e1.py:131-143`
**Issue:** Both scripts define an inline fallback for `map_uint16_to_uint8` when
`helpers.py` is not importable. The fallback handles the `lower_bound >= upper_bound` edge
case by decrementing `lower_bound` by 1 and continuing:

```python
# test_inference_e2.py line 67-68
if lower_bound >= upper_bound:
    lower_bound = upper_bound - 1
```

The canonical `helpers.py` implementation (line 17-18) instead **raises a ValueError**:
```python
if lower_bound >= upper_bound:
    raise ValueError('"lower_bound" must be smaller than "upper_bound"')
```

When `lower_bound >= upper_bound` (which can happen with nearly-uniform raster tiles, all
pixels zero, etc.), the fallback silently produces a 1-element LUT where the entire
dynamic range is mapped to a single transition. Combined with the LUT indexing
`lut[img]`, any pixel value above `upper_bound` indexes into `np.ones(...)*255` (correct)
but the "ramp" is only 1 element wide, so virtually all non-zero pixels map to 255. This
causes all-white tiles being fed to the model — silently, with no error. The detection
results for those tiles will be garbage without any indication.

Crucially, the callers in both inference scripts already guard against the
`p2 >= p98` case before calling `map_uint16_to_uint8` (lines 341-348 in `test_inference_e2.py`,
lines 235-239 in `test_inference_e1.py`), so the fallback's silent coercion is only
reachable when the caller's guard fails — making the divergence a latent trap for future
refactors.

**Fix:** Match the canonical implementation — raise ValueError instead of silently
adjusting:
```python
def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
    if lower_bound is None:
        lower_bound = int(np.min(img))
    if upper_bound is None:
        upper_bound = int(np.max(img))
    if lower_bound >= upper_bound:
        raise ValueError('"lower_bound" must be smaller than "upper_bound"')
    lut = np.concatenate([
        np.zeros(lower_bound, dtype=np.uint16),
        np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
        np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
    ])
    return lut[img].astype(np.uint8)
```

---

### CR-03: Partial-download corruption in `download_missing.py` — failed Warp leaves truncated file

**File:** `download_missing.py:49-90`
**Issue:** When `gdal.Warp` throws an exception (the `except Exception` branch on line 86),
the `finally` block only removes the temporary WMS XML file. If `gdal.Warp` had already
created `out_path` before failing mid-write, the partial output file is left on disk.

On the next run of the script, the existence check on line 51:
```python
if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
```
will find the truncated file, report `[skip]`, and silently use the corrupt raster for all
downstream processing. The `getsize(out_path) > 0` guard only protects against zero-byte
files; GDAL frequently creates partially-written GeoTIFFs of non-zero size before an
error terminates the write.

**Fix:** Remove the partial file in the exception handler before continuing to the
fallback zoom:
```python
except Exception as e:
    print(f'  [X] Z={attempt_zoom} failed: {e}')
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except OSError:
            pass
finally:
    if os.path.exists(wms_file):
        os.remove(wms_file)
```

---

## Warnings

### WR-01: `verify_e2_onnx.py` crashes with unhandled exception if ONNX file is missing

**File:** `models/verify_e2_onnx.py:8`
**Issue:** `ort.InferenceSession(onnx_path, ...)` is called unconditionally. If
`VHRTrees_yolov8m.onnx` does not exist, onnxruntime raises a generic `InvalidGraph` or
`FileNotFoundError` with a long internal traceback instead of a clear message. Every
other script in this phase explicitly checks `os.path.exists` before loading. This
inconsistency means a missing model produces a confusing stack trace rather than a
diagnostic message.

**Fix:**
```python
if not os.path.exists(onnx_path):
    raise FileNotFoundError(
        f"ONNX model not found: {onnx_path}\n"
        "Run: python models/export_e2_onnx.py"
    )
```
Add before line 8.

---

### WR-02: `export_e2_onnx.py` does not verify the ONNX file after a fallback move

**File:** `models/export_e2_onnx.py:36-43`
**Issue:** If `shutil.move` on line 41 raises an exception (permission error, cross-device
move failure, disk full), execution continues to line 44 which calls `assert
os.path.exists(onnx_path)`. The assertion will fail with a confusing AssertionError
rather than the underlying OS error. `shutil.move` exceptions should be caught and
re-raised with context.

Additionally, `import shutil` is deferred to inside the `if` block (line 40). While
functional, deferred imports can be missed by static analysis tools and are inconsistent
with the file-level imports at lines 15-16.

**Fix:** Move `import shutil` to the top of the file alongside `import os`. Wrap the move
in a try/except that surfaces the OS error clearly.

---

### WR-03: `infer_e2` in `test_inference_e2.py` does not validate `conf_thres` / `iou_thres` ranges

**File:** `scripts/test_inference_e2.py:269-270`
**Issue:** `conf_thres` and `iou_thres` are accepted as floats but never validated. If a
user passes `--conf 1.5` or `--conf -0.1`, `mask = scores >= conf_thres` on line 219
would either filter everything or keep everything, silently yielding meaningless results.
The same applies to `iou_thres` in the custom NMS on line 176.

The `infer_e1` counterpart in `test_inference_e1.py` (line 190) has the identical gap.

**Fix:**
```python
if not (0.0 <= conf_thres <= 1.0):
    raise ValueError(f"conf_thres must be in [0, 1], got {conf_thres}")
if not (0.0 <= iou_thres <= 1.0):
    raise ValueError(f"iou_thres must be in [0, 1], got {iou_thres}")
```
Add at the start of `infer_e2` (and `infer_e1` when it becomes active).

---

### WR-04: Global NMS not applied across tile boundaries in `test_inference_e2.py`

**File:** `scripts/test_inference_e2.py:428-430`
**Issue:** Per-tile NMS is applied during `yolov8_postprocess`, but after all tiles are
combined via `np.vstack(all_detections)` (line 429), no cross-tile NMS is performed.
With a 30-pixel overlap between tiles (`tile_step=470`, `tile_size=500`), the same
physical tree crown detected near a tile boundary will appear in two consecutive tiles'
detection lists. These duplicate detections are stacked together in `all_detections` and
returned verbatim, inflating the reported detection count and producing duplicate bounding
boxes in any downstream consumer.

The same issue exists in `test_inference_e1.py`'s `infer_e1` (line 296), where per-tile
detections are assembled without cross-tile deduplication.

**Fix:** Apply a second global NMS pass after combining all tile detections:
```python
if len(all_detections) > 0:
    detections = np.vstack(all_detections)
    # Cross-tile NMS to suppress duplicates from overlapping tile edges
    keep = nms(detections[:, :4], detections[:, 4], iou_thres)
    detections = detections[keep]
else:
    detections = np.zeros((0, 5), dtype=np.float32)
```

---

### WR-05: `download_missing.py` uses `os.rename` across potential filesystem boundaries

**File:** `download_missing.py:79`
**Issue:** When a fallback zoom level succeeds, the file is renamed from `out_path`
(inside `OUTPUT_DIR`) to a new name also in `OUTPUT_DIR`:
```python
os.rename(out_path, os.path.join(OUTPUT_DIR, new_name))
```
Both paths are in the same directory, so this is safe on the same filesystem. However,
the pattern mirrors a common cross-device rename bug. More importantly, if `OUTPUT_DIR`
does not exist (e.g., it was deleted or the hardcoded path from CR-01 is wrong), the
`open(wms_file, 'w')` on line 59 will raise `FileNotFoundError` before the download
begins. There is no `os.makedirs(OUTPUT_DIR, exist_ok=True)` guard anywhere in the file.

**Fix:** Add at the start of the script (after defining `OUTPUT_DIR`):
```python
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

---

### WR-06: `map_uint16_to_uint8` LUT can index out of bounds when pixel values equal `2**16`

**File:** `scripts/test_inference_e2.py:69-74`, `scripts/test_inference_e1.py:138-143`
**Issue:** The inline fallback LUT is constructed as:
```python
lut = np.concatenate([
    np.zeros(lower_bound, dtype=np.uint16),
    np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
    np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
])
```
The LUT has exactly `2**16` (65536) elements (indices 0–65535). If any pixel value in
`img` equals exactly `65535` and `upper_bound < 65535`, the pixel indexes into the
`np.ones(...)` tail, which is correct. But if `upper_bound = 65535` exactly, the tail
segment `np.ones(2**16 - 65535, ...)` = `np.ones(1, ...)` still allows index 65535.

The real exposure is that `upper_bound` is derived from `int(p98)` where `p98 = float(np.percentile(...))`. For a uint16 image, `np.percentile` can return exactly `65535.0` when the 98th percentile saturates; `int(65535)` → `upper_bound = 65535` → `2**16 - upper_bound = 1`. The LUT then has indices 0–65535, which is fine — but `upper_bound` could also round to `65536` in theory if percentile returns a float slightly above 65535 due to interpolation, creating a zero-length tail and making `lut[65535]` an out-of-bounds index (though numpy fancy indexing wraps, it would return lut[-1] = 255, which is accidentally correct).

The canonical `helpers.py` has the same structural pattern, so this is an inherited issue,
but the fallback should at minimum clamp `upper_bound` to `2**16 - 1`:
```python
upper_bound = min(int(p98), 65535)
```
at the percentile calculation site (lines 340-348 in `test_inference_e2.py`).

---

## Info

### IN-01: `import cv2` deferred inside `letterbox_resize` and `infer_e2`

**File:** `scripts/test_inference_e2.py:94`, `scripts/test_inference_e2.py:300`
**Issue:** `import cv2` is performed inside function bodies rather than at module top
level. If `cv2` is not installed, the error is raised only when `letterbox_resize` is
first called rather than at import time, making the dependency invisible to tooling and
giving a confusing error mid-inference.

**Fix:** Move `import cv2` to the top of `test_inference_e2.py` alongside the other
top-level imports, wrapped in a try/except with a clear error message:
```python
try:
    import cv2
except ImportError:
    print("ERROR: opencv-python not installed. Run: pip install opencv-python")
    sys.exit(1)
```

---

### IN-02: `test_inference_e1.py` has dead import-path code that is never exercised

**File:** `scripts/test_inference_e1.py:107-324`
**Issue:** The entire inference path (lines 107–394) is dead code in the current phase.
The script exits early at line 102 (`return`) whenever the model file is absent, which it
always is since E1 is blocked. The `argparse` block (lines 312–324), `infer_e1`, and
`preprocess_tile` are fully defined but unreachable during phase 6. This is intentional
per the design, but the live inference code contains bugs (see WR-03, WR-04) that will
need fixing before E1 becomes unblocked. A comment at the top of the inference section
should flag this explicitly so future implementers know to audit it before enabling.

**Fix:** Add a comment above the `# INFERENCE PATH` block:
```python
# NOTE: The code below has NOT been exercised. Before unblocking E1,
# verify: input validation (conf/iou range), cross-tile NMS,
# and ImageNet normalization ordering are all correct.
```

---

### IN-03: Commented-out PROJ_DATA line in `download_missing.py` is misleading documentation

**File:** `download_missing.py:9`
**Issue:** The `os.environ['PROJ_DATA']` assignment is active (not commented out), yet it
is phrased in the companion comment as a workaround. Given CR-01 has been raised, this
line needs to either become a proper runtime-configurable path or be documented as
developer-local setup that must be removed before distribution.

**Fix:** Remove the line or gate it behind an environment variable check:
```python
# Allow override via environment; fall back to nothing (let GDAL find PROJ itself)
if 'PROJ_DATA' not in os.environ:
    # Set only for local dev — remove or adjust for other machines
    # os.environ['PROJ_DATA'] = r'C:\Users\suily\miniconda3\...'
    pass
```

---

_Reviewed: 2026-06-24T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
