# Download Pretrained Models

## Overview

The pretrained model weights are not included in this repository due to GitHub file size limitations.

Before running the project, download all required model files and place them inside the appropriate directory.

---

# Download Link

## Google Drive

https://drive.google.com/drive/folders/1pGb1YGdUbdDwlWopSoyIslvHqajbQMxB?usp=sharing

---

# Required Directory Structure

Place all downloaded files inside:

```text
backend/models/weights/
```

Expected structure:

```text
backend/
└── models/
    └── weights/
        ├── improved_video_model.pth
        ├── best_audio_model.keras
        ├── audio_feature_extractor.keras
        ├── svm_efficientnet_b4.pkl
        ├── pca_efficientnet_b4.pkl
        ├── deep_scaler.pkl
        ├── land_scaler.pkl
        └── shape_predictor_68_face_landmarks.dat
```

---

# Model Descriptions

## 1. improved_video_model.pth

### Purpose

Video Deepfake Detection

### Architecture

* ResNeXt101 Backbone
* Face-Based Frame Analysis
* Suspicious Frame Detection
* Video-Level Aggregation

### Used By

```text
VideoRunner
```

### Output

* Frame Probabilities
* Video Score
* Deepfake Prediction

---

## 2. best_audio_model.keras

### Purpose

Audio Deepfake Detection

### Architecture

* CNN-Based Classifier
* Log-Mel Spectrogram Features
* Binary Classification

### Used By

```text
AudioRunner
```

### Output

* Audio Score
* Deepfake Prediction

---

## 3. audio_feature_extractor.keras

### Purpose

Auxiliary audio feature extraction model used during training and experimentation.

### Function

* Feature extraction
* Audio embedding generation
* Training support pipeline

---

## 4. svm_efficientnet_b4.pkl

### Purpose

Final SVM classifier used in the visual forensic fusion pipeline.

### Function

* Classification of extracted visual features
* Final image forensic decision

---

## 5. pca_efficientnet_b4.pkl

### Purpose

Dimensionality reduction for EfficientNet-B4 feature vectors.

### Function

* Feature compression
* Noise reduction
* Improved inference efficiency

---

## 6. deep_scaler.pkl

### Purpose

Normalization of deep visual features extracted from EfficientNet-B4.

### Function

* Feature standardization
* Stable classifier performance

---

## 7. land_scaler.pkl

### Purpose

Normalization of facial landmark features.

### Function

* Landmark feature scaling
* Consistent fusion input preparation

---

## 8. shape_predictor_68_face_landmarks.dat

### Purpose

Dlib facial landmark detector.

### Function

* Face geometry analysis
* Landmark extraction
* Visual forensic feature generation

### Landmarks

The detector extracts 68 facial landmarks including:

* Eyes
* Eyebrows
* Nose
* Mouth
* Jawline

---

# Verification

After downloading the files, verify that all required models are present.

Navigate to:

```text
backend/models/weights/
```

Expected files:

```text
improved_video_model.pth
best_audio_model.keras
audio_feature_extractor.keras
svm_efficientnet_b4.pkl
pca_efficientnet_b4.pkl
deep_scaler.pkl
land_scaler.pkl
shape_predictor_68_face_landmarks.dat
```

---

# Quick Verification Commands

### Windows PowerShell

```powershell
Get-ChildItem backend\models\weights
```

### Command Prompt

```cmd
dir backend\models\weights
```

---

# Troubleshooting

## Model Not Found Error

Verify that all files are placed inside:

```text
backend/models/weights/
```

and that the filenames match exactly.

---

## TensorFlow Loading Error

Ensure:

* Python 3.11 is installed
* Required packages are installed using:

```bash
pip install -r requirements.txt
```

---

## Dlib Loading Error

Ensure:

```bash
pip install dlib==20.0.1
```

is installed successfully.

---

# Notes

* Models are provided strictly for research and educational purposes.
* Do not redistribute model weights without permission.
* Some models were trained using publicly available datasets referenced in `DATASETS.md`.
* Performance may vary depending on hardware, operating system, and library versions.

---

# Related Documents

* `README.md`
* `datasets/DATASETS.md`
* `demo/DEMO_LINKS.md`
