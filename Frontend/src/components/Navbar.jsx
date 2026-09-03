import React from 'react';
import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';

export default function Navbar() {
  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div className="mx-2 sm:mx-4 mt-2 sm:mt-4">
        <nav className="max-w-4xl mx-auto px-3 sm:px-5 py-2.5 sm:py-3 rounded-2xl
          bg-void-900/80 border border-void-800/50
          backdrop-blur-xl flex items-center justify-between gap-2">

          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyber-400 to-cyber-600
              flex items-center justify-center">
              <Shield className="w-4 h-4 text-void-950" />
            </div>
            <span className="font-display font-semibold text-sm sm:text-base text-white tracking-tight whitespace-nowrap">
              Deepfake <span className="text-cyber-400">Detection</span>
            </span>
          </div>

          {/* Right side - status badge */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2 sm:px-3 py-1 rounded-full
              bg-void-800/50 border border-void-850">
              <span className="relative grid h-4 w-4 place-items-center" aria-hidden="true">
                <span className="absolute h-1.5 w-1.5 rounded-full bg-neon-green opacity-40 blur-sm animate-ping" />
                <motion.svg viewBox="0 0 24 24" className="relative h-4 w-4 overflow-visible" fill="none">
                  <path d="M2 12h4l2-7 3.2 14L14 9l2 3h6" stroke="rgba(0,255,157,0.25)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                  <motion.path d="M2 12h4l2-7 3.2 14L14 9l2 3h6" stroke="#00ff9d" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="7 5" animate={{ strokeDashoffset: [0, -36], opacity: [0.45, 1, 0.45] }} transition={{ strokeDashoffset: { duration: 1.3, repeat: Infinity, ease: 'linear' }, opacity: { duration: 1.3, repeat: Infinity, ease: 'easeInOut' } }} />
                </motion.svg>
              </span>
              <span className="status-label text-[11px] text-void-300 font-mono">System Active</span>
            </div>
          </div>
        </nav>
      </div>
    </motion.header>
  );
}
