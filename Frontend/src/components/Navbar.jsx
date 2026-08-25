import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Sun, Moon, Activity, Zap } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Navbar() {
  const { isDark, toggle } = useTheme();

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div className="mx-4 mt-4">
        <nav className="max-w-4xl mx-auto px-5 py-3 rounded-2xl
          bg-void-900/80 border border-void-800/50
          backdrop-blur-xl flex items-center justify-between">

          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyber-400 to-cyber-600
              flex items-center justify-center">
              <Shield className="w-4 h-4 text-void-950" />
            </div>
            <span className="font-display font-semibold text-base text-white tracking-tight">
              Deep<span className="text-cyber-400">Scan</span>
            </span>
          </div>

          {/* Right side - status badge */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full
              bg-void-800/50 border border-void-850">
              <Activity className="w-3 h-3 text-neon-green" />
              <span className="text-[11px] text-void-300 font-mono">System Active</span>
            </div>
          </div>
        </nav>
      </div>
    </motion.header>
  );
}
