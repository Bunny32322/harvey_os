"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function VoiceInterface() {
  const [isListening, setIsListening] = useState(false);

  const toggleListening = () => {
    setIsListening((prev) => !prev);
  };

  return (
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-center">
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="mb-4 glass-panel p-3 px-6 rounded-full flex gap-1 items-center"
          >
            {/* Simple CSS Waveform animation */}
            <span className="text-[var(--color-harvey-cyan)] text-xs uppercase tracking-widest font-bold mr-3 animate-pulse">
              Listening...
            </span>
            <div className="flex gap-1 h-4 items-end">
              {[1, 2, 3, 4, 5].map((i) => (
                <motion.div
                  key={i}
                  className="w-1 bg-[var(--color-harvey-gold)] rounded-t-sm"
                  animate={{
                    height: ["20%", "100%", "20%"],
                  }}
                  transition={{
                    // eslint-disable-next-line react-hooks/purity
                    duration: 0.6 + Math.random() * 0.4,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={toggleListening}
        className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 relative ${
          isListening 
            ? "bg-[var(--color-harvey-cyan)] bg-opacity-20 border-2 border-[var(--color-harvey-cyan)] shadow-[0_0_20px_rgba(0,255,255,0.4)]" 
            : "glass-panel bg-opacity-40 hover:bg-white hover:bg-opacity-10"
        }`}
      >
        {/* Glow effect when active */}
        {isListening && (
          <motion.div
            className="absolute inset-0 rounded-full border border-[var(--color-harvey-cyan)] pointer-events-none"
            animate={{
              scale: [1, 1.5, 2],
              opacity: [0.8, 0, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeOut",
            }}
          />
        )}
        
        {/* Microphone SVG */}
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke={isListening ? "var(--color-harvey-cyan)" : "var(--color-harvey-gold)"} 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" x2="12" y1="19" y2="22" />
        </svg>
      </button>
    </div>
  );
}
