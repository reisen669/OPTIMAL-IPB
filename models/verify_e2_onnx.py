"""Quick verification that E2 ONNX model loads with onnxruntime."""
import onnxruntime as ort
import os

models_dir = os.path.dirname(os.path.abspath(__file__))
onnx_path = os.path.join(models_dir, "VHRTrees_yolov8m.onnx")

sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
inputs = [i.name for i in sess.get_inputs()]
outputs = [o.name for o in sess.get_outputs()]
print(f"  [OK]  models/VHRTrees_yolov8m.onnx ({os.path.getsize(onnx_path)/1024/1024:.0f} MB)")
print(f"        inputs={inputs}")
print(f"        outputs={outputs}")

# Print full input/output shape information
for inp in sess.get_inputs():
    print(f"        input '{inp.name}': shape={inp.shape}, dtype={inp.type}")
for out in sess.get_outputs():
    print(f"        output '{out.name}': shape={out.shape}, dtype={out.type}")
