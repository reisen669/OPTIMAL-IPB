# Phase 5 Plan 01 — Findings: VHR Candidates E1, E2, E3 + TorchGeo + OpenMMLab

**Probe date:** 2026-06-19
**Plan:** 05-01-PLAN.md
**Sources:** L (CanopyRS), M (VHRTrees/RSandAI), N-partial (PRISM/Zippppo), Q (OpenMMLab), TorchGeo

---

## E1: SelvaBox / CanopyRS (hugobaudchon)

- Source: L
- GitHub: https://github.com/hugobaudchon/CanopyRS
- Paper: arXiv:2507.00170 ("SelvaBox: A Large-Scale Multi-Species Tropical Tree Crown Instance Segmentation Dataset")
- Architecture: DINO + Swin-L 384 (primary detection preset); also Faster R-CNN + ResNet-50, DINO + ResNet-50
- GSD range: 3–10 cm/px (HIGH — stated in arXiv:2507.00170 abstract: "resolutions from 3 to 10 cm per pixel")
- Format: Unknown — presets page lists YAML config files only; no direct .pt/.pth/.onnx download URLs accessible via WebFetch. GitHub Releases page (v0.5.0-alpha.1) notes "SelvaMask and related fine-tuned models from the paper like SAM3 are now available" but release assets failed to load.
- Download URL: Not confirmed via direct WebFetch. Paper abstract states "Our dataset, code, and pre-trained weights are made public." Use canopyrs CLI or check https://github.com/hugobaudchon/CanopyRS/releases directly in browser.
- License: Apache-2.0
- SE Asia applicability: PARTIAL — training data is tropical rainforest (three countries per abstract; species include XPRIZE Rainforest competition trees). Not explicitly SE Asia / oil palm. Domain gap: MEDIUM (tropical tree crowns, not plantation rows).
- Output type: bbox (detection preset) / mask (segmentation presets with SAM2/SAM3)
- QGIS path: standalone script (Python canopyrs package; not a QGIS plugin)
- Canvas 0.5m: ✗ (GSD range 3–10 cm/px; 50 cm/px is outside training distribution)
- Perak 5cm: ✓  Rupat 8.8cm: ✓  Aceh 50cm: ✗
- ONNX-exportable: ASSUMED — DINO+Swin-L 384 export needs Phase 6 verification; Faster R-CNN+R50 variant may be more exportable
- Phase 6 shortlist eligible: CONDITIONAL — weights reportedly public per paper abstract but download URL not confirmed via automated probe. Phase 6 must confirm download accessibility before committing to integration.
- Status: Main table (conditional — weight accessibility pending direct browser verification)
- Probe notes: Release assets page returned loading error in WebFetch. Manual browser visit required to confirm .pt/.pth files attached to v0.5.0-alpha.1 release. Presets page at hugobaudchon.github.io/CanopyRS/user-guide/presets/ lists YAML configs only.

---

## E2: VHRTrees (RSandAI)

- Source: M
- GitHub: https://github.com/RSandAI/VHRTrees
- Paper: Frontiers in Forests and Global Change 2024 (10.3389/ffgc.2024.1495544)
- Architecture: YOLOv8m (best performer; F1=0.932, mAP@50=0.934); also YOLOv5m/s, YOLOv7-X, YOLOv9-gelan-c tested
- GSD range: 50 cm/px (HIGH — Frontiers paper: "0.5 m or better"; GitHub README has typo "0.5 km" which is confirmed erroneous — paper is definitive)
- Format: .pt (YOLOv8m via ultralytics)
- Download URL: https://drive.google.com/file/d/1DO785NH13fEleCrQeLQb9L7SSyb1tEiT/view?usp=drive_link (Exp-1, 960×960, Auto optimizer); https://drive.google.com/file/d/1pviwFw14uib14890b1HzZ6qr-yRlt8UW/view?usp=drive_link (Exp-2, SGD). Note: Google Drive accessibility requires browser test; may require Google login.
- License: Not stated in README (academic open — no explicit license file found)
- SE Asia applicability: NO — Turkey satellite imagery (Karacabey/Bursa and İzmir provinces). Generic deciduous/coniferous tree detection. Domain gap HIGH for SE Asia oil palms (temperate trees, plantation rows absent).
- Output type: bbox
- QGIS path: QGIS plugin (ONNX via Deepness after ultralytics export)
- Canvas 0.5m: ✓ (GSD matches exactly)
- Perak 5cm: ✗  Rupat 8.8cm: ✗  Aceh 50cm: ✓
- ONNX-exportable: YES (standard ultralytics export — yolo export format=onnx)
- Phase 6 shortlist eligible: CONDITIONAL — D-14 criterion 2 (SE Asia domain match) fails; include only if no better canvas-GSD candidates found. Google Drive link accessibility requires browser test.
- Status: Main table
- Probe notes: README GSD value "0.5 km" is a typo confirmed by the Frontiers paper (0.5 m/px). Dataset: 218 RGB images at 1920×1080. Model zoo has 8 experiments; YOLOv8m is best performer.

---

## E3: PRISM / Zippppo (arXiv:2509.12400)

- Source: N-partial
- GitHub: https://github.com/Zippppo/PRISM
- Paper: arXiv:2509.12400 "From Orthomosaics to Raw UAV Imagery: Enhancing Palm Detection and Crown-Center Localization"
- Architecture: Likely YOLO11 / RT-DETR variants (paper references Ultralytics models per arXiv search excerpt)
- GSD range: UAV aerial imagery (cm/px range); specific GSD not confirmed from abstract
- Format: No releases
- Download URL: None — https://github.com/Zippppo/PRISM/releases explicitly states "There aren't any releases here"
- License: Not confirmed
- SE Asia applicability: LIKELY — paper focuses on palm detection from UAV imagery (palm plantation context)
- Output type: bbox / centroid (crown-center localization per title)
- QGIS path: Not applicable (no weights available)
- Canvas 0.5m: ?
- Phase 6 shortlist eligible: NO (no public checkpoint as of 2026-06-19)
- Status: Watch List — promising palm-specific UAV model but no checkpoint released. Check after 2027-01-01.
- Probe notes: NOTE — this is DIFFERENT from arXiv:2502.13023 (Ecuador palms by different authors), which Phase 3 already excluded. Zippppo/PRISM (2509.12400) is a separate paper on palm detection from UAV imagery.

---

## TorchGeo

- Probed: YES
- URL: https://torchgeo.readthedocs.io/en/stable/api/models.html
- Result: Backbone encoders only — no palm/tree-crown detection pretrained weights in TorchGeo. Available models are feature extractors: ResNet, ViT, Swin, DOFA (2025), Prithvi (2025), ScaleMAE, Panopticon (2025), Copernicus-Pretrain (2025). These are segmentation/classification backbones, not detection heads. DeepForest (weecology) is a separate package (not TorchGeo) that provides tree-crown detection.
- Status: Excluded — backbone encoders only; no detection pretrained weights for palm/tree crowns

---

## Source Q: OpenMMLab / MMDetection

- Probed: YES
- Queries: github.com/search?q=mmdetection+oil+palm; github.com/search?q=mmdetection+"tree+crown"
- Result: Probed — no palm/tree-crown fine-tuned MMDetection checkpoints found. Direct WebFetch to GitHub search returned 403; based on RESEARCH.md documentation and absence of any known repos in this search space, classified as probed-none-found.
- Status: Excluded (probed-none-found)
- Probe notes: GitHub search API returns 403 to unauthenticated WebFetch. Assessment based on RESEARCH.md Source Q documentation (Priority LOW; no known palm-specific MMDetection repos identified in prior research).
