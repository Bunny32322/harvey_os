"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

export default function AnalysisOutput({ text }: { text: string }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    if (!text) {
      setDisplayedText("");
      return;
    }

    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + text.charAt(i));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 15); // Fast typewriter effect

    return () => clearInterval(interval);
  }, [text]);

  if (!text) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 max-h-[40vh] overflow-y-auto w-full max-w-3xl absolute top-[60vh] left-1/2 -translate-x-1/2 z-10"
    >
      <h3 className="text-[var(--color-harvey-gold)] text-sm tracking-widest uppercase mb-2">
        Tactical Analysis
      </h3>
      <div className="text-gray-200 font-mono whitespace-pre-wrap text-sm leading-relaxed">
        {displayedText}
        <span className="animate-pulse ml-1 inline-block w-2 h-4 bg-[var(--color-harvey-cyan)]"></span>
      </div>
    </motion.div>
  );
}
