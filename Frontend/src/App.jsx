import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import DropZone from './components/DropZone';
import AnalyzeButton from './components/AnalyzeButton';
import ResultCard from './components/ResultCard';
import ResultSkeleton from './components/ResultSkeleton';
import HistoryPanel from './components/HistoryPanel';
import { ThemeProvider } from './context/ThemeContext';
import { useHistory } from './hooks/useHistory';
import { detectDeepfake } from './services/api';
import './index.css';

function DeepfakeApp() {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);
  const { history, addEntry, clearHistory } = useHistory();

  const handleFileSelect = useCallback((selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setUploadProgress(0);
  }, []);

  const handleClear = useCallback(() => {
    setFile(null);
    setResult(null);
    setUploadProgress(0);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;

    setIsProcessing(true);
    setUploadProgress(0);
    setResult(null);

    const toastId = toast.loading('Uploading file...', {
      style: {
        background: '#0f172a',
        color: '#e2e8f0',
        border: '1px solid rgba(20,184,166,0.3)',
        borderRadius: '12px',
        fontFamily: 'DM Sans, sans-serif',
      },
    });

    try {
      const prediction = await detectDeepfake(file, (progress) => {
        setUploadProgress(progress);
        if (progress === 100) {
          toast.loading('Analyzing with AI models...', {
            id: toastId,
            style: {
              background: '#0f172a',
              color: '#e2e8f0',
              border: '1px solid rgba(20,184,166,0.3)',
              borderRadius: '12px',
            },
          });
        }
      });

      setResult(prediction);
      addEntry(prediction);

      const isFake = prediction.prediction?.toLowerCase() === 'fake';
      toast.success(
        isFake ? '⚠ Deepfake detected!' : '✓ Content appears authentic',
        {
          id: toastId,
          style: {
            background: '#0f172a',
            color: isFake ? '#ff2d6b' : '#00ff9d',
            border: `1px solid ${isFake ? 'rgba(255,45,107,0.3)' : 'rgba(0,255,157,0.3)'}`,
            borderRadius: '12px',
          },
          duration: 4000,
        }
      );
    } catch (err) {
      toast.error(err.message || 'Analysis failed. Please try again.', {
        id: toastId,
        style: {
          background: '#0f172a',
          color: '#ff2d6b',
          border: '1px solid rgba(255,45,107,0.3)',
          borderRadius: '12px',
        },
        duration: 5000,
      });
    } finally {
      setIsProcessing(false);
    }
  }, [file, addEntry]);

  return (
    <div className="min-h-screen bg-void-950 dark:bg-void-950 relative">
      {/* Global background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-grid-pattern bg-grid opacity-30" />
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-cyber-500/5 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-neon-purple/5 blur-3xl" />
      </div>

      <Toaster position="top-right" />
      <Navbar />
      <Hero />

      {/* Main detector panel */}
      <main className="relative max-w-2xl mx-auto px-4 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="rounded-3xl border border-void-800 bg-void-900/40 backdrop-blur-xl
            p-6 md:p-8 space-y-6"
        >
          {/* Drop zone */}
          <DropZone
            onFileSelect={handleFileSelect}
            file={file}
            onClear={handleClear}
            isProcessing={isProcessing}
          />

          {/* Analyze button */}
          <AnalyzeButton
            onClick={handleAnalyze}
            isProcessing={isProcessing}
            disabled={!file}
            uploadProgress={uploadProgress}
          />

          {/* Results */}
          <AnimatePresence mode="wait">
            {isProcessing && uploadProgress >= 100 && !result && (
              <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <ResultSkeleton />
              </motion.div>
            )}
            {result && !isProcessing && (
              <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <ResultCard result={result} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </main>

      {/* History panel */}
      <HistoryPanel
        history={history}
        onClear={clearHistory}
        onSelect={(item) => {
          setResult(item);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <DeepfakeApp />
    </ThemeProvider>
  );
}
