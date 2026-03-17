"use client";

import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function NeuralThinking({ active }: { active: boolean }) {
  const pointsRef = useRef<THREE.Points>(null);
  const materialRef = useRef<THREE.PointsMaterial>(null);

  const particleCount = 200;
  
  const [particleData] = useState(() => {
    const pos = new Float32Array(particleCount * 3);
    const ph = new Float32Array(particleCount);
    for (let i = 0; i < particleCount; i++) {
        // Random spread around the core
      pos[i * 3] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 8;
      ph[i] = Math.random() * Math.PI * 2;
    }
    return { positions: pos, phases: ph };
  });

  const { positions, phases } = particleData;

  const clampRadius = (r: number) => Math.max(1.5, Math.min(r, 6));

  useFrame((state) => {
    if (!active) {
        if (materialRef.current) materialRef.current.opacity *= 0.9; // Fast fade out
        return;
    }

    if (materialRef.current) {
        materialRef.current.opacity += (0.8 - materialRef.current.opacity) * 0.1; // Fade in
    }

    if (pointsRef.current) {
      const positionsAttr = pointsRef.current.geometry.attributes.position;
      const array = positionsAttr.array as Float32Array;
      
      for (let i = 0; i < particleCount; i++) {
        // Swirl around the core
        const x = array[i * 3];
        const z = array[i * 3 + 2];
        const angle = Math.atan2(z, x) + 0.05;
        const radius = Math.sqrt(x*x + z*z);
        
        array[i * 3] = Math.cos(angle) * clampRadius(radius + Math.sin(state.clock.elapsedTime * 5 + phases[i]) * 0.05);
        array[i * 3 + 1] += Math.sin(state.clock.elapsedTime * 3 + phases[i]) * 0.02;
        array[i * 3 + 2] = Math.sin(angle) * clampRadius(radius + Math.cos(state.clock.elapsedTime * 5 + phases[i]) * 0.05);
      }
      positionsAttr.needsUpdate = true;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={particleCount} array={positions} itemSize={3} args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial ref={materialRef} color="#0ff" size={0.05} transparent opacity={0} blending={THREE.AdditiveBlending} />
    </points>
  );
}
