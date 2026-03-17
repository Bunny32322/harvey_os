"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Html } from "@react-three/drei";

export interface Opportunity {
  id: string;
  title: string;
  value: string;
  type: string;
}

interface OpportunityScannerProps {
  opportunities: Opportunity[];
  radius?: number;
}

export default function OpportunityScanner({ opportunities, radius = 4 }: OpportunityScannerProps) {
  const ringRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.y -= delta * 0.3; // Rotate counter-clockwise
    }
  });

  const cards = useMemo(() => {
    return opportunities.map((opp, index) => {
      const angle = (index / opportunities.length) * Math.PI * 2;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      return { ...opp, position: new THREE.Vector3(x, 0, z) };
    });
  }, [opportunities, radius]);

  // Ring geometry
  const ringGeometry = useMemo(() => new THREE.RingGeometry(radius - 0.05, radius + 0.05, 64), [radius]);
  const edges = useMemo(() => new THREE.EdgesGeometry(ringGeometry), [ringGeometry]);

  return (
    <group ref={ringRef} rotation={[-Math.PI / 4, 0, 0]}>
      {/* The scanning ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius - 0.05, radius + 0.05, 64]} />
        <meshBasicMaterial color="#0ff" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Ring Edges */}
      <lineSegments geometry={edges} rotation={[-Math.PI / 2, 0, 0]}>
        <lineBasicMaterial color="#0ff" transparent opacity={0.8} />
      </lineSegments>

      {/* Opportunity Cards */}
      {cards.map((card) => (
        <group key={card.id} position={card.position}>
          <mesh>
            <octahedronGeometry args={[0.2, 0]} />
            <meshStandardMaterial color="#c9a84c" emissive="#c9a84c" emissiveIntensity={1} />
          </mesh>
          <Html position={[0.3, 0.3, 0]} center className="pointer-events-none">
            <div className="glass-panel p-2 w-[150px] transform transition-transform hover:scale-110 pointer-events-auto">
              <div className="text-[var(--color-harvey-gold)] text-[10px] uppercase font-bold mb-1">
                {card.type}
              </div>
              <div className="text-gray-200 text-xs font-mono">{card.title}</div>
              <div className="text-[var(--color-harvey-cyan)] text-sm font-bold mt-1">
                {card.value}
              </div>
            </div>
          </Html>
        </group>
      ))}
    </group>
  );
}
