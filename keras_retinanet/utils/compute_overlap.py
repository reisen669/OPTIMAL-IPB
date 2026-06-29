"""
Pure NumPy replacement for compute_overlap Cython extension.
The original .pyx was compiled for Python 3.7 and cannot load on Python 3.12.
This module is only used for training (anchor target generation) — not inference.
"""
import numpy as np


def compute_overlap(boxes, query_boxes):
    """Compute IoU overlap between two sets of boxes.

    Args:
        boxes:       (N, 4) float64 array of (x1, y1, x2, y2)
        query_boxes: (K, 4) float64 array of (x1, y1, x2, y2)

    Returns:
        overlaps: (N, K) float64 IoU matrix
    """
    N = boxes.shape[0]
    K = query_boxes.shape[0]
    overlaps = np.zeros((N, K), dtype=np.float64)

    for k in range(K):
        box_area = (
            (query_boxes[k, 2] - query_boxes[k, 0] + 1.0) *
            (query_boxes[k, 3] - query_boxes[k, 1] + 1.0)
        )
        iw = (np.minimum(boxes[:, 2], query_boxes[k, 2]) -
              np.maximum(boxes[:, 0], query_boxes[k, 0]) + 1.0)
        ih = (np.minimum(boxes[:, 3], query_boxes[k, 3]) -
              np.maximum(boxes[:, 1], query_boxes[k, 1]) + 1.0)
        valid = (iw > 0) & (ih > 0)
        if not np.any(valid):
            continue
        intersection = iw[valid] * ih[valid]
        boxes_area = ((boxes[valid, 2] - boxes[valid, 0] + 1.0) *
                      (boxes[valid, 3] - boxes[valid, 1] + 1.0))
        union = boxes_area + box_area - intersection
        overlaps[valid, k] = intersection / union

    return overlaps
