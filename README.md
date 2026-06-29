# OPTIMAL-IPB

OPTIMAL-IPB (Oil Palm Trees Identification based on Machine Learning – IPB University) is an open access plugin in Quantum GIS software used to detect oil palm trees canopy on high-resolution satellite images. This plugin was developed based on deep learning models on Retinanet architecture implemented on the repository by [Fizyr](https://github.com/fizyr/keras-retinanet). Some modifications were applied to enhance the model’s accuracy in detecting oil palm trees canopy as small objects. OPTIMAL_IPB was built by researchers from the [Center for Regional System, Analysis, Planning and Development (P4W/CRESTPENT)](https://p4w.ipb.ac.id), IPB University, Indonesia. It was based on research funded by RISPRO program held by the [Indonesia Endowment Fund for Education (LPDP)](https://lpdp.kemenkeu.go.id/) – the Ministry of Finance.

## Installation Steps

:warning: This plugin was developed in python 3.7 environment contained in QGIS version 3.10 A Coruña, and works with keras version 2.4.3 and tensorflow version 2.3.0.

### 1. Package Required

Some packages need to be installed in the QGIS environment first. There are two ways to install packages in the QGIS environment.

#### - Package installation via python console in QGIS

Open python console in QGIS and run `import pip` then `pip.main(['install', '-q', '--disable-pip-version-check', 'scipy==1.4.1', 'cython', 'keras-resnet', 'opencv-python', 'pillow', 'progressbar2', 'tensorflow==2.3.0', 'keras==2.4.3', 'numpy==1.18.5', 'protobuf==3.15.8'])` to install all the prerequisites.

#### - Module installation via OSGeo4W Shell

Open OSGeo4W Shell then run this command `pip install scipy==1.4.1 cython keras-resnet opencv-python pillow progressbar2 tensorflow==2.3.0 keras==2.4.3 numpy==1.18.5 protobuf==3.15.8`

### 2. GPU Configuration (Optional)
This plugin is built using tensorflow as a machine learning framework. For faster process, it is highly recommended to use a GPU. You can find complete instructions for GPU Support through [this link](https://www.tensorflow.org/install/gpu#software_requirements).

For Windows user, we need to add the CUDA®, CUPTI, and cuDNN installation directories to the %PATH% environmental variable on QGIS. Click `Settings > Options`, on the System Tab choose `Environment` then check `Use custom variables (restart required - include separators)`.

Click Plus (+) button, then add configuration bellow:

- `Apply: Prepend`
- `Variable: PATH`
- `Value: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\bin;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\extras\CUPTI\lib64;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\include;`

### 3. Plugin Installation
There are two ways to install this plugin.
1. From official QGIS Plugin Repository - Use the QGIS Plugins menu to install the OPTIMAL-IPB Plugin (see [QGIS manual](http://docs.qgis.org/latest/en/docs/user_manual/plugins/plugins.html)).
2. From [Zipfile](https://github.com/p4wlppmipb/OPTIMAL-IPB/archive/master.zip) of this repository. Then follow this [instruction](http://docs.qgis.org/latest/en/docs/user_manual/plugins/plugins.html#the-install-from-zip-tab).

### 4. Pick a Model

There are three models that have been trained using Backbone Resnet101. You can download the three models in the table below:
| Satellite Imagery Paltform  | mAP@0.5 | Model (inference) |
| --------------------------- | ------- | -------------------- |
| Pleiades Satellite Imagery  | 0.903   | [Pleiades-Resnet101.h5](https://github.com/p4wlppmipb/OPTIMAL-IPB/releases/download/0.1/Pleiades-Resnet101.h5) |
| Geoeye Satellite Imagery    | 0.900   | [Geoeye-Resnet101.h5](https://github.com/p4wlppmipb/OPTIMAL-IPB/releases/download/0.1/Geoeye-Resnet101.h5)     |
| Google Satellite Imagery    | 0.925   | [Google-Resnet101.h5](https://github.com/p4wlppmipb/OPTIMAL-IPB/releases/download/0.1/Google-Resnet101.h5)     |

Copy all models you downloads to your plugin directory. Eg: `C:\Users\Username\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\models`.

## Usage

This plugin can be accessed under Plugins menu, then select `Calculate > OPTIMAL-IPB` or in the Processing Toolbox, then select `OPTIMAL-IPB > OPTIMAL-IPB` as shown in the image below:

<img src='imgs/Readme01.png'>

Afterward you can input your raster layer then select model previously downloaded. You can change the default value of mean Average Precision (mAP) during the detection process. Select output type from three types of output that can be generated namely point, bounding-box and canopy circle. Then select your output layer to save, then click `run`:

<img src='imgs/Readme02.png'>

:warning: Update: Now score attribute available on output for each object

## Performance on 0.30 m/px (Google z19) merged canvas

The three RetinaNet models were tested on `sample_data_qgis/output_canvas0.5mpx_google_z19/merged_canvas0.5mpx_google_z19.tif` (GSD = 0.298 m/px, 70 tiles merged, 100% quality). Results below are ranked by mAP@0.5 on this test raster.

### Best performance (in order)

| Rank | Model | mAP@0.5 | Detection output layer | Base raster |
|------|-------|---------|------------------------|-------------|
| 1 | **Geoeye-Resnet101** | **0.50** | `0.30mpx_z19_GeoEye_mAP0.50_(pt).gpkg` | `merged_canvas0.5mpx_google_z19_clean.tif` |
| 2 | **Google-Resnet101** | **0.30** | `0.30mpx_z19_googleresnet_mAP0.30_(pt).gpkg` | `merged_canvas0.5mpx_google_z19_clean.tif` |
| 3 | **Pleiades-Resnet101** | **0.20** | `0.30mpx_z19_Pleiaedes_mAP0.20_(pt).gpkg` | `merged_canvas0.5mpx_google_z19_clean.tif` |

### Case 1 — GeoEye-Resnet101 (mAP@0.5 = 0.50)

<img src='imgs/case1_geoeye_30mpx_z19.png' alt='0.30mpx z19 — GeoEye-Resnet101 mAP@0.5'>

*Overlay layers: `0.30mpx_z19_GeoEye_mAP0.50_(pt)` over base `merged_canvas0.5mpx_google_z19_clean`*

### Case 2 — Google-Resnet101 (mAP@0.5 = 0.30)

<img src='imgs/case2_googleresnet_30mpx_z19.png' alt='0.30mpx z19 — Google-Resnet101 mAP@0.5'>

*Overlay layers: `0.30mpx_z19_googleresnet_mAP0.30_(pt)` over base `merged_canvas0.5mpx_google_z19_clean`*

### Case 3 — Pléiades-Resnet101 (mAP@0.5 = 0.20)

<img src='imgs/case3_pleiades_30mpx_z19.png' alt='0.30mpx z19 — Pléiades-Resnet101 mAP@0.5'>

*Overlay layers: `0.30mpx_z19_Pleiaedes_mAP0.20_(pt)` over base `merged_canvas0.5mpx_google_z19_clean`*

### Combined results — all models

| Model | Architecture | GSD tier | mAP@0.5 (0.30 m/px z19) | Notes |
|-------|--------------|----------|------------------------|-------|
| **Geoeye-Resnet101** | RetinaNet, ResNet-101 | ~50 cm/px | **0.50** | Best on z19 — GeoEye satellite training domain matches 30 cm Google imagery characteristics |
| **Google-Resnet101** | RetinaNet, ResNet-101 | ~50 cm/px | **0.30** | Mid-tier — trained on Google imagery but lower mAP on this specific tile |
| **Pleiades-Resnet101** | RetinaNet, ResNet-101 | ~50 cm/px | **0.20** | Lowest — Pléiades 50 cm commercial imagery has different texture/spectral response than Google tiles |
| `tribber93_yolov11_palm.onnx` | YOLOv11 | 5–15 cm/px | _not tested on 0.30 m/px (GSD too coarse for VHR-trained model)_ | GSD mismatch — model expects VHR UAV imagery |
| `tree_tops_yolov9.onnx` | YOLOv9 | 10 cm/px | _not tested on 0.30 m/px (GSD too coarse for VHR-trained model)_ | Generic tree crowns, not palm-specific |
| `mopad/MOPAD_epoch_24.onnx` | Faster R-CNN+ResNet-101+RPF | 5–10 cm/px | _not tested on 0.30 m/px (GSD too coarse for VHR-trained model)_ | SE Asia oil palm UAV — out of GSD range |

> **Takeaway:** The three medium-resolution (50 cm/px) RetinaNet models are usable on 0.30 m/px (z19) imagery, but mAP drops significantly from the original training mAP (~0.90) to a 0.20–0.50 range. For higher-accuracy counting, VHR (≤15 cm/px) imagery with a VHR-trained model is required.

> **Note on feature counts and screenshots:** Feature counts and per-case feature counts are pending — populate the rows above with `featureCount(<output_layer>)` results from QGIS Python Console, and replace `imgs/case*.png` placeholders with saved QGIS canvas screenshots (Project → Import/Export → Export Map to Image).

## Sources

1) [fizyr/keras-retinanet](https://github.com/fizyr/keras-retinanet)
2) [Martin Zlocha](https://github.com/martinzlocha/anchor-optimization)
3) [(Faster) Non-Maximum Suppression in Python](https://pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/) by Adrian Rosebrock
4) [Sliding Windows for Object Detection with Python and OpenCV](https://pyimagesearch.com/2015/03/23/sliding-windows-for-object-detection-with-python-and-opencv/) by Adrian Rosebrock
5) Update: [Large Scale Non maximum Suppression (LSNMS)](https://github.com/remydubois/lsnms) by Rémy Dubois

## For developers

If you have any idea or trouble, please [post an Issue](https://github.com/p4wlppmipb/OPTIMAL-IPB/issues) first.

We very much welcome contributions from all developers out there. This project is a community-driven open-source tool - please help us to make it better.


## License

OPTIMAL-IPB is a free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

Intellectual property rights (IPR): [EC00202227184](https://e-hakcipta.dgip.go.id/index.php/c?code=OTk2Njg4MGQ5MmFlNGYzMjljNDA5M2JmNGUxOTg0YjAK), 22 April 2022

<em>Copyright © 2018-2022 Didit Okta Pribadi, Ernan Rustiadi, La Ode Syamsul Iman, Muhammad Nurdin. @ [P4W/CRESTPENT](https://p4w.ipb.ac.id)-LPPM, IPB University</em>
