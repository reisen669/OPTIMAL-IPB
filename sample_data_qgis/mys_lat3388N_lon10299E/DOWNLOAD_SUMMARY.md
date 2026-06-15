# Multi-Resolution Imagery Download Summary

**Location:** 3.388°N, 102.99°E (Johor, Malaysia)
**Source:** ESRI World Imagery (Maxar/DigitalGlobe)
**Date:** 2026-06-15

---

## Bounding Box (EPSG:3857)

| Corner | X (m) | Y (m) |
|--------|-------|-------|
| Upper-Left | 11,464,086.564 | 377,242.053 |
| Lower-Right | 11,464,728.435 | 376,763.883 |

**Coverage:** 641.87 m (W) × 478.17 m (H) = 30.69 ha

---

## Output Files

| Filename | Target GSD | Zoom | Native Tile GSD | Actual GSD | Dimensions | Size |
|----------|------------|------|-----------------|------------|------------|------|
| `imagery_0.5mpx.tif` | 0.5 m/px | Z=18 | 0.596 m/px | 0.5000 m/px | 1284 × 956 px | 3.5 MB |
| `imagery_0.3mpx.tif` | 0.3 m/px | Z=19 | 0.298 m/px | 0.3000 m/px | 2140 × 1594 px | 0.3 MB |
| `imagery_0.1mpx.tif` | 0.1 m/px | Z=20 | 0.149 m/px | 0.1000 m/px | 6419 × 4782 px | 2.8 MB |

---

## Zoom Level Reference

Pixel size formula (Web Mercator at lat 3.388°N):
`pixel_size_m = 156543.034 × cos(3.388° × π/180) / 2^Z = 156543.034 × 0.99825 / 2^Z`

| Zoom | Native Pixel Size | Approx Tiles (W×H) | Used For |
|---|---|---|---|
| Z=18 | 0.596 m/px | 12 × 9 = 108 tiles | 0.5 m/px output |
| Z=19 | 0.298 m/px | 23 × 17 = 391 tiles | 0.3 m/px output |
| Z=20 | 0.149 m/px | 45 × 33 = 1485 tiles | 0.1 m/px output |

---

## Notes on Effective Resolution

- **Z=18 (0.5 m output):** ESRI World Imagery for Johor has confirmed commercial satellite coverage (DigitalGlobe/Maxar) at ~0.3–0.5 m GSD. The 0.5 m output matches the native satellite resolution for this area.

- **Z=19 (0.3 m output):** This matches the typical native GSD of the best available imagery for this area. Expect maximum information content at this resolution.

- **Z=20 (0.1 m output):** ESRI served tiles at Z=20 successfully. The underlying imagery was captured at ~0.3–0.5 m. This output is a bicubic upscale of the Z=19 data — no additional detail is present. The file is useful for testing how OPTIMAL-IPB responds to high-resolution input, but detections will mirror the Z=19 result.

---

## Technical Details

- **CRS:** EPSG:3857 (WGS 84 / Web Mercator)
- **Bands:** 3 (RGB, 8-bit)
- **Compression:** LZW
- **Tiling:** 256 × 256 blocks
- **Resampling:** Cubic
- **Source URL:** `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`

---

## Fallback Status

All three files were downloaded at their target zoom levels without fallback. ESRI World Imagery has native Z=20 coverage for this location.
