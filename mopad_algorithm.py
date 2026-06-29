# -*- coding: utf-8 -*-
"""
MOPAD QGIS Processing Algorithm
Faster R-CNN (ResNet-101 + FPN + BFP) with 5 palm-health classes.
Runs via onnxruntime on fixed 1024x1024 tiles.
"""

from __future__ import division

import os
import json
import numpy as np

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsFeatureSink,
    QgsGeometry,
    QgsPointXY,
    QgsPoint,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsMessageLog,
    QgsWkbTypes,
)

from osgeo import gdal
from lsnms import nms

from .helpers import sliding_window, pixel2coord, map_uint16_to_uint8

_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), 'models', 'mopad', 'MOPAD_epoch_24.onnx'
)

_TILE_SIZE = 1024
_STEP      = 900   # 124 px overlap each side

# Class 2 = Grass — not a palm, excluded from palm output by default
_CLASS_NAMES = {0: 'Dead', 1: 'Healthy', 2: 'Grass', 3: 'Small', 4: 'Yellow'}
_GRASS_CLASS = 2

_OUTPUT_TYPES   = ['Point', 'Bounding Box']
_WKB_MAP        = {0: QgsWkbTypes.Point, 1: QgsWkbTypes.Polygon}

_ort_session = None   # lazy-loaded singleton


def _get_session():
    global _ort_session
    if _ort_session is None:
        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError(
                'onnxruntime not found. Install it into the qgis_mmcv_env conda '
                'environment and make sure QGIS can see it, or install into '
                'QGIS Python: pip install onnxruntime'
            )
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        _ort_session = ort.InferenceSession(_MODEL_PATH, providers=providers)
    return _ort_session


def _preprocess(tile_chw_uint8):
    """Prepare (C, H, W) uint8 RGB tile for MOPAD. The ONNX model applies
    ImageNet normalization internally (baked in at export time)."""
    return tile_chw_uint8.astype(np.float32)[None]  # (1, 3, H, W), values 0-255


class _MinMax:
    def __init__(self, lo, hi):
        self.minimum, self.maximum = lo, hi


_bboxes   = []
_scores   = []
_classes  = []
_best_scores = {}   # cls_id → best raw score seen (before score_thr filter)


def _infer_tile(ds, x_off, y_off, minmaxlist, score_thr, exclude_grass):
    x_off    = max(0, x_off)
    y_off    = max(0, y_off)
    actual_w = min(_TILE_SIZE, ds.RasterXSize - x_off)
    actual_h = min(_TILE_SIZE, ds.RasterYSize - y_off)
    if actual_w <= 0 or actual_h <= 0:
        return

    tile = ds.ReadAsArray(x_off, y_off, actual_w, actual_h)

    if actual_w < _TILE_SIZE or actual_h < _TILE_SIZE:
        padded = np.zeros((ds.RasterCount, _TILE_SIZE, _TILE_SIZE), dtype=tile.dtype)
        padded[:, :actual_h, :actual_w] = tile
        tile = padded

    if ds.GetRasterBand(1).DataType != 1:
        bands = [
            map_uint16_to_uint8(tile[i],
                                int(minmaxlist[i].minimum),
                                int(minmaxlist[i].maximum))
            for i in range(3)
        ]
        rgb_chw = np.stack(bands, axis=0).astype(np.uint8)
    else:
        rgb_chw = tile[:3].astype(np.uint8)

    blob = _preprocess(rgb_chw)

    sess = _get_session()
    try:
        dets_out, labels_out = sess.run(['dets', 'labels'], {'image': blob})
    except Exception as e:
        QgsMessageLog.logMessage(f'[MOPAD] inference error: {e}', 'OPTIMAL-IPB')
        return

    dets   = dets_out[0]    # (MAX_DET, 5)  x1,y1,x2,y2,score
    labels = labels_out[0]  # (MAX_DET,)

    # Track best raw score per class across all tiles (for end-of-run diagnostics)
    for k in range(dets.shape[0]):
        cls_k = int(labels[k])
        if cls_k == -1:
            break
        scr_k = float(dets[k, 4])
        if scr_k > _best_scores.get(cls_k, 0.0):
            _best_scores[cls_k] = scr_k

    for k in range(dets.shape[0]):
        cls = int(labels[k])
        if cls == -1:
            break
        scr = float(dets[k, 4])
        if scr < score_thr:
            continue
        if exclude_grass and cls == _GRASS_CLASS:
            continue

        px1, py1, px2, py2 = dets[k, :4]
        cx = (px1 + px2) / 2
        cy = (py1 + py2) / 2
        if cx >= actual_w or cy >= actual_h:
            continue

        x1 = int(px1) + x_off
        y1 = int(py1) + y_off
        x2 = int(min(px2, actual_w)) + x_off
        y2 = int(min(py2, actual_h)) + y_off
        _bboxes.append([x1, y1, x2, y2])
        _scores.append(scr)
        _classes.append(cls)


