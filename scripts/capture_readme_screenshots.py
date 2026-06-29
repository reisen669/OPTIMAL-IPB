"""Capture three QGIS canvas screenshots + feature counts for README.

Run from: Plugins -> Python Console -> Editor tab -> open file -> Run

Assumes QGIS is already zoomed to the target area and the base raster
"merged_canvas0.5mpx_google_z19_clean" is loaded as the bottom layer.

Implementation note (do not use QgsMapRendererCustomPainterJob here):
    QPainter resources in QGIS are owned by the main thread. Calling
    `QgsMapRendererCustomPainterJob.waitForFinished()` from the QGIS
    Python Console blocks the main thread and triggers a Windows access
    violation (QPainter::setCompositionMode) if any other QGIS worker
    thread (e.g., tile downloader, processing algorithm) is concurrently
    trying to render or modify map state.

    Correct approach: trigger the live canvas to redraw with the new layer
    visibility, and block on the canvas.renderComplete signal (a
    signal-and-slot idiom that is the supported way to wait for a
    synchronous render from the main thread).
"""
import os
from qgis.core import (
    QgsProject,
    QgsMapLayerType,
)
from qgis.PyQt.QtCore import QEventLoop, QTimer
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
    """Return list of IDs of all vector layers in the project."""
    return [
        lyr.id() for lyr in project.mapLayers().values()
        if lyr.type() == QgsMapLayerType.VectorLayer
    ]


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


# -- Render barrier -----------------------------------------------------

def _wait_for_render(timeout_ms=15000):
    """Block until the canvas finishes its current render, up to timeout_ms.

    Uses a single-shot connection to canvas.renderComplete to break out of a
    local QEventLoop. Falls back to timeout if no render is in flight.
    """
    loop = QEventLoop()
    finished = [False]

    def _on_render_done(_ok):
        if not finished[0]:
            finished[0] = True
            loop.quit()

    try:
        canvas.renderComplete.connect(_on_render_done)
    except (TypeError, RuntimeError):
        # If a connection is already in place, that's fine — disconnect
        # attempts below will handle it.
        pass
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(timeout_ms)
    loop.exec_()
    timer.stop()
    try:
        canvas.renderComplete.disconnect(_on_render_done)
    except (TypeError, RuntimeError):
        pass


def trigger_redraw_and_capture(out_path):
    """Trigger a redraw on the main thread canvas and save the result.

    Steps:
      1. canvas.refreshAllLayers()  -> schedules a new render.
      2. _wait_for_render()          -> blocks on renderComplete signal.
      3. canvas.saveAsImage(path)    -> saves the latest rendered canvas.
    """
    canvas.refreshAllLayers()
    # Pump the event loop briefly so the render job is actually kicked off
    # before we start waiting. Otherwise the first call may exit immediately.
    wait_loop = QEventLoop()
    QTimer.singleShot(50, wait_loop.quit)
    wait_loop.exec_()
    _wait_for_render()
    canvas.saveAsImage(out_path, None, "PNG")
    # Small extra wait to let any pending UI events settle
    settle_loop = QEventLoop()
    QTimer.singleShot(50, settle_loop.quit)
    settle_loop.exec_()


# -- Main loop ----------------------------------------------------------

def main():
    print("=" * 70)
    print("Feature counts (GeoTIFF source: Google Satellite z19 download)")
    print("Base raster: merged_canvas0.5mpx_google_z19.tif (0.298 m/px)")
    print("=" * 70)
    print("WARNING: stop any background QGIS jobs (tile download, processing)")
    print("         before running this script — concurrent renders crash.")
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
        try:
            trigger_redraw_and_capture(out_path)
        except Exception as exc:
            print(f"[ERROR] {label}: render failed: {exc}")
            # Restore visibility before bailing
            restore_all_visibility(saved_layer_ids)
            canvas.refreshAllLayers()
            raise
        size_kb = os.path.getsize(out_path) / 1024 if os.path.exists(out_path) else 0
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
