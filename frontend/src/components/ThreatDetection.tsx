"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Html } from "@react-three/drei";

export interface Threat {
  id: string;
  title: string;
  level: "WARNING" | "CRITICAL";
  description: string;
}

interface ThreatDetectionProps {
  threats: Threat[];
}

export default function ThreatDetection({ threats }: ThreatDetectionProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  const hasThreats = threats.length > 0;
  const isCritical = threats.some(t => t.level === "CRITICAL");
  
  // Decide color based on level
  const color = isCritical ? "#ff0033" : "#ffaa00";

  useFrame((state, delta) => {
    if (meshRef.current) {
      if (hasThreats) {
        // Fast pulsation
        const speed = isCritical ? 10 : 5;
        const pulse = Math.sin(state.clock.elapsedTime * speed) * 0.1;
        meshRef.current.scale.set(1 + pulse, 1 + pulse, 1 + pulse);
        // Rotation
        meshRef.current.rotation.y += delta;
      } else {
        // Reset scale gracefully
        meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
      }
    }
  });

  if (!hasThreats) return null;

  return (
    <group position={[0, 0, 0]}>
      <mesh ref={meshRef}>
        {/* Large outer sphere that encompasses the core */}
        <sphereGeometry args={[3, 32, 32]} />
        <meshBasicMaterial 
          color={color} 
          wireframe 
          transparent 
          opacity={0.15} 
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* 2D Overlay for Threat Readout */}
      <Html position={[0, 3.5, 0]} center zIndexRange={[100, 0]}>
        <div className="flex flex-col gap-2 items-center pointer-events-none">
          {threats.map(threat => (
            <div 
              key={threat.id} 
              className={`px-4 py-2 border rounded-md backdrop-blur-md animate-pulse uppercase tracking-widest text-xs font-bold pointer-events-auto
              ${threat.level === 'CRITICAL' ? 'border-red-500 bg-red-900/30 text-red-400' : 'border-amber-500 bg-amber-900/30 text-amber-400'}
              `}
            >
              ⚠ {threat.title}
            </div>
          ))}
        </div>
      </Html>
    </group>
  );
}
