"""Capture three QGIS canvas screenshots + feature counts for README.

Run from: Plugins -> Python Console -> Editor tab -> open file -> Run

Assumes QGIS is already zoomed to the target area and the base raster
"merged_canvas0.5mpx_google_z19_clean" is loaded as the bottom layer.

Layer name handling:
    The three detection layers have full names like
    "palm_0.30mpx/GeoEye_0.30mpx/0.30mpx_z19_GeoEye_mAP0.50_(pt)"
    (nested group path, separator is "/"). The CASES list below provides
    multiple match patterns per case; any one matching the layer's full
    name (or its basename) will be selected. The first match wins.

Canvas extent:
    The script never calls setExtent(), zoomToFullExtent(), or any method
    that changes the visible area. The user's current pan/zoom is
    preserved across all three captures.
"""
import os
from qgis.core import (
    QgsProject,
    QgsMapLayerType,
)
from qgis.PyQt.QtCore import QEventLoop, QTimer
from qgis.PyQt.QtWidgets import QApplication
from qgis.utils import iface

PLUGIN_ROOT = r"C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb"
IMGS_DIR = os.path.join(PLUGIN_ROOT, "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

# Three cases: (match_patterns, case_filename, case_label)
# A pattern matches if it is contained as a substring in the layer's full
# name (group path + name) OR equals the basename after the last "/".
# Three cases: (key_tokens, case_filename, case_label)
# A layer matches a case when its full name contains ALL of the given
# tokens (case-insensitive substring). Tokens are matched individually so
# that nested group paths like "palm_0.30mpx/GeoEye_0.30mpx/...mAP0.50_(pt)"
# are caught regardless of capitalisation.
CASES = [
    (["geoeye", "0.50"],
     "case1_geoeye_30mpx_z19.png",
     "GeoEye-Resnet101 (mAP@0.5=0.50)"),
    (["googleresnet", "0.30"],
     "case2_googleresnet_30mpx_z19.png",
     "Google-Resnet101 (mAP@0.5=0.30)"),
    (["pleiaedes", "0.20"],
     "case3_pleiades_30mpx_z19.png",
     "Pleiades-Resnet101 (mAP@0.5=0.20)"),
]

project = QgsProject.instance()
root = project.layerTreeRoot()
canvas = iface.mapCanvas()


# -- Layer matching -----------------------------------------------------

def find_layer_by_patterns(tokens):
    """Find first vector layer whose name (lowercased) contains ALL tokens.

    Tokens are matched case-insensitively as substrings of the full layer
    name (group path + name). Returns (layer, full_name) or (None, None).
    """
    tokens_lower = [t.lower() for t in tokens]
    for lyr in project.mapLayers().values():
        if lyr.type() != QgsMapLayerType.VectorLayer:
            continue
        full_name = lyr.name()
        full_lower = full_name.lower()
        if all(tok in full_lower for tok in tokens_lower):
            return lyr, full_name
    return None, None


# -- Visibility helpers -------------------------------------------------

def all_vector_layer_ids():
    """Return list of IDs of all vector layers in the project."""
    return [
        lyr.id() for lyr in project.mapLayers().values()
        if lyr.type() == QgsMapLayerType.VectorLayer
    ]


def show_only_vector_layer(target_id):
    """Hide all vector layers; show only the one with the given ID.

    Other vector layers become invisible. The base raster layer is left
    untouched (only vector layers are toggled).
    """
    for lyr in project.mapLayers().values():
        if lyr.type() != QgsMapLayerType.VectorLayer:
            continue
        node = root.findLayer(lyr.id())
        if node is None:
            continue
        node.setItemVisibilityChecked(lyr.id() == target_id)


def restore_all_visibility(layer_ids):
    """Re-enable visibility on all given vector layer IDs (cleanup)."""
    for lid in layer_ids:
        node = root.findLayer(lid)
        if node is not None:
            node.setItemVisibilityChecked(True)


# -- Render barrier -----------------------------------------------------

def _wait_for_render(timeout_ms=15000):
    """Block until the canvas finishes its current render, up to timeout_ms."""
    loop = QEventLoop()
    finished = [False]

    def _on_render_done(_ok):
        if not finished[0]:
            finished[0] = True
            loop.quit()

    try:
        canvas.renderComplete.connect(_on_render_done)
    except (TypeError, RuntimeError):
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
    """Trigger a redraw and save the canvas.

    Does NOT change extent, zoom, or pan. The canvas is redrawn with the
    current visibility settings and the result is saved as PNG.
    """
    canvas.repaint()
    QApplication.processEvents()
    _wait_for_render()
    QApplication.processEvents()
    canvas.saveAsImage(out_path, None, "PNG")
    # Final settle so save's repaint events finish
    settle_loop = QEventLoop()
    QTimer.singleShot(100, settle_loop.quit)
    settle_loop.exec_()


# -- Main loop ----------------------------------------------------------

def main():
    # Snapshot the current extent so we can detect any unexpected change
    initial_extent = canvas.extent()

    print("=" * 70)
    print("Feature counts (GeoTIFF source: Google Satellite z19 download)")
    print("Base raster: merged_canvas0.5mpx_google_z19.tif (0.298 m/px)")
    print("=" * 70)
    print("WARNING: stop any background QGIS jobs (tile download, processing)")
    print("         before running this script.")
    print("=" * 70)

    # List vector layers in the project for diagnostics
    print("\nVector layers detected in project:")
    for lyr in project.mapLayers().values():
        if lyr.type() == QgsMapLayerType.VectorLayer:
            print("  -", repr(lyr.name()))
    print()

    saved_layer_ids = all_vector_layer_ids()
    results = []

    for tokens, filename, label in CASES:
        lyr, full_name = find_layer_by_patterns(tokens)
        if lyr is None:
            print(f"[SKIP] {label}: no layer matches ALL of {tokens}")
            continue
        # Sanity-check: confirm the matched layer contains all tokens
        full_lower = full_name.lower()
        if not all(tok.lower() in full_lower for tok in tokens):
            print(f"[SKIP] {label}: layer matched but name {full_name!r} unexpected")
            continue
        # Toggle visibility: hide all others, show this one
        show_only_vector_layer(lyr.id())
        out_path = os.path.join(IMGS_DIR, filename)
        try:
            trigger_redraw_and_capture(out_path)
        except Exception as exc:
            print(f"[ERROR] {label}: render failed: {exc}")
            restore_all_visibility(saved_layer_ids)
            canvas.refreshAllLayers()
            raise
        # Verify extent is unchanged
        if canvas.extent() != initial_extent:
            print(f"[WARN] {label}: canvas extent changed during capture")
        count = lyr.featureCount()
        size_kb = os.path.getsize(out_path) / 1024 if os.path.exists(out_path) else 0
        print(f"[OK] {label}")
        print(f"     layer:         {full_name}")
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
