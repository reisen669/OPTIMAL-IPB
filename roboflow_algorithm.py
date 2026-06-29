# -*- coding: utf-8 -*-
"""
Roboflow Palm Detection — QGIS Processing Algorithm
Calls the UiTM oil-palm-aerial-detection/1 hosted model via Roboflow API.
Resolution-aware: tiles are resampled to the model's training scale (10 cm/px)
before being sent, so the algorithm works correctly regardless of input resolution.
API key is read from QGIS global variable 'roboflow_api_key' — never hardcoded.
"""

from __future__ import division

import base64
import io
import json
import os
import time
import urllib.parse
import urllib.request

import numpy as np
from osgeo import gdal

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsExpressionContextUtils,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMessageLog,
    QgsPoint,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
    QgsWkbTypes,
)

from .helpers import pixel2coord, map_uint16_to_uint8

# ── Roboflow API ──────────────────────────────────────────────────────────────
_RF_BASE_URL = "https://detect.roboflow.com"
_RF_MODEL_ID = "oil-palm-aerial-detection/1"
_RF_ENV_KEY  = "ROBOFLOW_API_KEY"

# ── Model constants ────────────────────────────────────────────────────────────
# Training resolution of the UiTM YOLOv8n model
_MODEL_RESOLUTION_M = 0.10   # 10 cm/px
_MODEL_INPUT_PX     = 640    # model input tile size

_OUTPUT_TYPES = ["Point", "Bounding Box"]
_WKB_MAP = {0: QgsWkbTypes.Point, 1: QgsWkbTypes.Polygon}


class _MinMax:
    def __init__(self, lo, hi):
        self.minimum, self.maximum = lo, hi


def _to_jpeg_bytes(rgb_hwc_uint8):
    """Convert (H, W, 3) uint8 RGB array → JPEG bytes via PIL."""
    try:
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(rgb_hwc_uint8, 'RGB').save(buf, format='JPEG', quality=88)
        return buf.getvalue()
    except ImportError:
        pass
    try:
        import cv2
        ok, buf = cv2.imencode('.jpg', rgb_hwc_uint8[:, :, ::-1],
                               [cv2.IMWRITE_JPEG_QUALITY, 88])
        if ok:
            return bytes(buf)
    except ImportError:
        pass
    raise RuntimeError("Pillow (or cv2) required — install: pip install Pillow")


def _upsample_rgb(rgb_hwc, target_px):
    """Upsample (H, W, 3) uint8 array to target_px × target_px via PIL."""
    from PIL import Image
    h, w = rgb_hwc.shape[:2]
    if h == target_px and w == target_px:
        return rgb_hwc
    img = Image.fromarray(rgb_hwc, 'RGB').resize(
        (target_px, target_px), Image.BILINEAR)
    return np.array(img, dtype=np.uint8)


