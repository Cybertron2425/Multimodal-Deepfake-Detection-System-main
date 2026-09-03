import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldX, Clock, Cpu, TrendingUp, BarChart3, Image, Video, Music, AlertTriangle, FileSearch, Info, Download, ScanLine, CheckCircle2 } from 'lucide-react';
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
    <div className="relative w-28 h-28 sm:w-40 sm:h-40 shrink-0">
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
        <span className="font-display font-bold text-2xl sm:text-3xl" style={{ color }}>
          {Math.round(animated)}
        </span>
        <span className="text-xs text-void-500 font-mono">%</span>
      </div>
    </div>
  );
}

function getFrameEvidence(result) {
  const details = result.frame_evidence || result.video_result?.frame_evidence;
  if (Array.isArray(details) && details.length) return details;

  // Older backend responses expose probabilities without timestamps.
  const probabilities = result.frame_probs || result.video_result?.frame_probs || [];
  return probabilities.map((probability, index) => {
    const value = Number(probability);
    const fakeProbability = value <= 1 ? value * 100 : value;
    return {
      frame_number: index + 1,
      frame_index: null,
      timestamp_seconds: null,
      fake_probability: fakeProbability,
      prediction: fakeProbability > 50 ? 'FAKE' : 'REAL',
    };
  });
}

function getFindings(result, isFake, fileType, confidence, model) {
  const target = fileType === 'video' ? 'video-frame patterns' : fileType === 'audio' ? 'audio-spectrum patterns' : 'image features';
  const frameEvidence = getFrameEvidence(result);
  const suspiciousFrames = frameEvidence.filter((frame) => frame.prediction === 'FAKE');
  if (!isFake) return [
    { icon: CheckCircle2, title: 'Model assessment passed', text: `${model || 'The selected model'} found the submitted ${target} more consistent with authentic content.` },
    { icon: TrendingUp, title: `${confidence.toFixed(1)}% classification confidence`, text: 'This expresses the model’s confidence in this scan; it is not a guarantee of authenticity.' },
    { icon: Info, title: 'Evidence scope', text: 'The current API returns a verdict and confidence only, so individual frame or timestamp evidence is not available.' },
  ];
  return [
    { icon: AlertTriangle, title: 'Manipulation pattern match', text: `${model || 'The AI model'} classified the submitted ${target} as more consistent with synthetic or manipulated content.` },
    { icon: ScanLine, title: `${confidence.toFixed(1)}% deepfake confidence`, text: 'The detection model assigned this probability to the fake class after processing the uploaded media.' },
    { icon: FileSearch, title: fileType === 'video' ? `${suspiciousFrames.length} of ${frameEvidence.length} sampled frames flagged` : 'Further review recommended', text: fileType === 'video' ? (frameEvidence.length ? 'Frame probabilities and timestamps below were returned directly by the detection backend.' : 'No individual-frame evidence was returned for this scan.') : 'Use this result as a screening signal and verify the original source before taking action.' },
  ];
}

