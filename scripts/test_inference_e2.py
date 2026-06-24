"""Test E2 VHRTrees YOLOv8m ONNX model on canvas_0.5mpx.tif and Aceh 50cm rasters.

This standalone script (NOT a QGIS plugin component) validates the E2 VHRTrees
YOLOv8m ONNX model's inference pipeline at 50 cm/px GSD.

Model: models/VHRTrees_yolov8m.onnx
  - Architecture: YOLOv8m (Ultralytics)
  - Training domain: Turkey satellite imagery, generic deciduous trees (0.5 m/px)
  - OR: Base YOLOv8m COCO weights if VHRTrees fine-tuned weights unavailable
  - Expected domain gap: HIGH for SE Asia oil palm (false positives likely)

YOLOv8 ONNX output format:
  - Input: 'images' [1, 3, 640, 640] float32 (letterboxed, normalized 0-1)
  - Output: 'output0' [1, 84, 8400] float32
    - Rows 0:4  = cx, cy, w, h (center format, 640x640 coords)
    - Row  4    = objectness score (for YOLOv8, this is absent — uses max class conf)
    - Rows 4:84 = class confidence scores (80 COCO classes)
    Note: YOLOv8 uses [cx, cy, w, h, class0, class1, ..., class79] without explicit
          objectness. Max class confidence is used directly as detection score.

Usage:
    python test_inference_e2.py
    python test_inference_e2.py --raster sample_data_qgis/canvas_0.5mpx.tif
    python test_inference_e2.py --raster tif_online_samples/oam_leuhan_aceh_0.5mpx.tif
    python test_inference_e2.py --conf 0.15 --iou 0.45
"""

import os
import sys
import argparse
import json

import numpy as np

# Plugin root path injection (to use helpers.py)
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PLUGIN_ROOT)

try:
    import onnxruntime as ort
except ImportError:
    print("ERROR: onnxruntime not installed. Run:")
    print("  pip install onnxruntime>=1.19.0")
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
    # Fallback: define inline if helpers.py not importable
    def sliding_window(width, height, stepSize):
        for y in range(0, height, stepSize):
            for x in range(0, width, stepSize):
                yield (x, y)

    def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
        if lower_bound is None:
            lower_bound = np.min(img)
        if upper_bound is None:
            upper_bound = np.max(img)
        if lower_bound >= upper_bound:
            lower_bound = upper_bound - 1
        lut = np.concatenate([
            np.zeros(lower_bound, dtype=np.uint16),
            np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
            np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
        ])
        return lut[img].astype(np.uint8)


# =============================================================================
# YOLOv8 pre/post-processing utilities
# =============================================================================

def letterbox_resize(image, target_size=640):
    """Resize image to target_size x target_size keeping aspect ratio, pad with grey.

    Args:
        image: numpy array HxWxC uint8 RGB
        target_size: output square size (default 640 for YOLOv8m)

    Returns:
        resized: numpy array target_size x target_size x C float32 (normalized 0-1)
        scale: scale factor applied (original_dim * scale = target_size)
        pad_top: number of rows padded at top
        pad_left: number of cols padded at left
    """
    import cv2

    h, w = image.shape[:2]
    scale = min(target_size / h, target_size / w)
    new_h = int(round(h * scale))
    new_w = int(round(w * scale))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Compute padding to reach target_size
    pad_h = target_size - new_h
    pad_w = target_size - new_w
    pad_top = pad_h // 2
    pad_bottom = pad_h - pad_top
    pad_left = pad_w // 2
    pad_right = pad_w - pad_left

    # Pad with grey (114 is standard YOLOv8 letterbox fill)
    letterboxed = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
    letterboxed[pad_top:pad_top + new_h, pad_left:pad_left + new_w] = resized

    return letterboxed, scale, pad_top, pad_left


def xywh2xyxy(boxes):
    """Convert [cx, cy, w, h] to [x1, y1, x2, y2].

    Args:
        boxes: array [..., 4] in center format

    Returns:
        array [..., 4] in corner format
    """
    y = np.copy(boxes)
    y[..., 0] = boxes[..., 0] - boxes[..., 2] / 2  # x1 = cx - w/2
    y[..., 1] = boxes[..., 1] - boxes[..., 3] / 2  # y1 = cy - h/2
    y[..., 2] = boxes[..., 0] + boxes[..., 2] / 2  # x2 = cx + w/2
    y[..., 3] = boxes[..., 1] + boxes[..., 3] / 2  # y2 = cy + h/2
    return y


