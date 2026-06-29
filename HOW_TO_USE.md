# OPTIMAL-IPB — How to Use

**Oil Palm Trees Identification based on Machine Learning – IPB University**

Detects oil palm tree canopies on high-resolution satellite imagery using a RetinaNet/ResNet101 deep learning model. Outputs detected trees as points, bounding boxes, or circles — each with a confidence score.

---

## Requirements

- QGIS 3.x with Python 3.12
- Model file: `models/Google-Resnet101.h5` (212 MB, mAP 0.925)
- High-resolution raster input: z18–z19 satellite tiles (0.6–1.2 m/pixel), RGB, 8-bit or 16-bit

---

## Step-by-Step (GUI)

### 1. Load your satellite image as a raster layer

**Layer → Add Layer → Add Raster Layer** → browse to a PNG chip.

Recommended source: chips from the satellite tile download skill, e.g.:
```
C:\QGIS-Projects\satellite-tile-project\output_johor_phase18\png\z18_x..._y..._1024.png
```

### 2. Open the algorithm

**Processing → Toolbox** → search `OPTIMAL` → double-click **OPTIMAL-IPB**

### 3. Set parameters

| Parameter | Recommended Value | Notes |
|-----------|------------------|-------|
| Input raster layer | your loaded PNG chip | must be in the QGIS Layers panel |
| Select Models | `Google-Resnet101.h5` | highest accuracy (mAP 0.925) |
| mAP threshold | `0.5` | lower = more detections (more false positives); raise to 0.7+ for cleaner output |
| Output type | `Point` | one dot per palm; use `Bounding Box` to see detection footprint |
| Output Layer | save to `.gpkg` or temp layer | |

### 4. Click Run

Processing time: **1–5 minutes per chip** — the model uses a 500×500 px sliding window (step 470 px) across the image.

### 5. Result

A vector layer appears with one feature per detected palm tree. Each feature has a `Score` attribute (0.0–1.0 confidence).

---

## Output Types

| Type | Geometry | Use case |
|------|----------|----------|
| Point | Single point at canopy centre | Counting, density maps |
| Bounding Box | Rectangle around canopy | Canopy size analysis |
| Circle | Circle fitted to canopy diameter | Canopy area estimation |

---

## Batch Processing (Python Console)

Run on all chips in a directory. Open **Plugins → Python Console**:

```python
import os, glob
from qgis.core import QgsRasterLayer
import processing

png_dir  = r'C:\QGIS-Projects\satellite-tile-project\output_johor_phase18\png'
out_dir  = r'C:\QGIS-Projects\satellite-tile-project\output_johor_detections'
os.makedirs(out_dir, exist_ok=True)

for png_path in glob.glob(os.path.join(png_dir, '*.png')):
    name = os.path.splitext(os.path.basename(png_path))[0]
    rl = QgsRasterLayer(png_path, name)
    if not rl.isValid():
        print(f'SKIP (invalid): {name}')
        continue
    out_path = os.path.join(out_dir, f'{name}_palms.gpkg')
    result = processing.run('OPTIMAL-IPB', {
        'INPUT': rl,
        'MODEL': 0,    # Google-Resnet101.h5
        'mAP': 0.5,
        'TYPE': 0,     # 0=Point, 1=Bounding Box, 2=Circle
        'OUTPUT': out_path,
    })
    print(f'Done: {name} -> {result["OUTPUT"]}')
```

**Tip:** Run a single chip first to verify results before batching all chips.

---

## Best Practices

- **Imagery:** Clear sky, no cloud cover. Mature oil palm (visible circular canopy pattern).
- **Zoom level:** z18–z19 matches the model's training resolution.
- **mAP tuning:** Start at 0.5. If too many false positives, raise to 0.65–0.75. If missing palms, lower to 0.35–0.45.
- **Output type:** Use `Point` for counting; `Bounding Box` or `Circle` for area/density analysis.
- **Batch limit:** Process 1 chip at a time when testing; batch overnight for large areas.

---

## Model Info

| File | Backbone | mAP | Size |
|------|----------|-----|------|
| `Google-Resnet101.h5` | ResNet101 | 0.925 | 212 MB |

Additional models available at:
https://github.com/p4wlppmipb/OPTIMAL-IPB/releases

---

## Developed by

Center for Regional System, Analysis, Planning and Development (P4W/CRESTPENT), IPB University, Indonesia.
Funded by RISPRO / LPDP – Ministry of Finance, Indonesia.
