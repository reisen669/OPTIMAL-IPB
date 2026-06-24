"""Export E2 VHRTrees YOLOv8m .pt to ONNX format.

NOTE: The VHRTrees_yolov8m.pt file should be the fine-tuned weights from:
  https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view
  (RSandAI/VHRTrees — YOLOv8m Exp-1 weights, trained on Turkey 0.5m/px tree imagery)

If the above Google Drive link is inaccessible (requires Google login), the base
YOLOv8m COCO weights are used as a functional substitute to validate the ONNX
export pipeline. Results will show generic COCO object detection, not VHRTrees
fine-tuned tree detection.

Usage:
    python export_e2_onnx.py
"""
from ultralytics import YOLO
import os

models_dir = os.path.dirname(os.path.abspath(__file__))
pt_path = os.path.join(models_dir, "VHRTrees_yolov8m.pt")
onnx_path = os.path.join(models_dir, "VHRTrees_yolov8m.onnx")

if not os.path.exists(pt_path):
    raise FileNotFoundError(
        f"Model weights not found: {pt_path}\n"
        "Download from: https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view\n"
        "Or run: python -c \"from ultralytics import YOLO; YOLO('yolov8m.pt')\" to download base weights."
    )

print(f"Loading model: {pt_path}")
model = YOLO(pt_path)
print(f"Exporting to ONNX (opset=13)...")
model.export(format="onnx", opset=13)

# ultralytics exports to the same directory as the .pt file with .onnx extension
# Check both the models dir and current dir
if not os.path.exists(onnx_path):
    # Sometimes exported to current working dir
    cwd_onnx = os.path.join(os.getcwd(), "VHRTrees_yolov8m.onnx")
    if os.path.exists(cwd_onnx):
        import shutil
        shutil.move(cwd_onnx, onnx_path)
        print(f"Moved ONNX from {cwd_onnx} to {onnx_path}")

assert os.path.exists(onnx_path), f"ONNX export failed: {onnx_path} not created"
size_mb = os.path.getsize(onnx_path) / 1024 / 1024
print(f"ONNX export successful: {onnx_path} ({size_mb:.0f} MB)")
