"""Inspect E1 CanopyRS checkpoint structure.

STATUS: SKIPPED — Plan 06-02 determined E1 CanopyRS is BLOCKED.

Reason: GitHub Releases (10 releases, 2022-2023) contain source archives only —
no .pth, .pt, or .ckpt weight files. Current CanopyRS requires SAM 3 (Meta,
gated HuggingFace), Linux (Ubuntu 22.04), Python 3.10, CUDA 12.6. This project
runs Windows / Python 3.12 / CPU. E1 empirical testing skipped in Phase 6.

If weights become available in the future, this script would inspect their structure:

    import torch
    ckpt = torch.load(
        'models/canopyrs_frcnn_r50.pth',
        map_location='cpu'
    )
    print(f"Checkpoint type: {type(ckpt)}")
    if isinstance(ckpt, dict):
        print(f"Keys: {list(ckpt.keys())}")
        for k, v in ckpt.items():
            if hasattr(v, 'keys'):
                print(f"  {k}: dict with {len(v)} keys, first 5: {list(v.keys())[:5]}")
            elif isinstance(v, (int, float, str, bool)):
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: {type(v)}")
    else:
        print(f"Direct state_dict: {type(ckpt)}")

See: https://github.com/hugobaudchon/CanopyRS/releases
See: https://hugobaudchon.github.io/CanopyRS/getting-started/installation/
"""

print("E1 CanopyRS checkpoint inspector — SKIPPED")
print("Reason: No weights available (see Plan 06-02 SUMMARY for details)")
print("        canopyrs_frcnn_r50.pth does not exist")
print("")
print("E1 CANOPYRS COMPATIBILITY REPORT (from Plan 06-02):")
print("  Weight URL: BLOCKED — GitHub Releases contain source archives only")
print("  canopyrs package: NOT INSTALLABLE (requires Linux / Python 3.10 / CUDA 12.6)")
print("  Recommendation: BLOCKED — skip E1 in Phase 6")
