"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Text } from "@react-three/drei";

interface RadarProps {
  data: number[]; // Array of 5 values (0-10)
  labels: string[]; // Array of 5 labels
  position?: [number, number, number];
}

export default function StrategicRadar({ data, labels, position = [-5, 0, 0] }: RadarProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Generate a pentagon shape based on the data
  const shape = useMemo(() => {
    const s = new THREE.Shape();
    const numPoints = 5;
    const angleStep = (Math.PI * 2) / numPoints;

    for (let i = 0; i < numPoints; i++) {
        // Normalize 0-10 range to 0.5 - 2.5 radius
      const radius = 0.5 + (data[i] / 10) * 2;
      const x = Math.cos(i * angleStep - Math.PI / 2) * radius;
      const y = Math.sin(i * angleStep - Math.PI / 2) * radius;

      if (i === 0) s.moveTo(x, y);
      else s.lineTo(x, y);
    }
    s.closePath();
    return s;
  }, [data]);

  const geometry = useMemo(() => new THREE.ShapeGeometry(shape), [shape]);
  const edges = useMemo(() => new THREE.EdgesGeometry(geometry), [geometry]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2; // Slow rotation
      groupRef.current.position.y = Math.sin(_.clock.elapsedTime) * 0.2; // Floating effect
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Radar Fill */}
      <mesh geometry={geometry}>
        <meshBasicMaterial color="#0ff" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>

      {/* Radar Outline */}
      <lineSegments geometry={edges}>
        <lineBasicMaterial color="#0ff" linewidth={2} />
      </lineSegments>

      {/* Axis Lines and Labels */}
      {labels.map((label, i) => {
        const angle = i * ((Math.PI * 2) / 5) - Math.PI / 2;
        const x = Math.cos(angle) * 3;
        const y = Math.sin(angle) * 3;

        return (
          <group key={label}>
            <Text position={[x * 1.1, y * 1.1, 0]} fontSize={0.2} color="#c9a84c" anchorX="center" anchorY="middle">
              {label}
            </Text>
          </group>
        );
      })}
    </group>
  );
}