def nms(boxes, scores, iou_thres=0.45):
    """Non-maximum suppression using IoU threshold.

    Args:
        boxes: array [N, 4] in x1y1x2y2 format
        scores: array [N]
        iou_thres: IoU threshold for suppression

    Returns:
        keep: indices of kept boxes (sorted by descending score)
    """
    if len(boxes) == 0:
        return np.array([], dtype=int)

    order = scores.argsort()[::-1]
    keep = []

    while order.size > 0:
        i = order[0]
        keep.append(i)
        if order.size == 1:
            break

        # IoU of box i with remaining boxes
        xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

        inter_w = np.maximum(0.0, xx2 - xx1)
        inter_h = np.maximum(0.0, yy2 - yy1)
        inter = inter_w * inter_h

        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_others = (
            (boxes[order[1:], 2] - boxes[order[1:], 0]) *
            (boxes[order[1:], 3] - boxes[order[1:], 1])
        )
        union = area_i + area_others - inter
        iou = inter / (union + 1e-16)

        inds = np.where(iou <= iou_thres)[0]
        order = order[inds + 1]

    return np.array(keep, dtype=int)


def yolov8_postprocess(raw_output, conf_thres=0.25, iou_thres=0.45,
                       scale=1.0, pad_top=0, pad_left=0, tile_x=0, tile_y=0,
                       tile_w=640, tile_h=640):
    """Post-process YOLOv8 ONNX output tensor.

    YOLOv8 ONNX output format: [1, 84, 8400]
      - 84 = 4 bbox coords (cx,cy,w,h) + 80 class scores
      - 8400 = grid anchors across 3 scales
      - NO separate objectness score (unlike YOLOv5)
      - Detection score = max class confidence

    Args:
        raw_output: numpy array [1, 84, 8400] from model.run()
        conf_thres: minimum detection confidence
        iou_thres: NMS IoU threshold
        scale: letterbox scale factor (used to convert 640-space back to tile-space)
        pad_top: letterbox padding rows at top
        pad_left: letterbox padding cols at left
        tile_x: tile x offset in original raster (pixels)
        tile_y: tile y offset in original raster (pixels)
        tile_w: actual tile width (before padding)
        tile_h: actual tile height (before padding)

    Returns:
        detections: numpy array [N, 5] with [x1, y1, x2, y2, score] in original raster pixels
    """
    # raw_output shape: [1, 84, 8400] — transpose to [8400, 84]
    pred = raw_output[0].transpose()  # [8400, 84]

    # Extract bbox (cx, cy, w, h) and class scores
    boxes_cxcywh = pred[:, :4]          # [8400, 4]
    class_scores = pred[:, 4:]          # [8400, 80]

    # Max class confidence as detection score
    scores = class_scores.max(axis=1)   # [8400]

    # Filter by confidence threshold
    mask = scores >= conf_thres
    if not mask.any():
        return np.zeros((0, 5), dtype=np.float32)

    boxes_cxcywh = boxes_cxcywh[mask]
    scores = scores[mask]

    # Convert to x1y1x2y2 (still in 640x640 letterbox coords)
    boxes_xyxy = xywh2xyxy(boxes_cxcywh)  # [N, 4]

    # Scale back from letterbox to tile pixel coords:
    #   1. Subtract padding offset
    #   2. Divide by scale factor
    boxes_xyxy[:, [0, 2]] = (boxes_xyxy[:, [0, 2]] - pad_left) / scale
    boxes_xyxy[:, [1, 3]] = (boxes_xyxy[:, [1, 3]] - pad_top) / scale

    # Clip to tile bounds
    boxes_xyxy[:, 0] = np.clip(boxes_xyxy[:, 0], 0, tile_w)
    boxes_xyxy[:, 2] = np.clip(boxes_xyxy[:, 2], 0, tile_w)
    boxes_xyxy[:, 1] = np.clip(boxes_xyxy[:, 1], 0, tile_h)
    boxes_xyxy[:, 3] = np.clip(boxes_xyxy[:, 3], 0, tile_h)

    # Filter out degenerate boxes (zero area)
    valid = (
        (boxes_xyxy[:, 2] - boxes_xyxy[:, 0] > 1) &
        (boxes_xyxy[:, 3] - boxes_xyxy[:, 1] > 1)
    )
    boxes_xyxy = boxes_xyxy[valid]
    scores = scores[valid]

    if len(boxes_xyxy) == 0:
        return np.zeros((0, 5), dtype=np.float32)

    # Apply NMS
    keep = nms(boxes_xyxy, scores, iou_thres)
    boxes_xyxy = boxes_xyxy[keep]
    scores = scores[keep]

    # Translate tile-relative coords to raster-global coords
    boxes_xyxy[:, [0, 2]] += tile_x
    boxes_xyxy[:, [1, 3]] += tile_y

    detections = np.column_stack([boxes_xyxy, scores[:, None]])
    return detections.astype(np.float32)


