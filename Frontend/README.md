# DeepScan — AI Deepfake Detection Platform

A professional, futuristic deepfake detection web application with support for images, videos, and audio.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- Backend API running (see Backend Setup)

### Frontend Setup

```bash
cd deepfake-detector
npm install
cp .env.example .env   # Edit API URL
npm start
```

Opens at http://localhost:3000

### Environment Variables

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 📁 Project Structure

```
deepfake-detector/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          # Fixed navbar with live status
│   │   ├── Hero.jsx            # Hero section with stats
│   │   ├── DropZone.jsx        # Drag & drop file upload
│   │   ├── AnalyzeButton.jsx   # Upload progress + analyze
│   │   ├── ResultCard.jsx      # Detection result with charts
│   │   ├── ResultSkeleton.jsx  # Loading skeleton
│   │   └── HistoryPanel.jsx    # Recent analyses history
│   ├── context/
│   │   └── ThemeContext.jsx    # Dark/light mode
│   ├── hooks/
│   │   └── useHistory.js       # LocalStorage history
│   ├── services/
│   │   └── api.js              # Axios API integration
│   ├── App.jsx
│   ├── index.js
│   └── index.css
├── .env
├── package.json
└── tailwind.config.js
```

## 🔌 Backend API Contract

### POST /predict/image
### POST /predict/video  
### POST /predict/audio

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "prediction": "Fake",
  "confidence": 97.3,
  "processing_time": "1.2s",
  "model": "EfficientNet-B4"
}
```

## 🧠 AI Models

| Media | Endpoint | Architecture |
|-------|----------|-------------|
| Image | `/predict/image` | EfficientNet-B4 |
| Video | `/predict/video` | SlowFast Network |
| Audio | `/predict/audio` | CNN + Log-Mel (ASVspoof) |

## ✨ Features

- Drag & drop upload with file preview
- Automatic file type detection (image/video/audio)
- Upload progress animation
- AI confidence visualization (radial chart)
- Real vs Fake verdict banner
- Processing time & model display
- Analysis history (persisted in localStorage)
- Dark/light mode toggle
- Toast notifications
- Loading skeletons
- Responsive design
- File validation (type + size)

## 🏗️ Building for Production

```bash
npm run build
# Serve the /build directory
```

## 🔧 Backend Quick Start (Python/FastAPI)

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    # Load your EfficientNet-B4 model and run inference
    return {"prediction": "Fake", "confidence": 97.3, "processing_time": "1.2s", "model": "EfficientNet-B4"}

@app.post("/predict/video")
async def predict_video(file: UploadFile = File(...)):
    return {"prediction": "Real", "confidence": 88.5, "processing_time": "3.4s", "model": "SlowFast"}

@app.post("/predict/audio")
async def predict_audio(file: UploadFile = File(...)):
    return {"prediction": "Fake", "confidence": 94.1, "processing_time": "0.8s", "model": "CNN-LogMel"}

# Run: uvicorn main:app --reload --port 8000
```