class MOPADPalmAlgorithm(QgsProcessingAlgorithm):
    """
    Detects oil palm trees and assesses their health using the MOPAD Faster R-CNN
    model (ResNet-101 + FPN + BFP, mmdet v1.0.rc0, epoch 24).

    Classes:
      0 = Dead    1 = Healthy    2 = Grass (filtered by default)
      3 = Small   4 = Yellow (stressed)

    The ONNX model must be present at:
      <plugin>/models/MOPAD_epoch_24.onnx
    onnxruntime must be installed in the Python environment QGIS uses.
    """

    INPUT         = 'INPUT'
    SCORE_THR     = 'SCORE_THR'
    NMS_IOU       = 'NMS_IOU'
    TYPE          = 'TYPE'
    EXCLUDE_GRASS = 'EXCLUDE_GRASS'
    OUTPUT        = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT, self.tr('Input raster layer'), [QgsProcessing.TypeRaster],
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.SCORE_THR, self.tr('Score threshold (0–1)'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.05, minValue=0.0, maxValue=1.0,
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.NMS_IOU, self.tr('NMS IoU threshold (0–1)'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.3, minValue=0.0, maxValue=1.0,
        ))
        self.addParameter(QgsProcessingParameterEnum(
            self.TYPE, self.tr('Output geometry type'),
            options=_OUTPUT_TYPES, defaultValue=0,
        ))
        self.addParameter(QgsProcessingParameterBoolean(
            self.EXCLUDE_GRASS, self.tr('Exclude Grass detections'),
            defaultValue=True,
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, self.tr('MOPAD detections'),
            QgsProcessing.TypeVectorAnyGeometry,
        ))

    def processAlgorithm(self, parameters, context, feedback):
        if not os.path.isfile(_MODEL_PATH):
            feedback.reportError(
                f'MOPAD ONNX model not found at:\n  {_MODEL_PATH}\n'
                'Export it first using export_mopad_clean.py in qgis_mmcv_env.',
                fatalError=True,
            )
            return {}

        score_thr     = self.parameterAsDouble(parameters, self.SCORE_THR, context)
        nms_iou       = self.parameterAsDouble(parameters, self.NMS_IOU, context)
        type_val      = self.parameterAsEnum(parameters, self.TYPE, context)
        exclude_grass = self.parameterAsBoolean(parameters, self.EXCLUDE_GRASS, context)
        source        = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        ds     = gdal.Open(source.source())
        width  = ds.RasterXSize
        height = ds.RasterYSize

        minmaxlist = []
        for b in range(1, min(ds.RasterCount, 3) + 1):
            arr = ds.GetRasterBand(b).ReadAsArray()
            lo, hi = np.percentile(arr, (2, 98))
            minmaxlist.append(_MinMax(lo, hi))

        _bboxes.clear()
        _scores.clear()
        _classes.clear()
        _best_scores.clear()

        tiles   = list(sliding_window(width, height, _STEP))
        n_tiles = len(tiles)

        for idx, (x, y) in enumerate(tiles):
            if feedback.isCanceled():
                break

            tx = max(0, min(x, width - _TILE_SIZE))
            ty = max(0, min(y, height - _TILE_SIZE))
            _infer_tile(ds, tx, ty, minmaxlist, score_thr, exclude_grass)
            feedback.setProgress(int((idx + 1) / n_tiles * 100))

        if _bboxes:
            boxes_arr  = np.array(_bboxes,   dtype=np.float32)
            scores_arr = np.array(_scores,   dtype=np.float32)
            classes_arr= np.array(_classes,  dtype=np.int32)
            keep       = nms(boxes_arr, scores_arr, iou_threshold=nms_iou)
            boxes_arr  = boxes_arr[keep]
            scores_arr = scores_arr[keep]
            classes_arr= classes_arr[keep]
        else:
            boxes_arr   = np.zeros((0, 4), dtype=np.float32)
            scores_arr  = np.array([], dtype=np.float32)
            classes_arr = np.array([], dtype=np.int32)

        fields = QgsFields()
        fields.append(QgsField('Score',  QVariant.Double, 'double', 10, 4))
        fields.append(QgsField('Class',  QVariant.Int,    'integer'))
        fields.append(QgsField('Health', QVariant.String, 'string', 16))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            fields, _WKB_MAP[type_val], source.crs(),
        )

        feat = QgsFeature()
        feat.setFields(fields)

        for jk in range(boxes_arr.shape[0]):
            b   = boxes_arr[jk].astype(int)
            scr = float(scores_arr[jk])
            cls = int(classes_arr[jk])
            lbl = _CLASS_NAMES.get(cls, str(cls))

            x1, y1, x2, y2 = b[0], b[1], b[2], b[3]
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            coor_x,  coor_y  = pixel2coord(ds, cx, cy)
            coor_x1, coor_y1 = pixel2coord(ds, x1, y1)
            coor_x2, coor_y2 = pixel2coord(ds, x2, y1)
            coor_x3, coor_y3 = pixel2coord(ds, x2, y2)
            coor_x4, coor_y4 = pixel2coord(ds, x1, y2)

            if type_val == 0:
                geom = QgsGeometry(QgsPoint(coor_x, coor_y))
            else:
                polygon = [[
                    QgsPointXY(coor_x1, coor_y1),
                    QgsPointXY(coor_x2, coor_y2),
                    QgsPointXY(coor_x3, coor_y3),
                    QgsPointXY(coor_x4, coor_y4),
                ]]
                geom = QgsGeometry.fromPolygonXY(polygon)

            feat.setGeometry(geom)
            feat.setAttribute(0, scr)
            feat.setAttribute(1, cls)
            feat.setAttribute(2, lbl)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        _bboxes.clear()
        _scores.clear()
        _classes.clear()

        # Diagnostic: report best raw score per class (across all tiles, before filters)
        palm_classes = [c for c in (0, 1, 3, 4) if c in _best_scores]
        if palm_classes:
            best_palm_cls = max(palm_classes, key=lambda c: _best_scores[c])
            feedback.pushInfo(
                f'[MOPAD] best palm-health score (pre-filter): '
                f'{_best_scores[best_palm_cls]:.4f} '
                f'({_CLASS_NAMES.get(best_palm_cls, str(best_palm_cls))})'
            )
        if _GRASS_CLASS in _best_scores:
            feedback.pushInfo(
                f'[MOPAD] best Grass score: {_best_scores[_GRASS_CLASS]:.4f}'
                + ('' if not exclude_grass else ' (excluded — set Exclude Grass=False to show)')
            )
        _best_scores.clear()

        feedback.pushInfo(
            f'[MOPAD] {boxes_arr.shape[0]} detection(s) after NMS '
            f'(score>={score_thr:.2f}, exclude_grass={exclude_grass})'
        )
        return {self.OUTPUT: dest_id}

    def name(self):
        return 'mopad-palm-detection'

    def displayName(self):
        return self.tr('MOPAD Palm Health Detection')

    def shortHelpString(self):
        return self.tr(
            'Runs the MOPAD Faster R-CNN (ResNet-101 + FPN + BFP) model to detect '
            'oil palms and classify their health state:\n'
            '  0 = Dead\n  1 = Healthy\n  2 = Grass\n  3 = Small\n  4 = Yellow\n\n'
            'Requires:\n'
            '  • MOPAD_epoch_24.onnx in the plugin models/ folder\n'
            '  • onnxruntime installed in the active Python environment\n\n'
            'Tiles input at 1024×1024 px; merges results with NMS.'
        )

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return MOPADPalmAlgorithm()
