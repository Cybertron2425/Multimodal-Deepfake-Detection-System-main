# Demo Videos and Project Showcase

## Overview

This document contains demonstration videos, project walkthroughs, screenshots, and example outputs for the **DeepScan: Multimodal Deepfake Detection System**.

The provided demonstrations showcase the capabilities of the image, video, audio, and multimodal deepfake detection pipelines.

---

# Demo Repository

## Google Drive

Project Demonstrations:

https://drive.google.com/drive/folders/1BHo-qVYbDMaEPtDTUX8z7fgm87DuBor7?usp=sharing

---

# Available Demonstrations

The drive folder contains:

* Complete Project Walkthrough
* Frontend Demonstration
* Backend API Demonstration
* Image Deepfake Detection Demo
* Audio Deepfake Detection Demo
* Video Deepfake Detection Demo
* Multimodal Deepfake Detection Demo
* Sample Inputs and Outputs
* Project Screenshots

---

# 1. Image Deepfake Detection

## Description

This demonstration showcases the image deepfake detection pipeline based on EfficientNet-B4 and visual forensic analysis.

### Features Demonstrated

* Image Upload Interface
* Face Detection
* Deepfake Classification
* Confidence Score Generation
* Real vs Fake Prediction

### Example Files

```text
real_face_demo.jpg
fake_face_demo.jpg
image_detection_demo.mp4
```

### Model Used

```text
EfficientNet-B4
```

---

# 2. Audio Deepfake Detection

## Description

This demonstration showcases the CNN-based audio deepfake detection system trained on ASVspoof2019-LA.

### Features Demonstrated

* Audio Upload
* Audio Preprocessing
* Log-Mel Spectrogram Generation
* CNN Inference
* Synthetic Speech Detection

### Example Files

```text
real_audio.wav
fake_audio.wav
audio_detection_demo.mp4
```

### Model Used

```text
CNN Log-Mel Spectrogram Classifier
```

---

# 3. Video Deepfake Detection

## Description

This demonstration showcases the video deepfake detection pipeline using ResNeXt101 and face extraction.

### Features Demonstrated

* Video Upload
* Face Extraction
* Frame Sampling
* Suspicious Frame Selection
* Frame-Level Analysis
* Video-Level Decision Making

### Example Files

```text
real_video.mp4
fake_video.mp4
video_detection_demo.mp4
```

### Model Used

```text
ResNeXt101
```

---

# 4. Multimodal Deepfake Detection

## Description

This demonstration showcases the complete multimodal detection pipeline where multiple modalities are analyzed together.

### Features Demonstrated

* Video Processing
* Audio Processing
* Visual Analysis
* Cross-Modal Verification
* Reliability-Aware Fusion
* Final Deepfake Prediction

### Example Files

```text
multimodal_demo.mp4
```

### Components Used

```text
Video Branch     : ResNeXt101
Audio Branch     : CNN Log-Mel Network
Image Branch     : EfficientNet-B4
Fusion Engine    : Reliability-Aware Fusion
```

---

# Example Outputs

The demonstrations include examples of:

* Real Image Detection
* Fake Image Detection
* Real Video Detection
* Fake Video Detection
* Real Audio Detection
* Synthetic Audio Detection
* Multimodal Analysis Results

Output includes:

```text
Prediction
Confidence Score
Raw Deepfake Score
Model Information
Processing Time
```

---

# Hardware Configuration

## Training Environment

* Google Colab Pro
* NVIDIA Tesla T4 GPU
* High-RAM Runtime

## Development Environment

* Windows 11
* Python 3.11
* TensorFlow 2.20
* PyTorch 2.2
* OpenCV
* React.js
* Flask

---

# Research Objectives Demonstrated

The demos highlight:

* Deepfake Image Detection
* Deepfake Video Detection
* Audio Spoof Detection
* Multimodal Deepfake Analysis
* Reliability-Aware Fusion
* Real-World Deepfake Evaluation

---

# Related Documents

For additional information, see:

```text
README.md
datasets/DATASETS.md
weights/DOWNLOAD_MODELS.md
```

---

# Author

**Shubham Raj**

B.Tech in Data Science

Final Year Project

**DeepScan: Multimodal Deepfake Detection System**
