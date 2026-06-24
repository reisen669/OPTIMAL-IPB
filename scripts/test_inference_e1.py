"""Test E1 CanopyRS Faster R-CNN+R50 ONNX model on Perak 5cm and Rupat 8.8cm rasters.

STATUS: SKIPPED — Plan 06-02 determined E1 CanopyRS is BLOCKED.

Reason: No pretrained weights available on GitHub Releases (source archives only).
        canopyrs package requires Linux (Ubuntu 22.04), Python 3.10, CUDA 12.6,
        and SAM 3 (gated HuggingFace model). This project runs Windows / Python
        3.12 / CPU. E1 empirical testing is skipped in Phase 6.

If E1 weights become available in a future release (e.g., CanopyRS v2 with public
weights, or an alternative XPRIZE Rainforest checkpoint), this script would run:

Usage (when E1 ONNX model is available):
    python test_inference_e1.py
    python test_inference_e1.py --raster tif_online_samples/oam_perak_01E2b_0.05mpx.tif
    python test_inference_e1.py --raster tif_online_samples/oam_rupat_indonesia_0.088mpx.tif

Test rasters (VHR tier, 3-10 cm/px):
    oam_perak_01E2b_0.05mpx.tif    — Perak, Malaysia 5 cm/px oil palm plantation
    oam_rupat_indonesia_0.088mpx.tif — Rupat, Indonesia 8.8 cm/px oil palm plantation

Model: models/canopyrs_frcnn_r50.onnx
  Architecture: Faster R-CNN + ResNet-50 FPN (fasterrcnn_resnet50_fpn from torchvision)
  Training domain: Tropical rainforest (3 countries, XPRIZE Rainforest context)
  Expected domain gap vs SE Asia oil palm: MEDIUM (tropical tree crowns similar
    to palm crowns; lacks plantation row geometry)
  Comparison to E2 VHRTrees (Turkey): E1 expected to show better tropical-domain
    precision, but still lacks palm-specific training

ONNX output format (when export succeeds via models/export_e1_onnx.py):
  Input:  'images' [1, 3, H, W] float32 (ImageNet-normalized, variable H/W)
  Output: 'boxes'  [N, 4] float32 — [x1, y1, x2, y2] per detection (xyxy format)
          'scores' [N]    float32 — confidence per detection
          'labels' [N]    int64   — class index per detection
  Note: Torchvision Faster R-CNN applies NMS internally — no external NMS needed.
  Note: Boxes in [x1, y1, x2, y2] format (NOT cxcywh like YOLOv8).

Inference pipeline (when weights become available):
    1. Load ONNX model via onnxruntime InferenceSession
    2. Open GeoTIFF with GDAL
    3. Compute per-band 2nd/98th percentile for uint16 -> uint8 normalization
    4. Sliding window (500px tiles, 470px step)
    5. Preprocess: uint8 RGB -> float32 [0,1] -> ImageNet normalize -> CHW -> batch
    6. Run session.run(None, {'images': input_tensor})
    7. Collect boxes/scores, offset by tile position, filter by score threshold
    8. Print detection count, confidence range, domain gap comparison

ImageNet normalization (required for Faster R-CNN+R50 pretrained on COCO):
    mean = [0.485, 0.456, 0.406]
    std  = [0.229, 0.224, 0.225]
    normalized = (rgb_float - mean) / std

See:
    models/export_e1_onnx.py      — ONNX export script (SKIPPED / blocker documented)
    models/inspect_e1_checkpoint.py — checkpoint structure inspector (SKIPPED)
    models/MODEL_CONVERSION_STATUS.md — overall model status
    .planning/phases/06-.../06-02-SUMMARY.md — E1 CANOPYRS COMPATIBILITY REPORT
    scripts/test_inference_e2.py  — E2 VHRTrees inference script (reference pattern)
"""

import os
import sys

# Plugin root path
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PLUGIN_ROOT)


