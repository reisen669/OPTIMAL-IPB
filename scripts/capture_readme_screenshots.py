"""Capture three QGIS canvas screenshots + feature counts for README.

Run from: Plugins → Python Console → Editor tab → paste + Run

Assumes QGIS is already zoomed to the target area and the base raster
"merged_canvas0.5mpx_google_z19_clean" is loaded as the bottom layer.
"""
import os
import subprocess
from qgis.core import (
    QgsProject,
    QgsMapLayerType,
    QgsExpression,
    QgsFeatureRequest,
)
from qgis.utils import iface

PLUGIN_ROOT = r"C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb"
IMGS_DIR = os.path.join(PLUGIN_ROOT, "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

# Three cases: (output_layer_name, case_filename, case_label)
CASES = [
    ("0.30mpx_z19_GeoEye_mAP0.50_(pt)", "case1_geoeye_30mpx_z19.png", "GeoEye-Resnet101 (mAP@0.5=0.50)"),
    ("0.30mpx_z19_googleresnet_mAP0.30_(pt)", "case2_googleresnet_30mpx_z19.png", "Google-Resnet101 (mAP@0.5=0.30)"),
    ("0.30mpx_z19_Pleiaedes_mAP0.20_(pt)", "case3_pleiades_30mpx_z19.png", "Pléiades-Resnet101 (mAP@0.5=0.20)"),
]

project = QgsProject.instance()
root = project.layerTreeRoot()

# Hide ALL vector layers first, then enable only one per case
def set_only_visible(layer_name):
    """Hide all vector layers; show only the named one (if loaded)."""
    target_id = None
    for lyr in project.mapLayers().values():
        if lyr.type() == QgsMapLayerType.VectorLayer:
            node = root.findLayer(lyr.id())
            if node:
                if lyr.name() == layer_name:
                    node.setItemVisibilityChecked(True)
                    target_id = lyr.id()
                else:
                    node.setItemVisibilityChecked(False)
    return target_id

print("=" * 70)
print("Feature counts (GeoTIFF source: Google Satellite z19 download)")
print("Base raster: merged_canvas0.5mpx_google_z19.tif (0.298 m/px)")
print("=" * 70)

results = []
for layer_name, filename, label in CASES:
    target_id = set_only_visible(layer_name)
    if not target_id:
        print(f"[SKIP] {label}: layer '{layer_name}' not found in project")
        continue
    lyr = project.mapLayer(target_id)
    count = lyr.featureCount()
    out_path = os.path.join(IMGS_DIR, filename)
    # Use iface to capture the canvas
    canvas = iface.mapCanvas()
    canvas.refreshAllLayers()
    canvas.saveAsImage(out_path)
    print(f"[OK] {label}")
    print(f"     layer: {layer_name}")
    print(f"     feature count: {count}")
    print(f"     screenshot: {out_path}")
    results.append((label, count, filename))

# Restore all vector layer visibility to True (cleanup)
for lyr in project.mapLayers().values():
    if lyr.type() == QgsMapLayerType.VectorLayer:
        node = root.findLayer(lyr.id())
        if node:
            node.setItemVisibilityChecked(True)

print("=" * 70)
print("Summary table for README:")
print("=" * 70)
for label, count, filename in results:
    print(f"| {label} | feature count: {count} | {filename} |")
print()
print("All layer detections source: GeoTIFF downloaded from Google Satellite z19")
print("Screenshots saved to:", IMGS_DIR)
