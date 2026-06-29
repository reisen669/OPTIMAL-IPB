"""
Convert Keras .h5 models to ONNX format using TensorFlow 2.3 and Keras 2.4.
This script is designed to run in the keras23_env conda environment.
"""
import os
import sys

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

import keras
import tf2onnx

def convert_h5_to_onnx(h5_path, onnx_path=None):
    """
    Convert a Keras .h5 model to ONNX format.

    Args:
        h5_path: Path to the .h5 model file
        onnx_path: Path to save the ONNX model (default: same name, .onnx extension)

    Returns:
        Path to the created ONNX file
    """
    if onnx_path is None:
        onnx_path = h5_path.replace('.h5', '.onnx')

    print(f"\nConverting: {os.path.basename(h5_path)}")
    print(f"Loading model from {h5_path}...")

    # Load the Keras model with custom objects from keras_retinanet
    from keras_retinanet.models import backbone
    custom_objects = backbone('resnet101').custom_objects

    model = keras.models.load_model(h5_path, custom_objects=custom_objects)
    print(f"Model loaded successfully. Input shape: {model.input_shape}")

    # Convert to ONNX
    print("Converting to ONNX...")
    onnx_model, external_tensor_storage = tf2onnx.convert.from_keras(model, opset=13)

    # Save ONNX model
    print(f"Saving ONNX model to {onnx_path}...")
    with open(onnx_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())

    # Verify file size
    h5_size = os.path.getsize(h5_path) / (1024 * 1024)  # MB
    onnx_size = os.path.getsize(onnx_path) / (1024 * 1024)  # MB
    print(f"[+] Conversion complete!")
    print(f"  Input size:  {h5_size:.1f} MB")
    print(f"  Output size: {onnx_size:.1f} MB")

    return onnx_path

def main():
    """Convert all .h5 models in the models directory to ONNX format."""
    base_dir = r'C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb'
    models_dir = os.path.join(base_dir, 'models')

    # List of .h5 models to convert
    h5_models = [
        'Geoeye-Resnet101.h5',
        'Pleiades-Resnet101.h5'
    ]

    print("=" * 60)
    print("OPTIMAL-IPB Model Converter: .h5 to ONNX")
    print("Using TensorFlow 2.3 + Keras 2.4")
    print("=" * 60)

    converted = []
    skipped = []

    for h5_file in h5_models:
        h5_path = os.path.join(models_dir, h5_file)

        if not os.path.exists(h5_path):
            print(f"\n[!] Model not found: {h5_file}")
            skipped.append(h5_file)
            continue

        onnx_file = h5_file.replace('.h5', '.onnx')
        onnx_path = os.path.join(models_dir, onnx_file)

        if os.path.exists(onnx_path):
            print(f"\n[+] ONNX already exists: {onnx_file}")
            converted.append(onnx_file)
            continue

        try:
            result = convert_h5_to_onnx(h5_path, onnx_path)
            converted.append(os.path.basename(result))
        except Exception as e:
            print(f"\n[X] Error converting {h5_file}: {e}")
            import traceback
            traceback.print_exc()
            skipped.append(h5_file)

    print("\n" + "=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"Successfully converted: {len(converted)}")
    for f in converted:
        print(f"  [+] {f}")

    if skipped:
        print(f"\nSkipped/Failed: {len(skipped)}")
        for f in skipped:
            print(f"  [X] {f}")

    print("=" * 60)

if __name__ == '__main__':
    main()
