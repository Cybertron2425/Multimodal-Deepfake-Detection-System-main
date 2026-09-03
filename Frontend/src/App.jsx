import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import Navbar from './components/Navbar';
import DropZone from './components/DropZone';
import AnalyzeButton from './components/AnalyzeButton';
import ResultCard from './components/ResultCard';
import AnalysisExperience from './components/AnalysisExperience';
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
    <div className="min-h-screen bg-void-950 dark:bg-void-950 relative overflow-hidden">
      {/* Global background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="background-grid absolute inset-0 bg-grid-pattern bg-grid opacity-30" />
        <div className="ambient-glow ambient-glow-one" />
        <div className="ambient-glow ambient-glow-two" />
        <div className="background-aurora" />
        <div className="background-particles" />
      </div>

      <Toaster position="top-right" />
      <Navbar />
      {/* Main detector panel */}
      <main className="relative max-w-2xl mx-auto px-3 sm:px-4 pt-24 sm:pt-28 md:pt-32 pb-10 sm:pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="detector-panel rounded-3xl border border-void-800 bg-void-900/40 backdrop-blur-xl
            p-4 sm:p-5 md:p-8 space-y-5 sm:space-y-6"
        >
          <div className="flex items-center justify-between pb-1">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-cyber-400">Secure analysis</p>
              <h2 className="mt-1 font-display text-lg sm:text-xl font-bold text-white">Upload a file to begin</h2>
            </div>
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-void-700/70 bg-void-950/50 px-3 py-1.5 text-xs text-void-400">
              <span className="h-1.5 w-1.5 rounded-full bg-neon-green shadow-[0_0_8px_#00ff9d]" />
              Private scan
            </div>
          </div>
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
            {isProcessing && !result && (
              <motion.div key="analysis" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <AnalysisExperience progress={uploadProgress} />
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
