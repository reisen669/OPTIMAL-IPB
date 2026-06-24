"""Export E1 CanopyRS Faster R-CNN+R50 to ONNX format.

STATUS: SKIPPED — Plan 06-02 determined E1 CanopyRS is BLOCKED.

Blocker details (from Plan 06-02 SUMMARY):
  - GitHub Releases (https://github.com/hugobaudchon/CanopyRS/releases):
    10 releases (2022-2023), each containing source code archives only.
    No .pth, .pt, .ckpt, or binary weight files were found.
  - Current CanopyRS requires:
      OS:     Linux (Ubuntu 22.04) — NOT Windows
      Python: 3.10 — project uses Python 3.12
      CUDA:   12.6 — project uses CPU
      SAM 3:  Meta's Segment Anything Model 3 (gated HuggingFace repo)
  - Result: E1 empirical testing is BLOCKED in Phase 6.

If weights become available, the export would follow this pattern
(based on torchvision Faster R-CNN):

    import torch
    from torchvision.models.detection import fasterrcnn_resnet50_fpn
    import os

    models_dir = os.path.dirname(os.path.abspath(__file__))
    ckpt_path = os.path.join(models_dir, "canopyrs_frcnn_r50.pth")
    onnx_path = os.path.join(models_dir, "canopyrs_frcnn_r50.onnx")

    # Load checkpoint first to inspect num_classes
    ckpt = torch.load(ckpt_path, map_location='cpu')
    if isinstance(ckpt, dict) and 'num_classes' in ckpt:
        num_classes = ckpt['num_classes']
    elif isinstance(ckpt, dict) and 'model_state_dict' in ckpt:
        num_classes = 91  # default COCO; adjust if inspection reveals different
    else:
        num_classes = 91

    model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=num_classes)
    if isinstance(ckpt, dict) and 'model_state_dict' in ckpt:
        model.load_state_dict(ckpt['model_state_dict'])
    else:
        model.load_state_dict(ckpt)
    model.eval()

    dummy_input = torch.randn(1, 3, 1024, 1024)
    torch.onnx.export(
        model, dummy_input, onnx_path,
        opset_version=13,
        input_names=['images'],
        output_names=['boxes', 'scores', 'labels'],
        dynamic_axes={
            'images': {0: 'batch', 2: 'height', 3: 'width'},
            'boxes': {0: 'num_detections'},
            'scores': {0: 'num_detections'},
            'labels': {0: 'num_detections'},
        }
    )

See models/inspect_e1_checkpoint.py for checkpoint inspection script.
See .planning/phases/06-.../06-02-SUMMARY.md for full blocker documentation.
"""

print("E1 ONNX EXPORT REPORT")
print("=====================")
print("Option A (Faster R-CNN+R50): SKIPPED — Plan 06-02 determined E1 is BLOCKED")
print("  Reason: No pretrained weights on GitHub Releases (source archives only)")
print("  Reason: canopyrs requires Linux/Python 3.10/CUDA 12.6 (incompatible with")
print("          Windows/Python 3.12/CPU environment)")
print("  Reason: Current CanopyRS depends on SAM 3 (gated HuggingFace)")
print("Option B (DINO+Swin-L): NOT ATTEMPTED (Option A gate not cleared)")
print("ONNX file created: N/A")
print("onnxruntime verification: N/A")
print("Export blocker: No .pth weights available; environment incompatible")
print("  (See 06-02-SUMMARY.md for full E1 CANOPYRS COMPATIBILITY REPORT)")
