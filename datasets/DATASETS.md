# Datasets Used

## Overview

This project utilizes multiple publicly available datasets for training, fine-tuning, validation, and evaluation of deepfake detection models across image, video, and audio modalities.

The objective is to improve robustness against modern AI-generated manipulations by leveraging diverse datasets and real-world media samples.

The project includes:

* Image Deepfake Detection
* Video Deepfake Detection
* Audio Deepfake Detection
* Multimodal Deepfake Analysis

To enhance generalization and real-world performance, additional real-world videos collected from YouTube were incorporated during retraining and evaluation.

---

# Video Deepfake Detection Datasets

## 1. FaceForensics++ (FF++)

**Dataset Link**

https://www.kaggle.com/datasets/xdxd003/ff-c23

### Description

FaceForensics++ is one of the most widely used benchmark datasets for deepfake detection research. It contains real and manipulated videos generated using multiple face manipulation techniques.

### Key Features

* Real and manipulated face videos
* High-quality compressed videos (C23)
* Diverse facial expressions and head poses
* Large-scale benchmark dataset
* Widely adopted in academic research

### Usage in This Project

* Primary dataset for video model training
* Frame-level deepfake classification
* Video-level inference evaluation
* Suspicious frame selection experiments

---

## 2. LAV-DF (Localized Audio-Visual DeepFake Dataset)

**Dataset Link**

https://www.kaggle.com/datasets/elin75/localized-audio-visual-deepfake-dataset-lav-df

### Description

LAV-DF is a large-scale multimodal deepfake dataset containing realistic manipulations across both visual and audio streams.

### Key Features

* Audio-visual deepfake samples
* Real-world manipulation scenarios
* Localized manipulation annotations
* Challenging benchmark for multimodal systems

### Usage in This Project

* Video model retraining and fine-tuning
* Improving robustness against unseen manipulations
* Enhancing real-world generalization
* Multimodal evaluation experiments

---

## 3. Real-World Video Collection

**Source**

Publicly Available YouTube Videos

### Description

Approximately 100 real-world videos were collected from YouTube to improve model robustness against real deployment scenarios.

### Purpose

* Reduce dataset bias
* Improve generalization capability
* Increase diversity of environments and lighting conditions
* Improve performance on unseen videos

### Usage in This Project

* Validation and testing
* Real-world robustness evaluation
* Model calibration and fine-tuning

---

# Audio Deepfake Detection Dataset

## ASVspoof 2019 Logical Access (LA)

**Dataset Link**

https://www.kaggle.com/datasets/awsaf49/asvpoof-2019-dataset

### Description

ASVspoof 2019 is a benchmark dataset specifically designed for synthetic speech and voice spoofing detection.

### Key Features

* Genuine human speech recordings
* AI-generated speech samples
* Voice conversion attacks
* Text-to-speech generated audio
* Industry-standard benchmark dataset

### Usage in This Project

* Training the CNN-based audio detector
* Synthetic speech detection
* Voice cloning detection
* Audio spoofing analysis

---

# Image Deepfake Detection Dataset

## 140K Real and Fake Faces Dataset

**Dataset Link**

https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces

### Description

This dataset contains a large collection of real and AI-generated face images suitable for binary image-level deepfake detection.

### Key Features

* 140,000+ facial images
* Real and synthetic samples
* Balanced dataset
* High-quality face images
* Suitable for deep learning-based classification

### Usage in This Project

* Training the image deepfake detector
* Feature extraction experiments
* Visual forensic analysis
* Supporting multimodal detection workflows

---

# Dataset Summary

| Modality              | Dataset                  |
| --------------------- | ------------------------ |
| Video                 | FaceForensics++ (FF++)   |
| Video Retraining      | LAV-DF                   |
| Real-World Validation | 100 YouTube Videos       |
| Audio                 | ASVspoof 2019 (LA)       |
| Image                 | 140K Real and Fake Faces |

---

# Dataset Availability

The datasets are not included in this repository due to:

* Large storage requirements
* Licensing restrictions
* Redistribution limitations

Please download the datasets directly from their official sources using the links provided above.

---

# Ethical Considerations

This project is intended solely for:

* Academic research
* Educational purposes
* Deepfake detection studies
* Multimedia forensics research

All datasets remain the property of their respective creators.

Users must comply with the original dataset licenses, usage policies, and distribution terms before downloading or using any dataset.

---

# Citation

If you use this project or any of the referenced datasets in academic work, please cite the original dataset authors and creators appropriately.
