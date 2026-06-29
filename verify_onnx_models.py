"""Verify all ONNX models in models/ load correctly with onnxruntime."""
import onnxruntime as ort
import os

models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
onnx_files = sorted(f for f in os.listdir(models_dir) if f.endswith('.onnx'))

print(f"Models directory: {models_dir}")
print(f"ONNX files found: {onnx_files}\n")

all_ok = True
for fname in onnx_files:
    path = os.path.join(models_dir, fname)
    size_mb = os.path.getsize(path) / 1024 / 1024
    try:
        sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
        inputs  = [i.name for i in sess.get_inputs()]
        outputs = [o.name for o in sess.get_outputs()]
        print(f"  [OK]  {fname} ({size_mb:.0f} MB)")
        print(f"        inputs={inputs}")
        print(f"        outputs={outputs}")
    except Exception as e:
        print(f"  [FAIL] {fname} ({size_mb:.0f} MB): {e}")
        all_ok = False

print()
if all_ok:
    print(f"All {len(onnx_files)} ONNX models verified successfully.")
else:
    print("Some models failed verification.")
