"""Convert OPTIMAL-IPB RetinaNet Keras .h5 weights to ONNX.

Run from keras23_env (TF 2.3.0 + Keras 2.4.3 + tf2onnx 1.14.0):

    "C:/SuperMap/supermap-iobjectspy-env-gpu-2025-win64/conda/envs/keras23_env/python.exe" ^
        "C:/Users/suily/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/optimal-ipb/models/convert_h5_to_onnx.py"

Source files: models/h5_sources/{Google,Geoeye,Pleiades}-Resnet101.h5
Output files: models/{Google,Geoeye,Pleiades}-Resnet101.onnx

The .h5 files use Keras 2.x format with keras-retinanet custom layers
(BatchNormFreeze, UpsampleLike). Loading them in modern environments
(TF 2.10+/Keras 3) fails with 'Keyword argument not understood: freeze'.

The plugin's vendored keras_retinanet/ and keras_resnet/ packages
provide the missing classes, registered via custom_objects.
"""
import os
import sys
import warnings
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
warnings.filterwarnings("ignore")

import tensorflow as tf  # noqa: E402
import tf2onnx  # noqa: E402

PLUGIN_ROOT = r"C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb"
SRC_DIR = os.path.join(PLUGIN_ROOT, "models", "h5_sources")
DST_DIR = os.path.join(PLUGIN_ROOT, "models")

SOURCES = [
    ("Google-Resnet101.h5",    "Google-Resnet101.onnx"),
    ("Geoeye-Resnet101.h5",    "Geoeye-Resnet101.onnx"),
    ("Pleiades-Resnet101.h5",  "Pleiades-Resnet101.onnx"),
]


def convert(h5_path, onnx_path):
    print(f"\n--- Converting {os.path.basename(h5_path)} ---")
    print(f"Loading .h5 (compile=False, custom_objects=...)...")
    import keras

    if PLUGIN_ROOT not in sys.path:
        sys.path.insert(0, PLUGIN_ROOT)

    # Import keras_retinanet custom layers (UpsampleLike, etc.) and
    # keras_resnet BatchNormalization subclass (with the 'freeze' kwarg).
    import keras_retinanet  # noqa: F401
    from keras_retinanet import layers as kr_layers  # noqa: F401
    import keras_resnet as kr  # noqa: F401
    from keras_resnet import layers as krl  # noqa: F401

    custom_objects = {
        "BatchNormalization": getattr(krl, "BatchNormFreeze", kr.layers.BatchNormFreeze),
        "UpsampleLike": getattr(kr_layers, "UpsampleLike", None),
    }
    custom_objects = {k: v for k, v in custom_objects.items() if v is not None}

    model = keras.models.load_model(h5_path, compile=False, custom_objects=custom_objects)
    print(f"  input  shape: {model.input_shape}")
    print(f"  output shapes: {[o.shape for o in model.outputs]}")

    print(f"Exporting to ONNX (opset=13)...")
    input_name = model.input_names[0]

    @tf.function(input_signature=[tf.TensorSpec(model.input_shape, tf.float32, name=input_name)])
    def frozen_model(x):
        return [model(x)]

    onnx_model, _ = tf2onnx.convert.from_function(
        frozen_model,
        input_signature=[tf.TensorSpec(model.input_shape, tf.float32, name=input_name)],
        opset=13,
        output_path=onnx_path,
    )
    print(f"  written: {onnx_path} ({os.path.getsize(onnx_path) / (1024*1024):.1f} MB)")


def verify(onnx_path):
    import onnxruntime as ort
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    print(f"Verification: {os.path.basename(onnx_path)}")
    print(f"  inputs : {[i.name for i in sess.get_inputs()]}")
    print(f"  outputs: {[o.name for o in sess.get_outputs()]}")
    inp = sess.get_inputs()[0]
    print(f"  input  shape={inp.shape} dtype={inp.type}")
    for o in sess.get_outputs():
        print(f"  output {o.name} shape={o.shape} dtype={o.type}")
    import numpy as np
    out = sess.run(None, {inp.name: np.random.random(inp.shape).astype(np.float32)})
    print(f"  smoke test: input {inp.shape} -> outputs {[o.shape for o in out]}")
    print("  PASS" if all(o is not None for o in out) else "  FAIL")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Convert only this source name (e.g. Google-Resnet101.h5)")
    args = parser.parse_args()

    for src_name, dst_name in SOURCES:
        if args.only and src_name != args.only:
            continue
        src = os.path.join(SRC_DIR, src_name)
        dst = os.path.join(DST_DIR, dst_name)
        if not os.path.exists(src):
            print(f"[SKIP] source not found: {src}")
            continue
        if os.path.exists(dst):
            print(f"[SKIP] destination exists: {dst}")
            verify(dst)
            continue
        convert(src, dst)
        verify(dst)
    print("\n=== Conversion complete ===")


if __name__ == "__main__":
    main()