import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, Trash2, ShieldX, ShieldCheck, Image, Video, Music, ChevronRight } from 'lucide-react';

const FILE_ICONS = { image: Image, video: Video, audio: Music };

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function HistoryPanel({ history, onClear, onSelect }) {
  const [showAll, setShowAll] = useState(false);
  if (history.length === 0) return null;
  const visibleHistory = showAll ? history : history.slice(0, 3);

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="max-w-2xl mx-auto px-4 pb-16"
    >
      <div className="rounded-2xl border border-void-700/50 bg-void-900/40 backdrop-blur-sm overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between gap-2 px-4 sm:px-5 py-3.5 sm:py-4 border-b border-void-700/50">
          <div className="flex min-w-0 items-center gap-1.5 sm:gap-2.5">
            <History className="w-4 h-4 shrink-0 text-cyber-400" />
            <h2 className="font-display text-sm sm:text-base font-semibold text-white whitespace-nowrap">Recent Analyses</h2>
            <span className="shrink-0 px-2 py-0.5 rounded-md bg-cyber-500/20 text-cyber-300 text-xs font-mono">
              {history.length}
            </span>
          </div>
          <button onClick={onClear}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs
              shrink-0 text-void-400 hover:text-neon-red hover:bg-neon-red/10 transition-all border
              border-transparent hover:border-neon-red/20">
            <Trash2 className="w-3.5 h-3.5" />
            Clear
          </button>
        </div>

        {/* List */}
        <div className="divide-y divide-void-800/50">
          <AnimatePresence>
            {visibleHistory.map((item, i) => {
              const isFake = item.prediction?.toLowerCase() === 'fake';
              const FileIcon = FILE_ICONS[item.file_type] || Image;
              return (
                <motion.button
                  key={item.id || i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => onSelect(item)}
                  className="w-full flex items-center gap-4 px-5 py-3.5 hover:bg-void-800/30
                    transition-colors text-left group"
                >
                  {/* Icon */}
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{
                      background: isFake ? 'rgba(255,45,107,0.1)' : 'rgba(0,255,157,0.1)',
                      border: `1px solid ${isFake ? 'rgba(255,45,107,0.2)' : 'rgba(0,255,157,0.2)'}`,
                    }}>
                    {isFake
                      ? <ShieldX className="w-4 h-4" style={{ color: '#ff2d6b' }} />
                      : <ShieldCheck className="w-4 h-4" style={{ color: '#00ff9d' }} />
                    }
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <FileIcon className="w-3 h-3 text-void-500 flex-shrink-0" />
                      <p className="text-sm text-white font-medium truncate">{item.file_name}</p>
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-xs font-mono"
                        style={{ color: isFake ? '#ff2d6b' : '#00ff9d' }}>
                        {isFake ? 'FAKE' : 'REAL'} · {item.confidence?.toFixed(1)}%
                      </span>
                      <span className="text-xs text-void-500 font-mono">{timeAgo(item.timestamp)}</span>
                    </div>
                  </div>

                  <ChevronRight className="w-4 h-4 text-void-600 group-hover:text-void-400 transition-colors flex-shrink-0" />
                </motion.button>
              );
            })}
          </AnimatePresence>
        </div>

        {history.length > 3 && (
          <div className="border-t border-void-700/50 p-3 text-center">
            <button
              onClick={() => setShowAll((current) => !current)}
              className="rounded-lg px-4 py-2 text-xs font-medium text-cyber-300 transition-colors hover:bg-cyber-500/10 hover:text-cyber-200"
            >
              {showAll ? 'Show less' : `Show more (${history.length - 3})`}
            </button>
          </div>
        )}
      </div>
    </motion.section>
  );
}
