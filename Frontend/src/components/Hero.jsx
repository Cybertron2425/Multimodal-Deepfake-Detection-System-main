import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Eye, Cpu, ScanLine, Sparkles } from 'lucide-react';

const stats = [
  { label: 'Models', value: '3', icon: Cpu, color: 'text-cyber-400' },
  { label: 'Accuracy', value: '97.3%', icon: Eye, color: 'text-neon-green' },
  { label: 'Formats', value: '15+', icon: Shield, color: 'text-neon-blue' },
];

export default function Hero() {
  return (
    <section className="relative pt-28 md:pt-32 pb-10 px-4 overflow-hidden">
      {/* Radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px]
        rounded-full bg-cyber-500/5 blur-3xl pointer-events-none" />

      <div className="relative max-w-5xl mx-auto grid items-center gap-8 lg:grid-cols-[1fr_280px]">
        <div className="text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-cyber-400/20 bg-cyber-500/10 px-3 py-1.5 mb-5"
          >
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-neon-green opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-neon-green" />
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-cyber-200">Forensic AI online</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.08 }}
            className="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 tracking-tight leading-[1.04]"
          >
            See what&apos;s{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-300 via-cyber-400 to-neon-blue">
              real.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.18 }}
            className="text-void-400 text-sm md:text-base max-w-xl mx-auto lg:mx-0"
          >
            Detect synthetic manipulation across images, videos, and audio with a multi-model forensic scan.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="show"
            variants={{ show: { transition: { staggerChildren: 0.1, delayChildren: 0.28 } } }}
            className="mt-7 grid grid-cols-3 gap-2 sm:gap-3 max-w-xl mx-auto lg:mx-0"
          >
            {stats.map(({ label, value, icon: Icon, color }) => (
              <motion.div
                key={label}
                variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
                className="rounded-xl border border-void-700/50 bg-void-900/50 px-3 py-3 backdrop-blur-sm"
              >
                <Icon className={`w-4 h-4 ${color} mb-2`} />
                <div className="font-display text-lg font-bold text-white leading-none">{value}</div>
                <div className="mt-1 text-[10px] sm:text-xs text-void-500 font-mono uppercase tracking-wide">{label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.82, rotate: -8 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, delay: 0.18, ease: [0.16, 1, 0.3, 1] }}
          className="hidden lg:grid relative place-items-center h-64"
          aria-hidden="true"
        >
          <div className="scanner-orbit scanner-orbit-one" />
          <div className="scanner-orbit scanner-orbit-two" />
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 14, repeat: Infinity, ease: 'linear' }} className="scanner-dash" />
          <div className="scanner-core">
            <ScanLine className="w-11 h-11 text-cyber-200" />
            <Sparkles className="absolute right-6 top-7 w-4 h-4 text-neon-blue" />
          </div>
          <motion.span animate={{ y: [-3, 3, -3], opacity: [0.55, 1, 0.55] }} transition={{ duration: 2.4, repeat: Infinity }} className="absolute -bottom-1 font-mono text-[10px] tracking-[0.22em] text-cyber-400">SCAN READY</motion.span>
        </motion.div>
      </div>
    </section>
  );
}