# =============================================================================
# Main inference function
# =============================================================================

def infer_e2(model_path, raster_path, conf_thres=0.25, iou_thres=0.45,
             tile_size=500, tile_step=470, target_model_size=640, verbose=True):
    """Run E2 VHRTrees YOLOv8m inference on a GeoTIFF raster.

    Uses a sliding window approach consistent with optimal_ipb_algorithm.py:
    - 500x500 pixel tiles with 470-pixel step (30-pixel overlap)
    - uint16 → uint8 normalization per band using 2nd/98th percentile
    - Letterbox resize to 640x640 for YOLOv8m input
    - YOLOv8-specific output post-processing (no objectness, max class conf)

    Args:
        model_path: path to VHRTrees_yolov8m.onnx
        raster_path: path to GeoTIFF raster (any number of bands; RGB assumed)
        conf_thres: detection confidence threshold (0.0–1.0)
        iou_thres: NMS IoU threshold (0.0–1.0)
        tile_size: sliding window tile width/height in pixels
        tile_step: stride between tiles in pixels
        target_model_size: YOLOv8 input size (640 for YOLOv8m)
        verbose: print progress if True

    Returns:
        dict with keys:
          - 'detections': numpy array [N, 5] with [x1, y1, x2, y2, score]
          - 'count': int detection count
          - 'min_conf': float minimum confidence (or 0.0 if no detections)
          - 'max_conf': float maximum confidence (or 0.0 if no detections)
          - 'raster_width': int raster pixel width
          - 'raster_height': int raster pixel height
          - 'num_bands': int number of raster bands
          - 'tiles_processed': int number of tiles processed
    """
    import cv2

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX model not found: {model_path}")
    if not os.path.exists(raster_path):
        raise FileNotFoundError(f"Raster not found: {raster_path}")

    # Load model
    if verbose:
        print(f"  Loading model: {os.path.basename(model_path)}")
    sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = sess.get_inputs()[0].name   # 'images'

    # Open raster
    if verbose:
        print(f"  Opening raster: {os.path.basename(raster_path)}")
    ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
    if ds is None:
        raise RuntimeError(f"GDAL failed to open: {raster_path}")

    raster_w = ds.RasterXSize
    raster_h = ds.RasterYSize
    num_bands = ds.RasterCount
    datatype = ds.GetRasterBand(1).DataType

    if verbose:
        print(f"  Raster size: {raster_w}x{raster_h}, bands={num_bands}, dtype={datatype}")

    # Pre-compute per-band 2nd/98th percentile stretch for uint16 → uint8 normalization
    # (same as optimal_ipb_algorithm.py processAlgorithm)
    minmaxlist = []
    if datatype != 1:  # not uint8 (1 = GDT_Byte)
        if verbose:
            print(f"  Computing per-band 2nd/98th percentile for uint16 normalization...")
        for band_idx in range(1, min(num_bands + 1, 4)):  # max 3 bands
            band = ds.GetRasterBand(band_idx)
            data = band.ReadAsArray()
            valid = data[data > 0]
            if len(valid) == 0:
                minmaxlist.append({'min': 0, 'max': 255})
            else:
                p2 = float(np.percentile(valid, 2))
                p98 = float(np.percentile(valid, 98))
                if p2 >= p98:
                    p2 = float(np.min(valid))
                    p98 = float(np.max(valid))
                if p2 >= p98:
                    p2 = 0.0
                    p98 = 1.0
                minmaxlist.append({'min': int(p2), 'max': int(p98)})
        if verbose:
            for i, mm in enumerate(minmaxlist):
                print(f"    Band {i+1}: p2={mm['min']}, p98={mm['max']}")

    # Sliding window inference
    all_detections = []
    tiles_processed = 0

    for tile_x, tile_y in sliding_window(raster_w, raster_h, tile_step):
        # Compute actual tile bounds (clamp to raster edge)
        actual_w = min(tile_size, raster_w - tile_x)
        actual_h = min(tile_size, raster_h - tile_y)
        if actual_w <= 0 or actual_h <= 0:
            continue

        # Read tile from raster
        tile_data = ds.ReadAsArray(tile_x, tile_y, actual_w, actual_h)
        if tile_data is None:
            continue

        # Ensure 3D array (bands, height, width)
        if tile_data.ndim == 2:
            tile_data = np.stack([tile_data, tile_data, tile_data], axis=0)

        # uint16 → uint8 normalization
        if datatype != 1:  # not uint8
            rgb_channels = []
            for band_idx in range(min(3, tile_data.shape[0])):
                mm = minmaxlist[band_idx] if band_idx < len(minmaxlist) else {'min': 0, 'max': 65535}
                lo = mm['min']
                hi = mm['max']
                if lo >= hi:
                    lo = 0
                    hi = max(1, int(tile_data[band_idx].max()))
                band_u8 = map_uint16_to_uint8(tile_data[band_idx], lo, hi)
                rgb_channels.append(band_u8)
            # Stack as HxWx3 RGB (bands are R,G,B order in GeoTIFF)
            rgb_img = np.dstack(rgb_channels)
        else:
            # uint8 already — stack bands as HxWx3
            if tile_data.shape[0] >= 3:
                rgb_img = np.dstack([tile_data[0], tile_data[1], tile_data[2]])
            else:
                rgb_img = np.dstack([tile_data[0], tile_data[0], tile_data[0]])

        # Letterbox resize to 640x640
        rgb_letterboxed, scale, pad_top, pad_left = letterbox_resize(rgb_img, target_model_size)

        # Normalize to [0, 1] float32 and convert to CHW format
        img_float = rgb_letterboxed.astype(np.float32) / 255.0
        img_chw = np.transpose(img_float, (2, 0, 1))  # HWC → CHW
        img_batch = np.expand_dims(img_chw, axis=0)   # add batch dim: [1, 3, 640, 640]

        # Run inference
        raw_output = sess.run(None, {input_name: img_batch})

        # Post-process YOLOv8 output
        tile_detections = yolov8_postprocess(
            raw_output[0],
            conf_thres=conf_thres,
            iou_thres=iou_thres,
            scale=scale,
            pad_top=pad_top,
            pad_left=pad_left,
            tile_x=tile_x,
            tile_y=tile_y,
            tile_w=actual_w,
            tile_h=actual_h
        )

        if len(tile_detections) > 0:
            all_detections.append(tile_detections)

        tiles_processed += 1

    ds = None  # close dataset

    # Combine all detections
    if len(all_detections) > 0:
        detections = np.vstack(all_detections)
    else:
        detections = np.zeros((0, 5), dtype=np.float32)

    count = len(detections)
    if count > 0:
        min_conf = float(detections[:, 4].min())
        max_conf = float(detections[:, 4].max())
    else:
        min_conf = 0.0
        max_conf = 0.0

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


