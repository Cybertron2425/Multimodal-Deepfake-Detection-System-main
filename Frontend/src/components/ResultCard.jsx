import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldX, Clock, Cpu, TrendingUp, BarChart3, Image, Video, Music } from 'lucide-react';
import { RadialBarChart, RadialBar, Cell, ResponsiveContainer } from 'recharts';

const FILE_ICONS = { image: Image, video: Video, audio: Music };

function ConfidenceArc({ confidence, isFake }) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(confidence), 300);
    return () => clearTimeout(timer);
  }, [confidence]);

  const color = isFake ? '#ff2d6b' : '#00ff9d';
  const data = [{ value: animated }, { value: 100 - animated }];

  return (
    <div className="relative w-40 h-40">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%" cy="50%"
          innerRadius="65%" outerRadius="90%"
          startAngle={225} endAngle={-45}
          data={data}
        >
          <RadialBar dataKey="value" cornerRadius={10} background={{ fill: 'rgba(255,255,255,0.03)' }}>
            <Cell fill={color} />
            <Cell fill="transparent" />
          </RadialBar>
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display font-bold text-3xl" style={{ color }}>
          {Math.round(animated)}
        </span>
        <span className="text-xs text-void-500 font-mono">%</span>
      </div>
    </div>
  );
}

export default function ResultCard({ result }) {
  const isFake = result.prediction?.toLowerCase() === 'fake';
  const FileIcon = FILE_ICONS[result.file_type] || Image;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="relative rounded-2xl overflow-hidden border backdrop-blur-sm"
      style={{
        borderColor: isFake ? 'rgba(255,45,107,0.3)' : 'rgba(0,255,157,0.3)',
        background: isFake
          ? 'linear-gradient(135deg, rgba(255,45,107,0.05) 0%, rgba(15,23,42,0.8) 100%)'
          : 'linear-gradient(135deg, rgba(0,255,157,0.05) 0%, rgba(15,23,42,0.8) 100%)',
      }}
    >
      {/* Top glow bar */}
      <div className="h-px w-full"
        style={{
          background: isFake
            ? 'linear-gradient(90deg, transparent, #ff2d6b, transparent)'
            : 'linear-gradient(90deg, transparent, #00ff9d, transparent)'
        }} />

      {/* Verdict banner */}
      <div className="px-6 pt-6 pb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{
              background: isFake ? 'rgba(255,45,107,0.15)' : 'rgba(0,255,157,0.15)',
              border: `1px solid ${isFake ? 'rgba(255,45,107,0.3)' : 'rgba(0,255,157,0.3)'}`,
            }}
          >
            {isFake
              ? <ShieldX className="w-6 h-6" style={{ color: '#ff2d6b' }} />
              : <ShieldCheck className="w-6 h-6" style={{ color: '#00ff9d' }} />
            }
          </motion.div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <FileIcon className="w-3.5 h-3.5 text-void-400" />
              <span className="text-xs text-void-400 font-mono uppercase tracking-wider">
                {result.file_type} analysis
              </span>
            </div>
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="font-display font-bold text-2xl"
              style={{ color: isFake ? '#ff2d6b' : '#00ff9d' }}
            >
              {isFake ? '⚠ DEEPFAKE DETECTED' : '✓ AUTHENTIC CONTENT'}
            </motion.span>
          </div>
        </div>

        {/* Confidence arc */}
        <ConfidenceArc confidence={result.confidence} isFake={isFake} />
      </div>

      {/* Stats row */}
      <div className="px-6 pb-6 grid grid-cols-3 gap-3">
        {[
          { icon: TrendingUp, label: 'Confidence', value: `${result.confidence?.toFixed(1)}%`, color: isFake ? '#ff2d6b' : '#00ff9d' },
          { icon: Clock, label: 'Processing', value: result.processing_time, color: '#00d4ff' },
          { icon: Cpu, label: 'Model', value: result.model, color: '#bf5af2' },
        ].map(({ icon: Icon, label, value, color }) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="rounded-xl p-3 bg-void-900/60 border border-void-700/30"
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <Icon className="w-3 h-3" style={{ color }} />
              <span className="text-xs text-void-500 font-mono">{label}</span>
            </div>
            <span className="text-sm font-semibold text-white truncate block" style={{ color }}>
              {value}
            </span>
          </motion.div>
        ))}
      </div>

      {/* File name */}
      <div className="px-6 pb-5">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-void-900/50 border border-void-700/30">
          <BarChart3 className="w-3.5 h-3.5 text-void-500 flex-shrink-0" />
          <span className="text-xs text-void-400 font-mono truncate">{result.file_name}</span>
        </div>
      </div>
    </motion.div>
  );
}