function downloadReport(result, isFake, findings) {
  const lines = [
    'DEEPSCAN FORENSIC SCREENING REPORT', `Generated: ${new Date().toLocaleString()}`, '',
    `File: ${result.file_name}`, `Media type: ${result.file_type}`, `Verdict: ${isFake ? 'LIKELY MANIPULATED / DEEPFAKE' : 'LIKELY AUTHENTIC'}`,
    `Model confidence: ${Number(result.confidence || 0).toFixed(1)}%`, `Model: ${result.model || 'Not reported'}`, `Processing time: ${result.processing_time || 'Not reported'}`, '',
    'ASSESSMENT FINDINGS', ...findings.map((item, index) => `${index + 1}. ${item.title}\n   ${item.text}`), '',
    'LIMITATION', 'This is an automated screening result. Frame evidence is included when returned by the backend, but the model does not provide feature-level explanations. Confirm high-impact decisions with additional forensic review.'
  ];
  const evidence = getFrameEvidence(result)
    .sort((a, b) => b.fake_probability - a.fake_probability)
    .slice(0, 3);
  if (evidence.length) {
    const limitationIndex = lines.indexOf('LIMITATION');
    lines.splice(
      limitationIndex,
      0,
      '',
      'TOP FRAME EVIDENCE FROM BACKEND',
      ...evidence.map((frame) => `Frame ${frame.frame_number} | ${frame.timestamp_seconds === null ? 'timestamp unavailable' : `${frame.timestamp_seconds.toFixed(2)}s`} | Fake probability: ${frame.fake_probability.toFixed(1)}% | ${frame.prediction}`),
    );
  }
  const escapePdfText = (value) => value.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
  const wrappedLines = lines.flatMap((line) => {
    if (!line) return [''];
    const words = line.split(' ');
    return words.reduce((output, word) => {
      const current = output[output.length - 1];
      if (!current || `${current} ${word}`.length > 88) output.push(word);
      else output[output.length - 1] = `${current} ${word}`;
      return output;
    }, []);
  });
  const pageLines = 46;
  const pages = Array.from({ length: Math.ceil(wrappedLines.length / pageLines) }, (_, index) => wrappedLines.slice(index * pageLines, (index + 1) * pageLines));
  const objects = ['<< /Type /Catalog /Pages 2 0 R >>', `<< /Type /Pages /Kids [${pages.map((_, index) => `${3 + index * 2} 0 R`).join(' ')}] /Count ${pages.length} >>`];
  pages.forEach((page, index) => {
    const pageObject = 3 + index * 2;
    const contentObject = pageObject + 1;
    const content = ['BT', '/F1 10 Tf', '50 790 Td', '14 TL', ...page.map((line) => `(${escapePdfText(line)}) Tj T*`), 'ET'].join('\n');
    objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents ${contentObject} 0 R >>`);
    objects.push(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`);
  });
  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  offsets.slice(1).forEach((offset) => { pdf += `${String(offset).padStart(10, '0')} 00000 n \n`; });
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  const url = URL.createObjectURL(new Blob([pdf], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `${(result.file_name || 'deepfake-analysis').replace(/\.[^/.]+$/, '')}-forensic-report.pdf`;
  link.click();
  URL.revokeObjectURL(url);
}

export default function ResultCard({ result }) {
  const isFake = result.prediction?.toLowerCase() === 'fake';
  const FileIcon = FILE_ICONS[result.file_type] || Image;
  const confidence = Number(result.confidence || 0);
  const findings = getFindings(result, isFake, result.file_type, confidence, result.model);
  const accent = isFake ? '#ff2d6b' : '#00ff9d';
  const frameEvidence = getFrameEvidence(result).sort((a, b) => b.fake_probability - a.fake_probability).slice(0, 3);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="result-report relative rounded-2xl overflow-hidden border backdrop-blur-sm"
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
      <div className="px-4 sm:px-6 pt-4 sm:pt-6 pb-3 sm:pb-4 flex flex-col sm:flex-row items-center sm:items-center justify-between gap-1 sm:gap-4">
        <div className="flex items-center gap-2.5 sm:gap-3 w-full min-w-0">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="w-11 h-11 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center shrink-0"
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
              className="font-display font-bold text-lg sm:text-2xl leading-tight"
              style={{ color: isFake ? '#ff2d6b' : '#00ff9d' }}
            >
              {isFake ? '⚠ DEEPFAKE DETECTED' : '✓ AUTHENTIC CONTENT'}
            </motion.span>
          </div>
        </div>

        {/* Confidence arc */}
        <div className="self-center -mt-1 sm:mt-0">
          <ConfidenceArc confidence={result.confidence} isFake={isFake} />
        </div>
      </div>

      {/* Stats row */}
      <div className="px-4 sm:px-6 pb-4 sm:pb-6 grid grid-cols-3 gap-2 sm:gap-3">
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
            className="rounded-xl p-2 sm:p-3 bg-void-900/60 border border-void-700/30 min-w-0"
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <Icon className="w-3 h-3" style={{ color }} />
              <span className="text-[9px] sm:text-xs text-void-500 font-mono truncate">{label}</span>
            </div>
            <span className="text-xs sm:text-sm font-semibold text-white truncate block" style={{ color }}>
              {value}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Forensic report */}
      <motion.section
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
        className="mx-4 sm:mx-6 mb-4 sm:mb-5 rounded-2xl border border-void-700/50 bg-void-950/35 p-3.5 sm:p-5"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <FileSearch className="w-4 h-4" style={{ color: accent }} />
              <h3 className="font-display font-bold text-white">Why this result?</h3>
            </div>
            <p className="mt-1 text-xs text-void-500">Forensic assessment summary based on this scan.</p>
          </div>
          <button onClick={() => downloadReport(result, isFake, findings)}
            className="inline-flex w-auto justify-center items-center gap-2 rounded-lg border border-void-700 bg-void-900 px-3 py-2 text-xs font-medium text-void-300 transition-all hover:border-cyber-400/50 hover:text-cyber-200">
            <Download className="w-3.5 h-3.5" /> Download report
          </button>
        </div>

        <div className="mt-4 space-y-2.5">
          {findings.map(({ icon: Icon, title, text }, index) => (
            <motion.div key={title} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.56 + index * 0.1 }}
              className="flex gap-3 rounded-xl border border-void-800/70 bg-void-900/45 p-3">
              <div className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg" style={{ background: `${accent}16` }}>
                <Icon className="w-3.5 h-3.5" style={{ color: accent }} />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-void-100">{title}</h4>
                <p className="result-finding-description mt-0.5 text-xs leading-5 text-void-400">{text}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {frameEvidence.length > 0 && (
          <div className="mt-4 border-t border-void-800/80 pt-4">
            <div className="mb-2 flex items-center gap-2">
              <Video className="w-3.5 h-3.5 text-neon-blue" />
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-void-400">Top frame evidence from backend</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {frameEvidence.map((frame) => (
                <div key={frame.frame_number} className="rounded-lg border border-void-700/60 bg-void-900/50 p-2.5 sm:p-2.5 min-w-0">
                  <p className="font-mono text-[10px] text-void-500 whitespace-nowrap">{frame.timestamp_seconds === null ? `Frame ${frame.frame_number}` : `${frame.timestamp_seconds.toFixed(2)}s`}</p>
                  <p className="mt-1 text-base sm:text-sm font-bold" style={{ color: frame.prediction === 'FAKE' ? '#ff2d6b' : '#00ff9d' }}>{frame.fake_probability.toFixed(1)}%</p>
                  <p className="mt-0.5 text-[10px] uppercase tracking-wide text-void-400">fake probability</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="result-limitation mt-4 flex gap-2 border-t border-void-800/80 pt-3 text-[11px] leading-4 text-void-500">
          <Info className="mt-0.5 w-3.5 h-3.5 shrink-0 text-void-400" />
          <p>This is an automated screening result, not definitive proof. Frame evidence is available when returned by the backend; feature-level explanations are not provided by the model.</p>
        </div>
      </motion.section>

      {/* File name */}
      <div className="px-4 sm:px-6 pb-4 sm:pb-6">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-void-900/50 border border-void-700/30">
          <BarChart3 className="w-3.5 h-3.5 text-void-500 flex-shrink-0" />
          <span className="text-xs text-void-400 font-mono truncate">{result.file_name}</span>
        </div>
      </div>
    </motion.div>
  );
}
