import React from 'react';
import { motion } from 'framer-motion';
import { AudioLines, BrainCircuit, CheckCircle2, ScanFace, Sparkles } from 'lucide-react';

const stages = [
  { label: 'Encrypting upload', icon: CheckCircle2 },
  { label: 'Extracting forensic signals', icon: ScanFace },
  { label: 'Comparing AI fingerprints', icon: BrainCircuit },
  { label: 'Building confidence report', icon: Sparkles },
];

export default function AnalysisExperience({ progress }) {
  const activeStage = progress < 100 ? 0 : 2;

  return (
    <motion.section initial={{ opacity: 0, y: 12, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -8, scale: 0.98 }} className="analysis-experience relative overflow-hidden rounded-2xl border border-cyber-400/25 p-5 sm:p-6" aria-live="polite">
      <div className="analysis-sweep" />
      <div className="relative grid items-center gap-6 md:grid-cols-[1fr_190px]">
        <div>
          <div className="flex items-center gap-2 text-cyber-300"><span className="flex h-2 w-2 relative"><span className="absolute inline-flex h-full w-full rounded-full bg-cyber-300 opacity-75 animate-ping" /><span className="relative inline-flex h-2 w-2 rounded-full bg-cyber-300" /></span><span className="font-mono text-[10px] uppercase tracking-[0.2em]">Live forensic pipeline</span></div>
          <h3 className="mt-3 font-display text-xl sm:text-2xl font-bold text-white">Reading digital fingerprints…</h3>
          <p className="mt-1 text-sm text-void-400">Our models are checking visual artifacts, audio patterns, and synthesis traces.</p>
          <div className="mt-5 space-y-2.5">
            {stages.map(({ label, icon: Icon }, index) => {
              const complete = index < activeStage;
              const active = index === activeStage;
              return <motion.div key={label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.08 }} className={`flex items-center gap-3 text-sm ${active ? 'text-white' : complete ? 'text-cyber-300' : 'text-void-500'}`}><span className={`grid h-6 w-6 place-items-center rounded-full border ${active ? 'border-cyber-300 bg-cyber-500/20' : complete ? 'border-cyber-400/50 bg-cyber-500/10' : 'border-void-700 bg-void-900/60'}`}><Icon className={`h-3.5 w-3.5 ${active ? 'animate-pulse text-cyber-200' : ''}`} /></span><span>{label}</span>{active && <span className="ml-auto font-mono text-[10px] text-cyber-300">RUNNING</span>}{complete && <CheckCircle2 className="ml-auto h-4 w-4 text-neon-green" />}</motion.div>;
            })}
          </div>
        </div>
        <div className="relative mx-auto grid h-44 w-44 place-items-center rounded-full border border-cyber-400/20 bg-void-950/40"><div className="analysis-ring analysis-ring-one" /><div className="analysis-ring analysis-ring-two" /><div className="analysis-grid" /><motion.div animate={{ rotate: 360 }} transition={{ duration: 3.2, repeat: Infinity, ease: 'linear' }} className="absolute inset-2 rounded-full border-t-2 border-cyber-300/80" /><div className="relative z-10 grid h-16 w-16 place-items-center rounded-2xl border border-cyber-400/35 bg-cyber-500/10 shadow-[0_0_32px_rgba(20,184,166,.22)]"><AudioLines className="h-7 w-7 text-cyber-200" /></div><div className="absolute -bottom-1 rounded-full border border-cyber-400/20 bg-void-900 px-2 py-1 font-mono text-[9px] tracking-widest text-cyber-300">ANALYZING</div></div>
      </div>
      <div className="relative mt-6 h-1.5 overflow-hidden rounded-full bg-void-800"><motion.div className="h-full rounded-full bg-gradient-to-r from-cyber-600 via-cyber-300 to-neon-blue" initial={{ width: '4%' }} animate={{ width: progress < 100 ? `${Math.max(8, progress)}%` : ['72%', '94%', '80%'] }} transition={progress < 100 ? { duration: 0.25 } : { duration: 2.2, repeat: Infinity, ease: 'easeInOut' }} /></div>
    </motion.section>
  );
}