def main():
    model_path = os.path.join(PLUGIN_ROOT, 'models', 'canopyrs_frcnn_r50.onnx')
    perak_path = os.path.join(PLUGIN_ROOT, 'tif_online_samples', 'oam_perak_01E2b_0.05mpx.tif')
    rupat_path = os.path.join(PLUGIN_ROOT, 'tif_online_samples', 'oam_rupat_indonesia_0.088mpx.tif')

    print("=" * 60)
    print("E1 CanopyRS Faster R-CNN+R50 Inference Test")
    print("=" * 60)
    print(f"Model: {model_path}")
    print()

    # Gate check — ONNX model must exist to run inference
    if not os.path.exists(model_path):
        print("E1 INFERENCE: SKIPPED — ONNX export was not completed")
        print()
        print("Reason: Plan 06-02 determined E1 CanopyRS is BLOCKED:")
        print("  - No pretrained weights on GitHub Releases (source archives only)")
        print("  - canopyrs requires Linux (Ubuntu 22.04) / Python 3.10 / CUDA 12.6")
        print("  - Current CanopyRS depends on SAM 3 (gated HuggingFace model)")
        print("  - This project runs Windows / Python 3.12 / CPU")
        print()
        print("See models/export_e1_onnx.py for E1 ONNX EXPORT REPORT.")
        print("See .planning/phases/06-.../06-02-SUMMARY.md for full details.")
        print()
        print("Rasters that would be tested (if model were available):")
        print(f"  oam_perak:  {perak_path}")
        print(f"    exists: {os.path.exists(perak_path)}")
        print(f"  oam_rupat:  {rupat_path}")
        print(f"    exists: {os.path.exists(rupat_path)}")
        print()

        # Domain gap note (always print for completeness)
        _print_domain_gap_note()
        return

    # -------------------------------------------------------------------------
    # INFERENCE PATH (only reached when canopyrs_frcnn_r50.onnx exists)
    # -------------------------------------------------------------------------
    import argparse
    import numpy as np

    try:
        import onnxruntime as ort
    except ImportError:
        print("ERROR: onnxruntime not installed.")
        sys.exit(1)

    try:
        from osgeo import gdal
        gdal.UseExceptions()
    except ImportError:
        print("ERROR: GDAL/osgeo not available. Ensure qgis_gdal_env is active.")
        sys.exit(1)

    try:
        from helpers import sliding_window, map_uint16_to_uint8
    except ImportError:
        def sliding_window(width, height, stepSize):
            for y in range(0, height, stepSize):
                for x in range(0, width, stepSize):
                    yield (x, y)

        def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
            if lower_bound is None:
                lower_bound = int(np.min(img))
            if upper_bound is None:
                upper_bound = int(np.max(img))
            if lower_bound >= upper_bound:
                lower_bound = upper_bound - 1
            lut = np.concatenate([
                np.zeros(lower_bound, dtype=np.uint16),
                np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
                np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
            ])
            return lut[img].astype(np.uint8)

    # ImageNet normalization constants (for torchvision Faster R-CNN pretrained on COCO)
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def preprocess_tile(tile_data, datatype, minmaxlist):
        """Convert GDAL tile data to ImageNet-normalized [1, 3, H, W] float32 tensor.

        Args:
            tile_data: numpy array (bands, H, W) from GDAL ReadAsArray
            datatype: GDAL datatype int (1 = uint8, else uint16)
            minmaxlist: list of {'min': int, 'max': int} per band

        Returns:
            numpy array [1, 3, H, W] float32, ImageNet-normalized
        """
        if tile_data.ndim == 2:
            tile_data = np.stack([tile_data, tile_data, tile_data], axis=0)

        if datatype != 1:  # uint16
            rgb_channels = []
            for band_idx in range(min(3, tile_data.shape[0])):
                mm = minmaxlist[band_idx] if band_idx < len(minmaxlist) else {'min': 0, 'max': 65535}
                lo, hi = mm['min'], mm['max']
                if lo >= hi:
                    lo, hi = 0, max(1, int(tile_data[band_idx].max()))
                band_u8 = map_uint16_to_uint8(tile_data[band_idx], lo, hi)
                rgb_channels.append(band_u8)
            rgb_img = np.dstack(rgb_channels)  # HxWx3 uint8
        else:
            if tile_data.shape[0] >= 3:
                rgb_img = np.dstack([tile_data[0], tile_data[1], tile_data[2]])
            else:
                rgb_img = np.dstack([tile_data[0], tile_data[0], tile_data[0]])

        # uint8 -> float32 [0, 1]
        img_float = rgb_img.astype(np.float32) / 255.0

        # ImageNet normalization: (x - mean) / std per channel
        img_float = (img_float - IMAGENET_MEAN) / IMAGENET_STD

        # HWC -> CHW -> add batch dim [1, 3, H, W]
        img_chw = np.transpose(img_float, (2, 0, 1))
        img_batch = np.expand_dims(img_chw, axis=0)
        return img_batch.astype(np.float32)

    def infer_e1(model_path, raster_path, score_threshold=0.25,
                 tile_size=500, tile_step=470, verbose=True):
        """Run E1 CanopyRS Faster R-CNN+R50 inference on a GeoTIFF raster.

        Returns dict with 'detections', 'count', 'min_conf', 'max_conf', etc.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX model not found: {model_path}")
        if not os.path.exists(raster_path):
            raise FileNotFoundError(f"Raster not found: {raster_path}")

        sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        input_name = sess.get_inputs()[0].name   # expected: 'images'
        output_names = [o.name for o in sess.get_outputs()]  # expected: ['boxes', 'scores', 'labels']

        if verbose:
            print(f"  Model inputs:  {[i.name for i in sess.get_inputs()]}")
            print(f"  Model outputs: {output_names}")

        ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
        if ds is None:
            raise RuntimeError(f"GDAL failed to open: {raster_path}")

        raster_w = ds.RasterXSize
        raster_h = ds.RasterYSize
        num_bands = ds.RasterCount
        datatype = ds.GetRasterBand(1).DataType

        if verbose:
            print(f"  Raster: {raster_w}x{raster_h}, bands={num_bands}, dtype={datatype}")

        # Per-band 2nd/98th percentile for uint16 normalization
        minmaxlist = []
        if datatype != 1:
            if verbose:
                print("  Computing per-band 2nd/98th percentile for uint16 normalization...")
            for band_idx in range(1, min(num_bands + 1, 4)):
                band = ds.GetRasterBand(band_idx)
                data = band.ReadAsArray()
                valid = data[data > 0]
                if len(valid) == 0:
                    minmaxlist.append({'min': 0, 'max': 255})
                else:
                    p2 = float(np.percentile(valid, 2))
                    p98 = float(np.percentile(valid, 98))
                    if p2 >= p98:
                        p2, p98 = float(np.min(valid)), float(np.max(valid))
                    if p2 >= p98:
                        p2, p98 = 0.0, 1.0
                    minmaxlist.append({'min': int(p2), 'max': int(p98)})

        all_detections = []
        tiles_processed = 0

        for tile_x, tile_y in sliding_window(raster_w, raster_h, tile_step):
            actual_w = min(tile_size, raster_w - tile_x)
            actual_h = min(tile_size, raster_h - tile_y)
            if actual_w <= 0 or actual_h <= 0:
                continue

            tile_data = ds.ReadAsArray(tile_x, tile_y, actual_w, actual_h)
            if tile_data is None:
                continue

            # Preprocess to [1, 3, H, W] float32 ImageNet-normalized
            img_batch = preprocess_tile(tile_data, datatype, minmaxlist)

            # Run inference
            outputs = sess.run(None, {input_name: img_batch})

            # Torchvision Faster R-CNN outputs (NMS already applied internally):
            # outputs[0]: boxes  [N, 4] float32 [x1, y1, x2, y2] in tile coords
            # outputs[1]: scores [N]    float32
            # outputs[2]: labels [N]    int64

            # Handle batch dim (output may be [1, N, 4] or [N, 4])
            boxes = outputs[0]
            scores = outputs[1]

            if boxes.ndim == 3:
                boxes = boxes[0]   # remove batch dim
            if scores.ndim == 2:
                scores = scores[0]

            if len(boxes) == 0:
                tiles_processed += 1
                continue

            # Filter by score threshold
            mask = scores > score_threshold
            boxes = boxes[mask]
            scores_filt = scores[mask]

            if len(boxes) > 0:
                # Offset by tile position (boxes are in tile-local [x1,y1,x2,y2])
                tile_boxes = boxes.copy()
                tile_boxes[:, [0, 2]] += tile_x
                tile_boxes[:, [1, 3]] += tile_y

                for box, score in zip(tile_boxes, scores_filt):
                    all_detections.append([box[0], box[1], box[2], box[3], float(score)])

            tiles_processed += 1

        ds = None  # close GDAL dataset

        detections = np.array(all_detections, dtype=np.float32) if all_detections else np.zeros((0, 5), dtype=np.float32)
        count = len(detections)
        min_conf = float(detections[:, 4].min()) if count > 0 else 0.0
        max_conf = float(detections[:, 4].max()) if count > 0 else 0.0

        return {
            'detections': detections,
            'count': count,
            'min_conf': min_conf,
            'max_conf': max_conf,
            'raster_width': raster_w,
            'raster_height': raster_h,
            'num_bands': num_bands,
            'tiles_processed': tiles_processed,
        }

    # Parse CLI args
    parser = argparse.ArgumentParser(
        description="Test E1 CanopyRS Faster R-CNN+R50 ONNX model on GeoTIFF rasters"
    )
    parser.add_argument('--raster', type=str, default=None,
                        help='Path to raster (relative to plugin root)')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Score confidence threshold (default: 0.25)')
    parser.add_argument('--tile-size', type=int, default=500,
                        help='Sliding window tile size in pixels (default: 500)')
    parser.add_argument('--tile-step', type=int, default=470,
                        help='Sliding window step size in pixels (default: 470)')
    args = parser.parse_args()

    # Determine test rasters
    if args.raster:
        test_rasters = [os.path.join(PLUGIN_ROOT, args.raster)]
    else:
        test_rasters = [perak_path, rupat_path]

    print(f"Score threshold: {args.conf}")
    print(f"Tile size:       {args.tile_size}x{args.tile_size} px")
    print(f"Tile step:       {args.tile_step} px (overlap: {args.tile_size - args.tile_step} px)")
    print(f"CNN engine:      CPU (onnxruntime)")
    print()

    all_results = {}

    for raster_path in test_rasters:
        raster_name = os.path.basename(raster_path)
        print(f"--- Raster: {raster_name} ---")

        if not os.path.exists(raster_path):
            print(f"  [SKIP] Raster not found: {raster_path}")
            all_results[raster_name] = {'count': None, 'error': 'Raster file not found'}
            print()
            continue

        try:
            result = infer_e1(
                model_path=model_path,
                raster_path=raster_path,
                score_threshold=args.conf,
                tile_size=args.tile_size,
                tile_step=args.tile_step,
                verbose=True
            )
            print(f"  Tiles processed:  {result['tiles_processed']}")
            print(f"  Detection count:  {result['count']}")
            if result['count'] > 0:
                print(f"  Confidence range: [{result['min_conf']:.3f}, {result['max_conf']:.3f}]")
            else:
                print(f"  Confidence range: N/A (no detections)")
            all_results[raster_name] = {
                'count': result['count'],
                'min_conf': result['min_conf'],
                'max_conf': result['max_conf'],
                'raster_size': f"{result['raster_width']}x{result['raster_height']}",
                'tiles': result['tiles_processed'],
                'error': None
            }
        except Exception as exc:
            print(f"  [ERROR] {type(exc).__name__}: {exc}")
            all_results[raster_name] = {'count': None, 'error': str(exc)}

        print()

    # Results summary
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for raster_name, result in all_results.items():
        if result.get('error'):
            print(f"{raster_name}: ERROR — {result['error']}")
        elif result['count'] is None:
            print(f"{raster_name}: SKIPPED")
        elif result['count'] == 0:
            print(f"{raster_name}: 0 detections (above threshold {args.conf})")
        else:
            print(f"{raster_name}: {result['count']} detections, "
                  f"confidence [{result['min_conf']:.3f}, {result['max_conf']:.3f}]")

    _print_domain_gap_note()


def _print_domain_gap_note():
    """Print the domain gap comparison note (always displayed)."""
    print()
    print("DOMAIN GAP COMPARISON:")
    print("-" * 60)
    print("E1 CanopyRS (this model, when available):")
    print("  Training domain: Tropical rainforest (3 countries, XPRIZE Rainforest)")
    print("  SE Asia oil palm domain gap: MEDIUM")
    print("    - Tropical tree crowns similar in shape to oil palm crowns")
    print("    - Lacks plantation row geometry awareness")
    print("    - Expected: better palm-specific precision than E2 (Turkey)")
    print()
    print("E2 VHRTrees (baseline, see scripts/test_inference_e2.py):")
    print("  Training domain: Turkey satellite imagery, generic deciduous trees")
    print("  SE Asia oil palm domain gap: HIGH")
    print("    - Different crown shape and spectral signature")
    print("    - Base COCO weights used (VHRTrees fine-tuned weights unavailable)")
    print("    - Expected: low palm precision, generic object/texture detections")
    print()
    print("Phase 6 conclusion: E1 empirical comparison skipped (blocked).")
    print("Phase 7 recommendation: Seek alternative tropical canopy model with")
    print("  publicly available weights, or use palm-specific model (tribber93_yolov11_palm)")


if __name__ == '__main__':
    main()
