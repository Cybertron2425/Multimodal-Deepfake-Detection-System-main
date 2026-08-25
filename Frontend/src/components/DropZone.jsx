import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Image, Video, Music, X, FileCheck, AlertCircle } from 'lucide-react';
import { ACCEPTED_FILES, MAX_FILE_SIZE, getFileType } from '../services/api';

const FILE_ICONS = { image: Image, video: Video, audio: Music };
const FILE_COLORS = {
  image: 'text-neon-blue',
  video: 'text-neon-purple',
  audio: 'text-neon-green',
};

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function DropZone({ onFileSelect, file, onClear, isProcessing }) {
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError('');
    if (rejectedFiles.length > 0) {
      const err = rejectedFiles[0].errors[0];
      setError(err.code === 'file-too-large'
        ? `File too large. Max size is ${formatSize(MAX_FILE_SIZE)}.`
        : 'Unsupported file type. Please upload image, video, or audio.');
      return;
    }
    if (acceptedFiles.length > 0) {
      try {
        getFileType(acceptedFiles[0]); // validate
        onFileSelect(acceptedFiles[0]);
      } catch (e) {
        setError(e.message);
      }
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: () => setDragActive(false),
    accept: ACCEPTED_FILES,
    maxSize: MAX_FILE_SIZE,
    maxFiles: 1,
    disabled: isProcessing,
  });

  const fileType = file ? getFileType(file) : null;
  const FileIcon = fileType ? FILE_ICONS[fileType] : null;

  return (
    <div className="w-full">
      <AnimatePresence mode="wait">
        {file ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative rounded-2xl border border-cyber-500/40 bg-void-900/60
              backdrop-blur-sm p-6 overflow-hidden"
          >
            {/* Shimmer top border */}
            <div className="absolute top-0 left-0 right-0 h-px
              bg-gradient-to-r from-transparent via-cyber-400 to-transparent" />

            <div className="flex items-center gap-4">
              <div className={`w-14 h-14 rounded-xl flex items-center justify-center
                bg-void-800 border border-void-700/50 flex-shrink-0`}>
                <FileIcon className={`w-7 h-7 ${FILE_COLORS[fileType]}`} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <FileCheck className="w-3.5 h-3.5 text-cyber-400 flex-shrink-0" />
                  <span className="text-xs text-cyber-400 font-mono uppercase tracking-wider">
                    {fileType} file ready
                  </span>
                </div>
                <p className="text-white font-medium truncate">{file.name}</p>
                <p className="text-void-400 text-sm mt-0.5">{formatSize(file.size)}</p>
              </div>

              {!isProcessing && (
                <button onClick={onClear}
                  className="w-8 h-8 rounded-lg bg-void-800 border border-void-700/50
                    flex items-center justify-center hover:border-neon-red/50
                    hover:text-neon-red transition-all flex-shrink-0 text-void-400">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Media preview */}
            {fileType === 'image' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="mt-4 rounded-xl overflow-hidden border border-void-700/50"
              >
                <img
                  src={URL.createObjectURL(file)}
                  alt="Preview"
                  className="w-full max-h-64 object-contain bg-void-950"
                />
              </motion.div>
            )}

            {fileType === 'audio' && (
              <div className="mt-4">
                <audio controls className="w-full" style={{ filter: 'invert(0.9) hue-rotate(180deg)' }}>
                  <source src={URL.createObjectURL(file)} type={file.type} />
                </audio>
              </div>
            )}

            {fileType === 'video' && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="mt-4 rounded-xl overflow-hidden border border-void-700/50"
              >
                <video controls className="w-full max-h-64 bg-void-950">
                  <source src={URL.createObjectURL(file)} type={file.type} />
                </video>
              </motion.div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            {...getRootProps()}
            className={`relative rounded-2xl border-2 border-dashed cursor-pointer
              transition-all duration-300 p-12 text-center group overflow-hidden
              ${isDragActive || dragActive
                ? 'border-cyber-400 bg-cyber-500/5'
                : 'border-void-700/50 bg-void-900/40 hover:border-cyber-500/50 hover:bg-cyber-500/5'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />

            {/* Scan line when dragging */}
            {(isDragActive || dragActive) && (
              <motion.div
                className="absolute left-0 right-0 h-px bg-gradient-to-r
                  from-transparent via-cyber-400 to-transparent"
                animate={{ top: ['0%', '100%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              />
            )}

            {/* Icon cluster */}
            <div className="flex items-center justify-center gap-3 mb-6">
              {[Image, Video, Music].map((Icon, i) => (
                <motion.div
                  key={i}
                  whileHover={{ scale: 1.1 }}
                  className="w-12 h-12 rounded-xl bg-void-800 border border-void-700/50
                    flex items-center justify-center group-hover:border-cyber-500/30
                    transition-all duration-300"
                >
                  <Icon className="w-6 h-6 text-void-400 group-hover:text-cyber-400 transition-colors" />
                </motion.div>
              ))}
            </div>

            <div className="flex items-center justify-center gap-2 mb-3">
              <Upload className="w-4 h-4 text-cyber-400" />
              <p className="text-white font-semibold">
                Drop your file here, or{' '}
                <span className="text-cyber-400 underline underline-offset-2">browse</span>
              </p>
            </div>
            <p className="text-void-500 text-sm">
              Supports Images, Videos, and Audio • Max 500MB
            </p>
            <p className="text-void-600 text-xs mt-2 font-mono">
              JPG · PNG · MP4 · AVI · MOV · MP3 · WAV · FLAC
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-3 flex items-center gap-2 px-4 py-3 rounded-xl
              bg-neon-red/10 border border-neon-red/30"
          >
            <AlertCircle className="w-4 h-4 text-neon-red flex-shrink-0" />
            <p className="text-neon-red text-sm">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
