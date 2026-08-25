/**
 * src/services/api.js
 *
 * Drop-in replacement for your existing api.js.
 * Zero changes required to any other component.
 *
 * Backend endpoints (Flask, port 8000):
 *   POST /predict/image   → { prediction, confidence, processing_time, model }
 *   POST /predict/video   → { prediction, confidence, processing_time, model }
 *   POST /predict/audio   → { prediction, confidence, processing_time, model }
 *
 * Error shape from Flask:  { detail: "message" }
 * Interceptor re-throws as: new Error(detail)
 */

import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,  // 120 s — matches Flask model inference time for large videos
});

// Map Flask { detail } → JS Error so components get err.message
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'An error occurred';
    return Promise.reject(new Error(message));
  }
);

/**
 * Detect deepfakes in an image, video, or audio file.
 *
 * @param {File}     file              - The file to analyse
 * @param {Function} onUploadProgress  - Called with integer 0-100
 * @returns {Promise<{
 *   prediction:      "Fake"|"Real",
 *   confidence:      number,
 *   processing_time: string,
 *   model:           string,
 *   file_type:       "image"|"video"|"audio",
 *   file_name:       string,
 *   timestamp:       string,   // ISO-8601
 *   id:              number,   // Date.now()
 * }>}
 */
export const detectDeepfake = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const fileType = getFileType(file);
  const endpoint = `/predict/${fileType}`;

  const startTime = performance.now();

  const response = await api.post(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const progress = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      );
      onUploadProgress?.(progress);
    },
  });

  const elapsed = ((performance.now() - startTime) / 1000).toFixed(1);

  // Merge server response with client-side metadata
  return {
    ...response.data,
    // Prefer server's processing_time (pure inference); fall back to wall time
    processing_time: response.data.processing_time || `${elapsed}s`,
    file_type:  fileType,
    file_name:  file.name,
    timestamp:  new Date().toISOString(),
    id:         Date.now(),
  };
};

/**
 * Derive media type from browser MIME type.
 * Matches the backend's routing logic exactly.
 */
export const getFileType = (file) => {
  const { type } = file;
  if (type.startsWith('image/')) return 'image';
  if (type.startsWith('video/')) return 'video';
  if (type.startsWith('audio/')) return 'audio';
  throw new Error(
    'Unsupported file type. Please upload an image, video, or audio file.'
  );
};

/** Accepted MIME types for react-dropzone (mirrors backend ALLOWED_*_TYPES) */
export const ACCEPTED_FILES = {
  'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'],
  'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
  'audio/*': ['.mp3', '.wav', '.flac', '.ogg', '.m4a'],
};

/** Max upload size — must match Flask MAX_CONTENT_LENGTH (500 MB) */
export const MAX_FILE_SIZE = 500 * 1024 * 1024;