# =============================================================================
# Main entry point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test E2 VHRTrees YOLOv8m ONNX model on GeoTIFF rasters"
    )
    parser.add_argument(
        '--raster', type=str, default=None,
        help='Path to raster (relative to plugin root). Default: test both canvas and Aceh.'
    )
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Confidence threshold (default: 0.25)')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='NMS IoU threshold (default: 0.45)')
    parser.add_argument('--tile-size', type=int, default=500,
                        help='Sliding window tile size in pixels (default: 500)')
    parser.add_argument('--tile-step', type=int, default=470,
                        help='Sliding window step size in pixels (default: 470)')
    parser.add_argument('--save-json', action='store_true',
                        help='Save detection results to JSON (outputs/ directory)')
    args = parser.parse_args()

    plugin_root = PLUGIN_ROOT
    model_path = os.path.join(plugin_root, 'models', 'VHRTrees_yolov8m.onnx')

    # Determine test rasters
    if args.raster:
        test_rasters = [os.path.join(plugin_root, args.raster)]
    else:
        # Default: test both rasters
        test_rasters = [
            os.path.join(plugin_root, 'sample_data_qgis', 'canvas_0.5mpx.tif'),
            os.path.join(plugin_root, 'tif_online_samples', 'oam_leuhan_aceh_0.5mpx.tif'),
        ]

    print("=" * 60)
    print("E2 VHRTrees YOLOv8m Inference Test")
    print("=" * 60)
    print(f"Model:                {model_path}")
    print(f"Confidence threshold: {args.conf}")
    print(f"IoU threshold:        {args.iou}")
    print(f"Tile size:            {args.tile_size}x{args.tile_size} px")
    print(f"Tile step:            {args.tile_step} px (overlap: {args.tile_size - args.tile_step} px)")
    print(f"CNN inference engine: CPU (onnxruntime)")
    print()

    # Check model exists
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found: {model_path}")
        print("Run: python models/export_e2_onnx.py")
        sys.exit(1)

    all_results = {}

    for raster_path in test_rasters:
        raster_name = os.path.basename(raster_path)
        print(f"--- Raster: {raster_name} ---")

        if not os.path.exists(raster_path):
            print(f"  [SKIP] Raster not found: {raster_path}")
            all_results[raster_name] = {
                'count': None,
                'min_conf': None,
                'max_conf': None,
                'error': 'Raster file not found'
            }
            continue

        try:
            result = infer_e2(
                model_path=model_path,
                raster_path=raster_path,
                conf_thres=args.conf,
                iou_thres=args.iou,
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

            # Save JSON output if requested
            if args.save_json and result['count'] > 0:
                out_dir = os.path.join(plugin_root, 'outputs')
                os.makedirs(out_dir, exist_ok=True)
                out_name = os.path.splitext(raster_name)[0] + '_e2_detections.json'
                out_path = os.path.join(out_dir, out_name)
                dets = result['detections'].tolist()
                with open(out_path, 'w') as f:
                    json.dump({
                        'model': 'VHRTrees_yolov8m.onnx',
                        'raster': raster_path,
                        'conf_thres': args.conf,
                        'iou_thres': args.iou,
                        'detections': [
                            {'x1': d[0], 'y1': d[1], 'x2': d[2], 'y2': d[3], 'score': d[4]}
                            for d in dets
                        ]
                    }, f, indent=2)
                print(f"  Detections saved: {out_path}")

        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            all_results[raster_name] = {
                'count': None,
                'min_conf': None,
                'max_conf': None,
                'error': str(e)
            }

        print()

    # =========================================================================
    # RESULTS SUMMARY
    # =========================================================================
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

    # =========================================================================
    # DOMAIN GAP NOTE
    # =========================================================================
    print()
    print("DOMAIN GAP NOTE:")
    print("-" * 60)
    print("E2 VHRTrees was trained on Turkey satellite imagery (generic")
    print("deciduous trees, 0.5 m/px GSD). The fine-tuned VHRTrees weights")
    print("were unavailable for automated download (Google Drive requires")
    print("authentication). The base YOLOv8m COCO weights were used instead.")
    print()
    print("Domain gap factors:")
    print("  1. Training domain: Turkey deciduous trees -> SE Asia oil palm")
    print("     Gap severity: HIGH - different crown shape, spectral signature")
    print("  2. Base COCO model (if VHRTrees weights unavailable):")
    print("     Gap severity: VERY HIGH - COCO is a general object detection")
    print("     dataset (80 classes: person, car, cat, etc.), not remote sensing")
    print()
    print("Expected outcomes:")
    print("  - Low palm-specific precision (false positives expected)")
    print("  - Detections may be generic objects or texture patterns")
    print("  - Zero detections above threshold is also possible")
    print("  - This result serves as a NEGATIVE CONTROL / BASELINE")
    print()
    print("For accurate palm detection, use:")
    print("  - tribber93_yolov11_palm.onnx (trained on palm imagery)")
    print("  - tree_tops_yolov9.onnx (tree top detection, 50cm GSD)")


if __name__ == '__main__':
    main()
