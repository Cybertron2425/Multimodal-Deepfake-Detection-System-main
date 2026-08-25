import React from 'react';
import { motion } from 'framer-motion';

function Skeleton({ className }) {
  return (
    <motion.div
      className={`rounded-xl bg-void-800/50 relative overflow-hidden ${className}`}
      animate={{}}
    >
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-void-700/30 to-transparent"
        animate={{ x: ['-100%', '100%'] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
      />
    </motion.div>
  );
}

export default function ResultSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-2xl border border-void-700/50 bg-void-900/40 p-6 space-y-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="w-12 h-12" />
          <div className="space-y-2">
            <Skeleton className="w-20 h-3" />
            <Skeleton className="w-44 h-6" />
          </div>
        </div>
        <Skeleton className="w-40 h-40 rounded-full" />
      </div>
      <div className="grid grid-cols-3 gap-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-16" />
        ))}
      </div>
      <Skeleton className="h-9" />
    </motion.div>
  );
}
