import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Eye, Cpu } from 'lucide-react';

const stats = [
  { label: 'Models', value: '3', icon: Cpu, color: 'text-cyber-400' },
  { label: 'Accuracy', value: '97.3%', icon: Eye, color: 'text-neon-green' },
  { label: 'Formats', value: '15+', icon: Shield, color: 'text-neon-blue' },
];

export default function Hero() {
  return (
    <section className="relative pt-32 pb-8 px-4 text-center">
      {/* Radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px]
        rounded-full bg-cyber-500/5 blur-3xl pointer-events-none" />

      <div className="relative max-w-2xl mx-auto">
        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="font-display text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight"
        >
          AI Deepfake{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-400 to-neon-blue">
            Detector
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="text-void-400 text-sm md:text-base max-w-md mx-auto mb-6"
        >
          Analyze audio, images, or videos for synthetic manipulation and forensic details.
        </motion.p>
      </div>
    </section>
  );
}
