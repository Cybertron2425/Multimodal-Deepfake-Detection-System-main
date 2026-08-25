import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scan, Loader2, Zap } from 'lucide-react';

export default function AnalyzeButton({ onClick, isProcessing, disabled, uploadProgress }) {
  return (
    <div className="space-y-3">
      {/* Upload progress */}
      <AnimatePresence>
        {isProcessing && uploadProgress < 100 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-void-400 font-mono">Uploading...</span>
              <span className="text-xs text-cyber-400 font-mono">{uploadProgress}%</span>
            </div>
            <div className="h-1.5 bg-void-800 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-cyber-500 to-neon-blue rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${uploadProgress}%` }}
                transition={{ ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}

        {isProcessing && uploadProgress >= 100 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 justify-center"
          >
            <div className="flex gap-0.5">
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1 bg-cyber-400 rounded-full"
                  animate={{ height: ['8px', '24px', '8px'] }}
                  transition={{
                    duration: 0.8,
                    repeat: Infinity,
                    delay: i * 0.1,
                    ease: 'easeInOut'
                  }}
                />
              ))}
            </div>
            <span className="text-sm text-cyber-400 font-mono">Analyzing with AI...</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main button */}
      <motion.button
        onClick={onClick}
        disabled={disabled || isProcessing}
        whileHover={!disabled && !isProcessing ? { scale: 1.02 } : {}}
        whileTap={!disabled && !isProcessing ? { scale: 0.98 } : {}}
        className={`w-full py-4 rounded-2xl font-semibold text-base
          flex items-center justify-center gap-3 relative overflow-hidden
          transition-all duration-300
          ${disabled || isProcessing
            ? 'bg-void-800 text-void-500 cursor-not-allowed border border-void-700/50'
            : 'bg-gradient-to-r from-cyber-500 to-cyber-600 text-white shadow-neon hover:shadow-[0_0_30px_rgba(20,184,166,0.4)] border border-cyber-400/30'
          }`}
      >
        {/* Shimmer effect */}
        {!disabled && !isProcessing && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent
              -skew-x-12"
            animate={{ x: ['-200%', '200%'] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          />
        )}

        {isProcessing ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Processing...</span>
          </>
        ) : (
          <>
            <Scan className="w-5 h-5" />
            <span>Analyze for Deepfakes</span>
            <Zap className="w-4 h-4 opacity-70" />
          </>
        )}
      </motion.button>
    </div>
  );
}
