"use client";

import { useEffect, useState, Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, Effects } from "@react-three/drei";
import { UnrealBloomPass } from "three-stdlib";
import { extend } from "@react-three/fiber";

import HolographicCore from "../components/HolographicCore";
import StrategicRadar from "../components/StrategicRadar";
import DataPanel from "../components/DataPanel";
import NeuralThinking from "../components/NeuralThinking";
import AnalysisOutput from "../components/AnalysisOutput";
import DecisionTimeline, { DecisionNode } from "../components/DecisionTimeline";
import OpportunityScanner, { Opportunity } from "../components/OpportunityScanner";
import ThreatDetection, { Threat } from "../components/ThreatDetection";
import VoiceInterface from "../components/VoiceInterface";
import { api, HabitsData } from "../lib/api";

extend({ UnrealBloomPass });

export default function Home() {
  const [isThinking, setIsThinking] = useState(false);
  const [situation, setSituation] = useState("");
  const [analysisResult, setAnalysisResult] = useState("");
  const [habits, setHabits] = useState<HabitsData | null>(null);
  const [leverageScore, setLeverageScore] = useState<number>(0);
  const [decisions, setDecisions] = useState<DecisionNode[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);

  useEffect(() => {
    // Fetch initial data
    api.getHabits().then((data) => {
      setHabits(data.habits);
      setLeverageScore(data.leverage_score);
    }).catch(err => console.error("API Connection Error (Habits):", err));

    api.getDecisions().then((data) => setDecisions(data)).catch(console.error);
    api.getOpportunities().then((data) => setOpportunities(data)).catch(console.error);
    api.getThreats().then((data) => setThreats(data)).catch(console.error);
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!situation.trim()) return;

    setIsThinking(true);
    setAnalysisResult("");

    try {
      const res = await api.analyze(situation);
      setAnalysisResult(res.analysis);
    } catch (error) {
      console.error("Analysis Error:", error);
      setAnalysisResult("Error: Connection to HARVEY OS Backend failed.");
    } finally {
      setIsThinking(false);
      setSituation("");
    }
  };

  const radarData = habits
    ? [
        habits.deep_work_hours,
        habits.learning_hours,
        habits.workout,
        habits.networking_actions,
        leverageScore, // using leverage as the 5th point for the radar
      ]
    : [5, 5, 5, 5, 5];

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-[var(--color-harvey-dark)]">
      {/* 3D Canvas Background */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10], fov: 45 }}>
          <color attach="background" args={["#0a0a14"]} />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#c9a84c" />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#0ff" />
          
          <Suspense fallback={null}>
            <HolographicCore isThinking={isThinking} />
            <StrategicRadar
              data={radarData}
              labels={["Deep Work", "Learning", "Fitness", "Network", "Leverage"]}
              position={[-6, 0, -2]}
            />
            <DecisionTimeline decisions={decisions} position={[0, -4, 0]} />
            <OpportunityScanner opportunities={opportunities} radius={4} />
            <ThreatDetection threats={threats} />
            <NeuralThinking active={isThinking} />
            <Environment preset="night" />
          </Suspense>

          <OrbitControls 
            enableZoom={false} 
            enablePan={false} 
            autoRotate 
            autoRotateSpeed={0.5}
            maxPolarAngle={Math.PI / 1.5}
            minPolarAngle={Math.PI / 3}
          />
          
          <Effects disableGamma>
            {/* @ts-expect-error: unrealBloomPass is a valid three element via extend() */}
            <unrealBloomPass threshold={0.2} strength={1.5} radius={0.8} />
          </Effects>
        </Canvas>
      </div>

      {/* 2D Overlay UI */}
      <div className="absolute inset-0 z-10 pointer-events-none p-8 flex flex-col justify-between">
        
        {/* Top Header */}
        <header className="flex justify-between items-start w-full">
          <div>
            <h1 className="text-[var(--color-harvey-gold)] text-3xl font-bold tracking-widest drop-shadow-[0_0_10px_rgba(201,168,76,0.5)]">
              HARVEY OS
            </h1>
            <p className="text-[var(--color-harvey-cyan)] font-mono text-xs tracking-[0.2em] mt-1 opacity-80">
              STRATEGIC COMMAND CENTER
            </p>
          </div>
          <div className="flex gap-2">
            <div className={`w-3 h-3 rounded-full ${isThinking ? 'bg-yellow-400 animate-pulse' : 'bg-[var(--color-harvey-cyan)] shadow-[0_0_8px_#0ff]'}`}></div>
            <span className="text-xs font-mono uppercase text-gray-400">{isThinking ? 'Processing' : 'Online'}</span>
          </div>
        </header>

        {/* Right Data Panels */}
        <div className="absolute right-8 top-24 flex flex-col pointer-events-auto">
          <DataPanel title="Leverage Score" value={(leverageScore).toFixed(1)} subtitle="System Composite" delay={0.2} />
          <DataPanel title="Market State" value="Volatile" subtitle="Opportunity Index: High" delay={0.4} />
          <DataPanel title="Momentum" value="+12%" subtitle="7-day trajectory" delay={0.6} />
        </div>

        {/* Output Display */}
        <AnalysisOutput text={analysisResult} />

        {/* Bottom Input Area */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-2xl pointer-events-auto">
          <form onSubmit={handleAnalyze} className="relative group">
             <input
              type="text"
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              placeholder="Input situation parameters..."
              disabled={isThinking}
              className="w-full bg-[var(--color-harvey-panel)] border border-[var(--color-harvey-gold)]/30 rounded-full py-4 px-6 text-gray-200 font-mono placeholder-gray-500 focus:outline-none focus:border-[var(--color-harvey-cyan)] focus:shadow-[0_0_15px_rgba(0,255,255,0.3)] backdrop-blur-md transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isThinking || !situation.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-[var(--color-harvey-gold)] text-black font-bold uppercase tracking-wider text-xs px-6 py-2 rounded-full hover:bg-yellow-400 hover:shadow-[0_0_15px_rgba(201,168,76,0.6)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Analyze
            </button>
          </form>
        </div>

        {/* Voice Interface */}
        <div className="pointer-events-auto">
          <VoiceInterface />
        </div>
      </div>
    </main>
  );
}
