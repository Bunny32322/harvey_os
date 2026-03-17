"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface DataPanelProps {
  title: string;
  value: string | number;
  subtitle?: string;
  delay?: number;
  details?: string[];
}

export default function DataPanel({ title, value, subtitle, delay = 0, details }: DataPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8, delay, ease: "easeOut" }}
      whileHover={!isExpanded ? { scale: 1.05, x: -10 } : {}}
      onClick={() => setIsExpanded(!isExpanded)}
      className="glass-panel p-4 mb-4 min-w-[200px] cursor-pointer max-w-sm"
    >
      <motion.h3 layout className="text-[var(--color-harvey-gold)] text-xs uppercase tracking-widest mb-1 opacity-80 flex justify-between">
        {title}
        <span>{isExpanded ? '[-]' : '[+]'}</span>
      </motion.h3>
      
      <motion.div layout className="text-[var(--color-harvey-cyan)] text-3xl font-mono holographic-text">
        {value}
      </motion.div>
      
      {subtitle && <motion.p layout className="text-gray-400 text-xs mt-1">{subtitle}</motion.p>}

      <AnimatePresence>
        {isExpanded && details && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: "auto", marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            className="overflow-hidden border-t border-[var(--color-harvey-gold)]/20 pt-2"
          >
            <ul className="text-sm font-mono text-gray-300 space-y-1">
              {details.map((detail, idx) => (
                <li key={idx} className="flex gap-2 items-start">
                  <span className="text-[var(--color-harvey-cyan)] opacity-70">▹</span> 
                  {detail}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
