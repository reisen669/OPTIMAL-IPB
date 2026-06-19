# Phase 5 Plan 03 — Findings: Roboflow Re-probe (Source S)

**Probe date:** 2026-06-19
**Plan:** 05-03-PLAN.md
**Sources:** S (Roboflow Universe — R1/R2 re-probe + R4–R8 new models)

---

## Source S: Roboflow Re-probe (R1, R2)

- Probe date: 2026-06-19
- API key accessible outside QGIS: NO — `roboflow_api_key` is stored as a QGIS global variable (QgsSettings). The value is only accessible inside the QGIS Python environment (via `qgis.utils.QgsSettings().value("roboflow_api_key")`). Programmatic probe from executor context outside QGIS is not possible without extracting the key value manually.
- R1 (Manfred Michael) probe outcome: Key not accessible outside QGIS — probe not executed. Roboflow documented policy applied (see below).
- R2 (UiTM) probe outcome: Key not accessible outside QGIS — probe not executed. Roboflow documented policy applied.
- Roboflow policy (docs.roboflow.com/deploy/download-roboflow-model-weights): Weight download from Roboflow Universe requires a paid Core/Enterprise plan. Free-tier API keys support inference via Roboflow-hosted servers only, not local weight file download. This policy was documented in Phase 3 (HTTP 403 Forbidden on download attempt) and remains consistent with Roboflow's pricing model as of 2026-06-19.
- Classification per D-06: "API inference only, weights not downloadable (free tier roboflow_api_key)"
- Note: R3 (ArcGIS Living Atlas) is out of scope per D-07 — NOT re-probed.

---

## R1: Roboflow — Manfred Michael (oil-palm-detection)

- URL: https://universe.roboflow.com/manfred-michael/oil-palm-detection
- Architecture: YOLOv5–YOLOv11 variants (multiple model versions trained on dataset; .pt weights via ultralytics)
- Images: 4,063 aerial palm images (from Phase 3 documentation)
- Weight download status: API inference only — weights not downloadable (free tier roboflow_api_key per D-06; Core plan required per Roboflow policy; probe not executable outside QGIS Python environment)
- QGIS path: API call (roboflow_algorithm.py pattern)
- Output type: bbox
- SE Asia?: Unknown (aerial imagery, geographic origin unconfirmed)
- Status: API-only (not main table; no downloadable checkpoint)

---

## R2: Roboflow — UiTM (oil-palm-aerial-detection)

- URL: https://universe.roboflow.com/uitm-14tb6/oil-palm-aerial-detection
- Architecture: YOLOv8 .pt weights (from Phase 3 documentation)
- Images: 8,532 aerial palm images (from Phase 3 documentation)
- Weight download status: API inference only — weights not downloadable (free tier roboflow_api_key per D-06; Core plan required per Roboflow policy; probe not executable outside QGIS Python environment)
- QGIS path: API call (roboflow_algorithm.py pattern)
- Output type: bbox
- SE Asia?: YES — UiTM = Universiti Teknologi MARA, Malaysia; aerial palm detection from Malaysian context
- Status: API-only (not main table; no downloadable checkpoint)

---

## R4: Roboflow — Rio Bastian (oil-palm-tree-detection-xgrav)

- URL: https://universe.roboflow.com/rio-bastian/oil-palm-tree-detection-xgrav
- Also found: https://universe.roboflow.com/rio-bastian/new-oil-palm-detection (same author, updated dataset)
- Images: ~210 (from RESEARCH.md; Roboflow page returned HTTP 403 — exact count not verified via WebFetch)
- Aerial or ground-level: AERIAL — "oil palm tree detection" framing, dataset named "oil-palm-tree-detection" typical of drone/aerial plantation surveys; consistent with other aerial Roboflow palm datasets
- Weight download status: API inference only, weights not downloadable (free tier roboflow_api_key per D-06 — same Roboflow policy applies universally to all Universe models)
- SE Asia?: Likely — Indonesia/Malaysia palm context inferred from "oil palm" naming
- Status: API-only — aerial model (not main table; no downloadable checkpoint)
- Probe notes: Direct Roboflow Universe page returned HTTP 403. Classification based on dataset naming conventions and RESEARCH.md documentation.

---

## R5: Roboflow — nn-2ju5u (oil-palm-detection-2kozl)

- URL: https://universe.roboflow.com/nn-2ju5u/oil-palm-detection-2kozl
- Also confirmed: https://universe.roboflow.com/nn-2ju5u/oil-palm-detection-2kozl/model/1 (inference API active)
- Images: Unknown (Roboflow page returned HTTP 403)
- Aerial or ground-level: AERIAL — inference API available confirming it is a trained detection model; "oil palm detection" framing consistent with aerial plantation monitoring
- Weight download status: API inference only, weights not downloadable (free tier roboflow_api_key per D-06)
- SE Asia?: Likely — oil palm context
- Status: API-only — aerial model (not main table; no downloadable checkpoint)
- Probe notes: Roboflow inference API URL accessible per WebSearch result; direct Universe page 403. API-only classification per D-06.

---

## R6: Roboflow — oilpalm-gpu3a (oil-palm-tree-zyvyi)

- URL: https://universe.roboflow.com/oilpalm-gpu3a/oil-palm-tree-zyvyi
- Dataset version: v1, created 2024-04-17
- Images: 60 (from RESEARCH.md; Roboflow page returned HTTP 403 — not re-verified via WebFetch)
- Aerial or ground-level: AERIAL — "oil palm tree" framing; small dataset (60 images) consistent with a focused aerial palm patch dataset
- Weight download status: API inference only, weights not downloadable (free tier roboflow_api_key per D-06)
- SE Asia?: Likely — oil palm context
- Status: API-only — aerial model (not main table; no downloadable checkpoint)
- Probe notes: Roboflow Universe page returned HTTP 403. Classification based on RESEARCH.md documentation and dataset naming.

---

## R7: Roboflow — palm-tree (palm-tree-detection-kxzc5)

- URL: https://universe.roboflow.com/palm-tree/palm-tree-detection-kxzc5
- Images: 34 (from RESEARCH.md)
- Aerial or ground-level: GROUND-LEVEL — very small dataset (34 images), generic "palm tree" name (not "oil palm"), workspace name "palm-tree" without agricultural/aerial context. Low image count and generic naming strongly indicate street/garden ground-level photography (decorative palms, not plantation). Could not verify via direct WebFetch (403).
- Weight download status: API inference only (even if aerial — same D-06 policy applies)
- Status: Excluded — ground-level photography (high probability); dataset too small and not oil-palm-specific for aerial plantation detection
- Probe notes: Direct Roboflow Universe page returned HTTP 403. Classification is probabilistic based on image count (34) and naming conventions — manual verification recommended if needed.

---

## R8: Roboflow — PalmTree (palm-tree-detection-7bu7u)

- URL: https://universe.roboflow.com/palmtree-3uhul/palm-tree-detection-7bu7u
- Images: 338 (from RESEARCH.md)
- Aerial or ground-level: UNCERTAIN — larger dataset (338 images) could indicate aerial but "PalmTree" / "palm-tree-detection" naming without "oil" or "aerial" qualifier is ambiguous. Direct Roboflow Universe page returned HTTP 403; cannot confirm from sample images.
- Weight download status: API inference only (D-06 applies regardless of imagery type)
- Status: Excluded — insufficient evidence of aerial palm plantation context; generic palm tree (likely mixed ornamental/street palm)
- Probe notes: Roboflow Universe page returned HTTP 403. Cannot confirm aerial vs ground-level without direct page access. Classified as Excluded due to ambiguous naming and inability to verify imagery type.
