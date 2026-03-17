"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Text, Line } from "@react-three/drei";

export interface DecisionNode {
  id: string;
  title: string;
  impact: number; // 0 to 10
  timestamp: string;
}

interface DecisionTimelineProps {
  decisions: DecisionNode[];
  position?: [number, number, number];
}

export default function DecisionTimeline({ decisions, position = [0, -4, 0] }: DecisionTimelineProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Generate points based on decisions
  const { points } = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    const spacing = 2; // Distance between nodes
    
    // Create a winding path or straight timeline. Let's do a gentle spiral or curve.
    decisions.forEach((_, i) => {
      const x = Math.sin(i * 0.5) * 2;
      const y = i * 0.5;
      const z = -i * spacing;
      pts.push(new THREE.Vector3(x, y, z));
    });

    // If no decisions, just create a default line
    if (pts.length < 2) {
      pts.push(new THREE.Vector3(0, 0, 0));
      pts.push(new THREE.Vector3(0, 0, -5));
    }

    const curve = new THREE.CatmullRomCurve3(pts);
    // Use curve to get smoother points for the line
    return { points: pts };
  }, [decisions]);

  useFrame((state) => {
    if (groupRef.current) {
      // Gentle floating animation
      groupRef.current.position.y += Math.sin(state.clock.elapsedTime * 0.5) * 0.002;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Connecting Line */}
      <Line 
        points={points} 
        color="#0ff" 
        lineWidth={2}
        transparent 
        opacity={0.4} 
      />

      {/* Decision Nodes */}
      {points.map((pt, i) => {
        const decision = decisions[i];
        if (!decision) return null;
        
        // Size node based on impact
        const nodeSize = 0.1 + (decision.impact / 10) * 0.2;
        
        return (
          <group key={decision.id} position={pt}>
            <mesh>
              <sphereGeometry args={[nodeSize, 16, 16]} />
              <meshStandardMaterial 
                color="#c9a84c" 
                emissive="#c9a84c"
                emissiveIntensity={0.8}
                transparent 
                opacity={0.9} 
              />
            </mesh>
            {/* Label */}
            <Text 
              position={[0.5, 0.2, 0]} 
              fontSize={0.15} 
              color="#eeeeee"
              anchorX="left" 
              anchorY="middle"
            >
              {decision.title}
            </Text>
          </group>
        );
      })}
    </group>
  );
}
