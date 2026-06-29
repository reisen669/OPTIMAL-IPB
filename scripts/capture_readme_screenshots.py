"""Capture three QGIS canvas screenshots + feature counts for README.

Run from: Plugins -> Python Console -> Editor tab -> open file -> Run

Assumes QGIS is already zoomed to the target area and the base raster
"merged_canvas0.5mpx_google_z19_clean" is loaded as the bottom layer.

The script, for each case:
  1. Hides ALL vector layers, shows only the named case layer.
  2. Forces a synchronous redraw of the canvas (refreshAllLayers + waitForRendering).
  3. Captures the canvas image to imgs/caseN_*.png.
  4. Records feature count.
  5. Restores all vector layer visibility at the end.
"""
import os
from qgis.core import (
    QgsProject,
    QgsMapLayerType,
    QgsMapRendererCustomPainterJob,
    QgsMapSettings,
)
from qgis.PyQt.QtCore import QSize, QEventLoop, QTimer
from qgis.PyQt.QtGui import QImage, QPainter, QColor
from qgis.utils import iface

PLUGIN_ROOT = r"C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb"
IMGS_DIR = os.path.join(PLUGIN_ROOT, "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

# Three cases: (output_layer_name, case_filename, case_label)
CASES = [
    ("0.30mpx_z19_GeoEye_mAP0.50_(pt)", "case1_geoeye_30mpx_z19.png", "GeoEye-Resnet101 (mAP@0.5=0.50)"),
    ("0.30mpx_z19_googleresnet_mAP0.30_(pt)", "case2_googleresnet_30mpx_z19.png", "Google-Resnet101 (mAP@0.5=0.30)"),
    ("0.30mpx_z19_Pleiaedes_mAP0.20_(pt)", "case3_pleiades_30mpx_z19.png", "Pleiades-Resnet101 (mAP@0.5=0.20)"),
]

project = QgsProject.instance()
root = project.layerTreeRoot()
canvas = iface.mapCanvas()

# -- Visibility helpers -------------------------------------------------

def all_vector_layer_ids():
    """Return list of IDs of all vector layers in the project (in tree order)."""
    ids = []
    for lyr in project.mapLayers().values():
        if lyr.type() == QgsMapLayerType.VectorLayer:
            ids.append(lyr.id())
    return ids


def show_only_vector_layer(target_name):
    """Hide all vector layers; show only the layer whose name matches target_name.

    Returns the matching layer ID, or None if not found.
    """
    target_id = None
    for lyr in project.mapLayers().values():
        if lyr.type() != QgsMapLayerType.VectorLayer:
            continue
        node = root.findLayer(lyr.id())
        if node is None:
            continue
        if lyr.name() == target_name:
            node.setItemVisibilityChecked(True)
            target_id = lyr.id()
        else:
            node.setItemVisibilityChecked(False)
    return target_id


def restore_all_visibility(layer_ids):
    """Re-enable visibility on all given vector layer IDs (cleanup)."""
    for lid in layer_ids:
        node = root.findLayer(lid)
        if node is not None:
            node.setItemVisibilityChecked(True)


# -- Canvas capture (synchronous) ---------------------------------------

def _wait_for_render(timeout_ms=10000):
    """Block until the canvas finishes rendering, up to timeout_ms."""
    loop = QEventLoop()
    done = [False]

    def _on_render_finished(_ok):
        if not done[0]:
            done[0] = True
            loop.quit()

    try:
        canvas.renderComplete.connect(_on_render_finished)
        QTimer.singleShot(timeout_ms, loop.quit)
        loop.exec_()
    finally:
        try:
            canvas.renderComplete.disconnect(_on_render_finished)
        except (TypeError, RuntimeError):
            pass


def capture_canvas_synchronously(out_path):
    """Force a redraw and wait for it to complete, then snapshot the canvas.

    The QGIS API does not guarantee that canvas.saveAsImage() captures the
    most recent layer-state change — it can return before the render job
    finishes. To make sure the saved PNG reflects the *current* layer
    visibility, we trigger refreshAllLayers() and block on renderComplete.
    """
    canvas.refreshAllLayers()
    # Force a synchronous render pass via mapSettings job (this blocks)
    map_settings = canvas.mapSettings()
    image = QImage(map_settings.outputSize(), QImage.Format_ARGB32)
    image.fill(QColor(255, 255, 255))
    job = QgsMapRendererCustomPainterJob(map_settings, QPainter(image))
    job.start()
    job.waitForFinished()
    del job
    image.save(out_path, "PNG")
    # Also let the live canvas finish its pending render for consistency
    _wait_for_render()


# -- Main loop ----------------------------------------------------------

def main():
    print("=" * 70)
    print("Feature counts (GeoTIFF source: Google Satellite z19 download)")
    print("Base raster: merged_canvas0.5mpx_google_z19.tif (0.298 m/px)")
    print("=" * 70)

    saved_layer_ids = all_vector_layer_ids()
    results = []

    for layer_name, filename, label in CASES:
        target_id = show_only_vector_layer(layer_name)
        if not target_id:
            print(f"[SKIP] {label}: layer '{layer_name}' not found in project")
            continue
        lyr = project.mapLayer(target_id)
        count = lyr.featureCount()
        out_path = os.path.join(IMGS_DIR, filename)
        capture_canvas_synchronously(out_path)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"[OK] {label}")
        print(f"     layer:         {layer_name}")
        print(f"     feature count: {count}")
        print(f"     screenshot:    {out_path}  ({size_kb:.1f} KB)")
        results.append((label, count, filename, out_path))

    restore_all_visibility(saved_layer_ids)
    canvas.refreshAllLayers()

    print("=" * 70)
    print("Summary (paste into README.md):")
    print("=" * 70)
    for label, count, filename, out_path in results:
        print(f"| {label} | feature count: {count} | {filename} |")
    print()
    print("All layer detections source: GeoTIFF downloaded from Google Satellite z19")
    print("Screenshots saved to:", IMGS_DIR)


main()