def _rf_infer(jpeg_bytes, api_key, confidence_pct, overlap_pct=30):
    """
    POST a JPEG to the Roboflow detection API.
    Returns list of raw prediction dicts (x, y, width, height, confidence, class).
    API key travels only via HTTPS query string — never printed.
    Raises on HTTP/network error so the caller can surface it.
    """
    b64 = base64.b64encode(jpeg_bytes).decode('utf-8')
    url = (
        f"{_RF_BASE_URL}/{_RF_MODEL_ID}"
        f"?api_key={urllib.parse.quote(api_key, safe='')}"
        f"&confidence={confidence_pct}&overlap={overlap_pct}"
    )
    req = urllib.request.Request(
        url,
        data=b64.encode('utf-8'),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result.get('predictions', [])


class RoboflowPalmDetectionAlgorithm(QgsProcessingAlgorithm):
    """
    Detects oil palms via the Roboflow hosted inference API
    (UiTM oil-palm-aerial-detection/1, YOLOv8n, mAP 91.66 %, ~8 500 aerial images).

    Resolution-aware: each raster window is resampled to 10 cm/px (the model's
    training scale) before being sent, so it works on any input resolution.

    Requires internet access and the QGIS global variable 'roboflow_api_key'.
    Free tier: ~1 000 API calls/month; each tile = 1 call.
    """

    INPUT       = 'INPUT'
    CONFIDENCE  = 'CONFIDENCE'
    TYPE        = 'TYPE'
    OUTPUT      = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT, self.tr('Input raster layer'),
            [QgsProcessing.TypeRaster],
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.CONFIDENCE, self.tr('Confidence threshold (0–1)'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.25, minValue=0.01, maxValue=1.0,
        ))
        self.addParameter(QgsProcessingParameterEnum(
            self.TYPE, self.tr('Output geometry type'),
            options=_OUTPUT_TYPES, defaultValue=0,
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, self.tr('Palm detections (Roboflow UiTM)'),
            QgsProcessing.TypeVectorAnyGeometry,
        ))

    def processAlgorithm(self, parameters, context, feedback):
        # ── API key ──────────────────────────────────────────────────────────
        api_key = (
            QgsExpressionContextUtils.globalScope()
            .variable('roboflow_api_key') or ''
        ).strip()
        if not api_key:
            api_key = os.environ.get(_RF_ENV_KEY, '').strip()
        if not api_key:
            feedback.reportError(
                "Roboflow API key not set.\n"
                "Run in the QGIS Python Console:\n"
                "  from qgis.core import QgsExpressionContextUtils\n"
                "  QgsExpressionContextUtils.setGlobalVariable("
                "'roboflow_api_key', 'YOUR_KEY')",
                fatalError=True)
            return {}

        # ── Pillow check ─────────────────────────────────────────────────────
        try:
            from PIL import Image as _PIL
        except ImportError:
            feedback.reportError(
                "Pillow not found in QGIS Python. Run: pip install Pillow",
                fatalError=True)
            return {}

        # ── parameters ───────────────────────────────────────────────────────
        confidence = self.parameterAsDouble(parameters, self.CONFIDENCE, context)
        confidence_pct = max(1, int(confidence * 100))
        type_val   = self.parameterAsEnum(parameters, self.TYPE, context)
        source     = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        # ── open raster ───────────────────────────────────────────────────────
        ds = gdal.Open(source.source())
        if ds is None:
            feedback.reportError(f"Cannot open raster: {source.source()}",
                                 fatalError=True)
            return {}
        gt    = ds.GetGeoTransform()
        W, H  = ds.RasterXSize, ds.RasterYSize

        # pixel size in map units (assume projected CRS in metres; approximate)
        raster_m_per_px = abs(gt[1])
        feedback.pushInfo(
            f"Raster: {W} × {H} px  |  pixel size: {raster_m_per_px:.4f} m/px  "
            f"|  layer: {source.name()}")

        # ── resolution-aware tile size ────────────────────────────────────────
        # Ground area one model tile covers (at training resolution)
        tile_ground_m = _MODEL_INPUT_PX * _MODEL_RESOLUTION_M  # = 64 m

        # How many raster pixels span that ground distance
        raster_tile_px = max(32, round(tile_ground_m / raster_m_per_px))

        # Scale factor: model pixels ÷ raster pixels (> 1 = upsampling required)
        upsample = _MODEL_INPUT_PX / raster_tile_px

        # Overlap: keep ~6 % of the tile on each side (same ratio as 40/640)
        overlap_px = max(2, round(raster_tile_px * 40 / 640))
        stride_px  = raster_tile_px - overlap_px

        feedback.pushInfo(
            f"Tile: {raster_tile_px} raster px → upsampled {upsample:.1f}× "
            f"to {_MODEL_INPUT_PX} px  |  overlap: {overlap_px} px  "
            f"|  stride: {stride_px} px")

        # ── per-band stretch (for uint16 rasters) ────────────────────────────
        minmaxlist = []
        for b in range(1, min(ds.RasterCount, 3) + 1):
            arr = ds.GetRasterBand(b).ReadAsArray()
            lo, hi = np.percentile(arr, (2, 98))
            minmaxlist.append(_MinMax(lo, hi))

        # ── output sink ───────────────────────────────────────────────────────
        fields = QgsFields()
        fields.append(QgsField('Score', QVariant.Double, 'double', 10, 4))
        fields.append(QgsField('Class', QVariant.String, 'string', 32))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            fields, _WKB_MAP[type_val], source.crs())

        # ── tile grid ─────────────────────────────────────────────────────────
        xs = list(range(0, W, stride_px))
        ys = list(range(0, H, stride_px))
        total = len(xs) * len(ys)
        feedback.pushInfo(f"Total tiles to send: {total}")

        all_boxes  = []   # [x1,y1,x2,y2] in raster pixels
        all_scores = []
        all_classes= []
        n_done = 0
        n_api_errors = 0

        for y_off in ys:
            if feedback.isCanceled():
                break
            for x_off in xs:
                if feedback.isCanceled():
                    break

                x0 = min(x_off, max(0, W - raster_tile_px))
                y0 = min(y_off, max(0, H - raster_tile_px))
                tw = min(raster_tile_px, W - x0)
                th = min(raster_tile_px, H - y0)

                tile_arr = ds.ReadAsArray(x0, y0, tw, th)
                if tile_arr is None or tile_arr.ndim < 3 or tile_arr.shape[0] < 3:
                    n_done += 1
                    feedback.setProgress(int(n_done / total * 100))
                    continue

                # normalise to uint8
                if ds.GetRasterBand(1).DataType != 1:
                    bands = [
                        map_uint16_to_uint8(tile_arr[i],
                                            int(minmaxlist[i].minimum),
                                            int(minmaxlist[i].maximum))
                        for i in range(3)
                    ]
                    rgb_chw = np.stack(bands, axis=0)
                else:
                    rgb_chw = tile_arr[:3].astype(np.uint8)

                # pad if at raster edge, then convert CHW→HWC
                if tw < raster_tile_px or th < raster_tile_px:
                    padded = np.zeros((3, raster_tile_px, raster_tile_px),
                                     dtype=np.uint8)
                    padded[:, :th, :tw] = rgb_chw
                    rgb_chw = padded
                rgb_hwc = rgb_chw.transpose(1, 2, 0)

                # upsample to model input size
                rgb_model = _upsample_rgb(rgb_hwc, _MODEL_INPUT_PX)

                # encode and call API
                try:
                    jpeg = _to_jpeg_bytes(rgb_model)
                    preds = _rf_infer(jpeg, api_key, confidence_pct)
                except Exception as e:
                    n_api_errors += 1
                    msg = f"[Roboflow] tile ({x0},{y0}) error: {e}"
                    feedback.pushWarning(msg)
                    QgsMessageLog.logMessage(msg, 'OPTIMAL-IPB')
                    n_done += 1
                    feedback.setProgress(int(n_done / total * 100))
                    time.sleep(0.5)
                    continue

                # map predictions from model pixel space → raster pixel space
                scale = raster_tile_px / _MODEL_INPUT_PX  # e.g. 0.2 at 0.5 m/px
                for p in preds:
                    cx_m, cy_m = p['x'], p['y']
                    w_m,  h_m  = p['width'], p['height']

                    # skip if centre is in the overlap zone of a prior tile
                    cx_tile = cx_m * scale
                    cy_tile = cy_m * scale
                    if x_off > 0 and cx_tile < overlap_px // 2:
                        continue
                    if y_off > 0 and cy_tile < overlap_px // 2:
                        continue

                    # raster-pixel bounding box
                    x1r = int(x0 + (cx_m - w_m / 2) * scale)
                    y1r = int(y0 + (cy_m - h_m / 2) * scale)
                    x2r = int(x0 + (cx_m + w_m / 2) * scale)
                    y2r = int(y0 + (cy_m + h_m / 2) * scale)
                    all_boxes.append([x1r, y1r, x2r, y2r])
                    all_scores.append(p['confidence'])
                    all_classes.append(p.get('class', 'palm'))

                n_done += 1
                feedback.setProgress(int(n_done / total * 100))
                time.sleep(0.1)   # light rate-limit courtesy

        ds_closed = None
        feedback.pushInfo(
            f"API calls: {n_done}  |  errors: {n_api_errors}  "
            f"|  raw detections: {len(all_boxes)}")

        # ── NMS ──────────────────────────────────────────────────────────────
        if all_boxes:
            try:
                from lsnms import nms
                boxes_arr  = np.array(all_boxes,   dtype=np.float32)
                scores_arr = np.array(all_scores,  dtype=np.float32)
                keep       = nms(boxes_arr, scores_arr, iou_threshold=0.3)
                boxes_arr  = boxes_arr[keep]
                scores_arr = scores_arr[keep]
                classes_arr= [all_classes[i] for i in keep]
            except ImportError:
                boxes_arr  = np.array(all_boxes,  dtype=np.float32)
                scores_arr = np.array(all_scores, dtype=np.float32)
                classes_arr= all_classes
                feedback.pushWarning("lsnms not found — skipping NMS; "
                                     "duplicate detections near tile edges possible")
        else:
            boxes_arr   = np.zeros((0, 4), dtype=np.float32)
            scores_arr  = np.array([], dtype=np.float32)
            classes_arr = []

        # ── write features ────────────────────────────────────────────────────
        ds2 = gdal.Open(source.source())
        feat = QgsFeature(fields)
        for k in range(boxes_arr.shape[0]):
            b  = boxes_arr[k].astype(int)
            sc = float(scores_arr[k])
            cl = classes_arr[k]
            x1, y1, x2, y2 = b[0], b[1], b[2], b[3]
            xc = (x1 + x2) / 2.0
            yc = (y1 + y2) / 2.0

            coor_xc, coor_yc = pixel2coord(ds2, xc, yc)

            if type_val == 0:
                feat.setGeometry(QgsGeometry(QgsPoint(coor_xc, coor_yc)))
            else:
                coor_x1, coor_y1 = pixel2coord(ds2, x1, y1)
                coor_x2, coor_y2 = pixel2coord(ds2, x2, y1)
                coor_x3, coor_y3 = pixel2coord(ds2, x2, y2)
                coor_x4, coor_y4 = pixel2coord(ds2, x1, y2)
                feat.setGeometry(QgsGeometry.fromPolygonXY([[
                    QgsPointXY(coor_x1, coor_y1),
                    QgsPointXY(coor_x2, coor_y2),
                    QgsPointXY(coor_x3, coor_y3),
                    QgsPointXY(coor_x4, coor_y4),
                ]]))

            feat.setAttribute(0, sc)
            feat.setAttribute(1, cl)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        ds2 = None
        feedback.pushInfo(
            f"Done — {boxes_arr.shape[0]} palm(s) after NMS  "
            f"(conf ≥ {confidence:.0%}, model: {_RF_MODEL_ID})")

        if n_api_errors == n_done and n_done > 0:
            feedback.reportError(
                "All API calls failed. Check your internet connection and "
                "that roboflow_api_key is valid.")

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'roboflow-palm-detection'

    def displayName(self):
        return self.tr('Roboflow Palm Detection (API)')

    def shortHelpString(self):
        return self.tr(
            'Detects oil palms via Roboflow hosted inference '
            '(UiTM YOLOv8n, oil-palm-aerial-detection/1, mAP 91.66 %).\n\n'
            'Works at any input resolution — tiles are resampled to the model\'s '
            'training scale (10 cm/px) before being sent.\n\n'
            'Prerequisite: set QGIS global variable roboflow_api_key:\n'
            '  from qgis.core import QgsExpressionContextUtils\n'
            '  QgsExpressionContextUtils.setGlobalVariable(\n'
            '      "roboflow_api_key", "YOUR_KEY")\n\n'
            'Internet access required. Free tier: ~1000 calls/month.'
        )

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RoboflowPalmDetectionAlgorithm()
