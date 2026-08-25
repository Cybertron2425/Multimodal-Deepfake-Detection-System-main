import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const detectDeepfake = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const fileType = getFileType(file);
  const endpoint = `/predict/${fileType}`;

  const startTime = performance.now();

  const response = await api.post(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      onUploadProgress?.(progress);
    },
  });

  const elapsed = ((performance.now() - startTime) / 1000).toFixed(1);

  return {
    ...response.data,
    processing_time: response.data.processing_time || `${elapsed}s`,
    file_type: fileType,
    file_name: file.name,
    timestamp: new Date().toISOString(),
    id: Date.now(),
  };
};

export const getFileType = (file) => {
  const { type } = file;
  if (type.startsWith('image/')) return 'image';
  if (type.startsWith('video/')) return 'video';
  if (type.startsWith('audio/')) return 'audio';
  throw new Error('Unsupported file type. Please upload an image, video, or audio file.');
};

export const ACCEPTED_FILES = {
  'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'],
  'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
  'audio/*': ['.mp3', '.wav', '.flac', '.ogg', '.m4a'],
};

export const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB
