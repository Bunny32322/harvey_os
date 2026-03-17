"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Mesh, MeshStandardMaterial } from "three";

export default function HolographicCore({ isThinking }: { isThinking: boolean }) {
  const meshRef = useRef<Mesh>(null);
  const materialRef = useRef<MeshStandardMaterial>(null);

  useFrame((state, delta) => {
    if (meshRef.current) {
      // Base rotation
      const speed = isThinking ? 2.5 : 0.5;
      meshRef.current.rotation.y += delta * speed;
      meshRef.current.rotation.x += delta * (speed * 0.5);

      // Pulsing effect
      const scale = 1 + Math.sin(state.clock.elapsedTime * (isThinking ? 8 : 2)) * 0.05;
      meshRef.current.scale.set(scale, scale, scale);
    }

    if (materialRef.current) {
      // Glow intensity based on thinking state
      const targetEmissive = isThinking ? 2.0 : 0.5;
      materialRef.current.emissiveIntensity += (targetEmissive - materialRef.current.emissiveIntensity) * 0.1;
    }
  });

  return (
    <group>
      {/* Outer wireframe */}
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2, 1]} />
        <meshStandardMaterial
          ref={materialRef}
          color="#c9a84c"
          emissive="#c9a84c"
          emissiveIntensity={0.5}
          wireframe
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Inner solid pseudo-core */}
      <mesh>
        <octahedronGeometry args={[1, 0]} />
        <meshStandardMaterial color="#0ff" emissive="#0ff" emissiveIntensity={0.2} transparent opacity={0.3} />
      </mesh>
    </group>
  );
}
