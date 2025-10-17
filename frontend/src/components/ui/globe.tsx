"use client";
import React, { useEffect, useRef, useState } from "react";
import { Color, Scene, Fog, PerspectiveCamera, Vector3, Group, Raycaster, Vector2 } from "three";
import ThreeGlobe from "three-globe";
import { useThree, Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import countries from "../../data/globe.json";
// If TS complains about json modules, ensure resolveJsonModule is enabled.

const RING_PROPAGATION_SPEED = 3;
const aspect = 1.2;
const cameraZ = 300;

type Position = {
  order: number;
  startLat: number;
  startLng: number;
  endLat: number;
  endLng: number;
  arcAlt: number;
  color: string;
  /** 0..1 importance; >0 marks highlight */
  importance?: number;
  /** optional name for the location */
  name?: string;};

export type GlobeConfig = {
  pointSize?: number;
  globeColor?: string;
  showAtmosphere?: boolean;
  atmosphereColor?: string;
  atmosphereAltitude?: number;
  emissive?: string;
  emissiveIntensity?: number;
  shininess?: number;
  polygonColor?: string;
  ambientLight?: string;
  directionalLeftLight?: string;
  directionalTopLight?: string;
  pointLight?: string;
  arcTime?: number;
  arcLength?: number;
  rings?: number;
  maxRings?: number;
  initialPosition?: {
    lat: number;
    lng: number;
  };
  autoRotate?: boolean;
  autoRotateSpeed?: number;
  highlightedPoints?: string[];  // Names of points to highlight
  focusPoint?: {               // Point to rotate to
    lat: number;
    lng: number;
  };
};

interface WorldProps {
  globeConfig: GlobeConfig;
  data: Position[];
  onPointClick?: (position: Position) => void;
}

// rings index cache is generated per interval; no static cache needed

export const Globe = React.memo(function Globe({ globeConfig, data, onPointClick }: WorldProps) {
  const globeRef = useRef<ThreeGlobe | null>(null);
  const groupRef = useRef<Group | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const { camera, gl } = useThree();

  const defaultProps = {
    pointSize: 1,
    atmosphereColor: "#ffffff",
    showAtmosphere: true,
    atmosphereAltitude: 0.1,
    polygonColor: "rgba(255,255,255,0.7)",
    globeColor: "#1d072e",
    emissive: "#000000",
    emissiveIntensity: 0.1,
    shininess: 0.9,
    arcTime: 2000,
    arcLength: 0.9,
    rings: 1,
    maxRings: 3,
    ...globeConfig,
  };

  // Initialize globe only once
  useEffect(() => {
    if (!globeRef.current && groupRef.current) {
      globeRef.current = new ThreeGlobe();
      groupRef.current.add(globeRef.current as unknown as Group);
      setIsInitialized(true);
    }
  }, []);

  // Build material when globe is initialized or when relevant props change
  useEffect(() => {
    if (!globeRef.current || !isInitialized) return;

    const globeMaterial = globeRef.current.globeMaterial() as unknown as {
      color: Color;
      emissive: Color;
      emissiveIntensity: number;
      shininess: number;
    };
    // Use merged defaults so undefined values don't wash out the material
    globeMaterial.color = new Color(defaultProps.globeColor);
    globeMaterial.emissive = new Color(defaultProps.emissive);
    globeMaterial.emissiveIntensity = defaultProps.emissiveIntensity || 0.1;
    globeMaterial.shininess = defaultProps.shininess || 0.9;
  }, [
    isInitialized,
    defaultProps.globeColor,
    defaultProps.emissive,
    defaultProps.emissiveIntensity,
    defaultProps.shininess,
  ]);

  // Build data when globe is initialized or when data changes
  useEffect(() => {
    if (!globeRef.current || !isInitialized || !data) return;

    const arcs = data;
    const points: Array<{
      size: number;
      order: number;
      color: string;
      lat: number;
      lng: number;
      importance?: number;
      name?: string;
    }> = [];
    for (let i = 0; i < arcs.length; i++) {
      const arc = arcs[i];
      const importance = (arc as any).importance ?? 0;
      const name = (arc as any).name;
      points.push({
        size: defaultProps.pointSize,
        order: arc.order,
        color: arc.color,
        lat: arc.startLat,
        lng: arc.startLng,
        importance,
        name,
      });
      points.push({
        size: defaultProps.pointSize,
        order: arc.order,
        color: arc.color,
        lat: arc.endLat,
        lng: arc.endLng,
        importance,
        name,
      });
    }

    // remove duplicates for same lat and lng
    const filteredPoints = points.filter(
      (v, i, a) =>
        a.findIndex((v2) =>
          ["lat", "lng"].every(
            (k) => v2[k as "lat" | "lng"] === v[k as "lat" | "lng"],
          ),
        ) === i,
    );

    globeRef.current
      .hexPolygonsData(countries.features)
      .hexPolygonResolution(3)
      .hexPolygonMargin(0.5)
      .showAtmosphere(true)
      .atmosphereColor('#7aa2ff')
      .atmosphereAltitude(0.22)
      // brighter land to distinguish from oceans
      .hexPolygonColor(() => 'rgba(180,200,255,0.55)');

    globeRef.current
      .arcsData(data)
      .arcStartLat((d) => (d as { startLat: number }).startLat * 1)
      .arcStartLng((d) => (d as { startLng: number }).startLng * 1)
      .arcEndLat((d) => (d as { endLat: number }).endLat * 1)
      .arcEndLng((d) => (d as { endLng: number }).endLng * 1)
      .arcColor((e: any) => (e as { color: string }).color)
      .arcAltitude((e) => (e as { arcAlt: number }).arcAlt * 1)
      .arcStroke(() => [0.32, 0.28, 0.3][Math.round(Math.random() * 2)])
      .arcDashLength(defaultProps.arcLength)
      .arcDashInitialGap((e) => (e as { order: number }).order * 1)
      .arcDashGap(15)
      .arcDashAnimateTime(() => defaultProps.arcTime);

    globeRef.current
      .pointsData(filteredPoints)
      .pointColor((e: any) => {
        const isHighlighted = globeConfig.highlightedPoints?.includes(e.name);
        if (isHighlighted) return '#ffeb3b'; // Bright yellow for highlighted points
        return ((e.importance ?? 0) > 0 ? '#e6efff' : '#95aaff');
      })
      .pointsMerge(false) // Don't merge so we can click individual points
      .pointAltitude((e: any) => {
        const isHighlighted = globeConfig.highlightedPoints?.includes(e.name);
        return isHighlighted ? 0.02 : (((e.importance ?? 0) > 0 ? 0.01 : 0.005));
      })
      .pointRadius((e: any) => {
        const isHighlighted = globeConfig.highlightedPoints?.includes(e.name);
        return isHighlighted ? 2.0 : (((e.importance ?? 0) > 0 ? 1.2 : 0.8));
      })

    globeRef.current
      .ringsData([])
      .ringColor(() => defaultProps.polygonColor)
      .ringMaxRadius(defaultProps.maxRings)
      .ringPropagationSpeed(RING_PROPAGATION_SPEED)
      .ringRepeatPeriod(
        (defaultProps.arcTime * defaultProps.arcLength) / defaultProps.rings,
      );
  }, [
    isInitialized,
    data,
    defaultProps.pointSize,
    defaultProps.showAtmosphere,
    defaultProps.atmosphereColor,
    defaultProps.atmosphereAltitude,
    defaultProps.polygonColor,
    defaultProps.arcLength,
    defaultProps.arcTime,
    defaultProps.rings,
    defaultProps.maxRings,
  ]);

  // Handle rings animation with cleanup
  useEffect(() => {
    if (!globeRef.current || !isInitialized || !data) return;

    const interval = setInterval(() => {
      if (!globeRef.current) return;

      const newNumbersOfRings = genRandomNumbers(
        0,
        data.length,
        Math.floor((data.length * 4) / 5),
      );

      const highlighted = data
        .filter((d) => ((d as any).importance ?? 0) > 0)
        .map((d) => ({ lat: d.startLat, lng: d.startLng, color: '#dbe8ff' }));

      const ringsData = [
        ...highlighted,
        ...data
          .filter((_, i) => newNumbersOfRings.includes(i))
          .map((d) => ({ lat: d.startLat, lng: d.startLng, color: d.color })),
      ];

      globeRef.current.ringsData(ringsData);
    }, 2000);

    return () => {
      clearInterval(interval);
    };
  }, [isInitialized, data]);

  // Handle clicks on the globe - improved to detect points accurately
  useEffect(() => {
    if (!gl || !onPointClick || !isInitialized || !globeRef.current) return;

    const handleClick = (event: MouseEvent) => {
      // Calculate mouse position in normalized device coordinates
      const rect = gl.domElement.getBoundingClientRect();
      const mouse = new Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
      );

      // Create raycaster with larger threshold for easier clicking
      const raycaster = new Raycaster();
      raycaster.params.Points = { threshold: 5 }; // Larger threshold for easier clicking
      raycaster.setFromCamera(mouse, camera);

      if (!groupRef.current) return;

      // First, try to find point objects specifically
      const pointObjects = groupRef.current.children.filter(
        (child) => child.type === 'Points' || child.type === 'Mesh'
      );
      
      const pointIntersects = raycaster.intersectObjects(pointObjects, true);
      
      // If we hit a point object, try to match it to our data
      if (pointIntersects.length > 0) {
        const hitPoint = pointIntersects[0].point;
        
        // Convert hit point to lat/lng
        const radius = 100;
        const lat = Math.asin(hitPoint.y / radius) * (180 / Math.PI);
        const lng = Math.atan2(hitPoint.z, hitPoint.x) * (180 / Math.PI);
        
        // Find closest data point
        let closestPoint = null;
        let closestDistance = Infinity;
        
        for (const dataPoint of data) {
          const distance = Math.sqrt(
            Math.pow(dataPoint.startLat - lat, 2) + 
            Math.pow(dataPoint.startLng - lng, 2)
          );
          
          if (distance < closestDistance && distance < 15) {
            closestDistance = distance;
            closestPoint = dataPoint;
          }
        }
        
        if (closestPoint) {
          console.log('Clicked on:', closestPoint.name, 'at', closestPoint.startLat, closestPoint.startLng);
          onPointClick(closestPoint);
          return;
        }
      }
      
      // Fallback: check all objects if no point was directly hit
      const allIntersects = raycaster.intersectObjects(groupRef.current.children, true);
      if (allIntersects.length > 0) {
        const hitPoint = allIntersects[0].point;
        const radius = 100;
        const lat = Math.asin(hitPoint.y / radius) * (180 / Math.PI);
        const lng = Math.atan2(hitPoint.z, hitPoint.x) * (180 / Math.PI);
        
        let closestPoint = null;
        let closestDistance = Infinity;
        
        for (const dataPoint of data) {
          const distance = Math.sqrt(
            Math.pow(dataPoint.startLat - lat, 2) + 
            Math.pow(dataPoint.startLng - lng, 2)
          );
          
          if (distance < closestDistance && distance < 10) {
            closestDistance = distance;
            closestPoint = dataPoint;
          }
        }
        
        if (closestPoint) {
          console.log('Clicked near:', closestPoint.name);
          onPointClick(closestPoint);
        }
      }
    };

    gl.domElement.addEventListener('click', handleClick);
    gl.domElement.style.cursor = 'pointer';
    
    return () => {
      gl.domElement.removeEventListener('click', handleClick);
    };
  }, [gl, camera, onPointClick, data, isInitialized]);

  return <group ref={groupRef} />;
});

export function WebGLRendererConfig() {
  const { gl, size } = useThree();

  useEffect(() => {
    gl.setPixelRatio(window.devicePixelRatio);
    gl.setSize(size.width, size.height);
    gl.setClearColor(0xffaaff, 0);
  }, [gl, size]);

  return null;
}

export const World = React.memo(function World(props: WorldProps) {
  const { globeConfig } = props;
  const scene = new Scene();
  scene.fog = new Fog(0xffffff, 400, 2000);
  const controlsRef = useRef<any>(null);

  // Handle focusing on a point
  useEffect(() => {
    if (controlsRef.current && globeConfig.focusPoint) {
      const { lat, lng } = globeConfig.focusPoint;
      
      // Convert lat/lng to Euler rotation
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (90 - lng) * (Math.PI / 180);
      
      // Stop auto-rotation temporarily
      controlsRef.current.autoRotate = false;
      
      // Animate to the new position
      const targetRotation = {
        x: phi,
        y: theta,
      };
      
      // Simple animation
      const startRotation = {
        x: controlsRef.current.getPolarAngle(),
        y: controlsRef.current.getAzimuthalAngle(),
      };
      
      let start: number | null = null;
      const duration = 1000; // 1 second animation
      
      function animate(timestamp: number) {
        if (!start) start = timestamp;
        const progress = (timestamp - start) / duration;
        
        if (progress < 1) {
          controlsRef.current.setAzimuthalAngle(
            startRotation.y + (targetRotation.y - startRotation.y) * progress
          );
          controlsRef.current.setPolarAngle(
            startRotation.x + (targetRotation.x - startRotation.x) * progress
          );
          requestAnimationFrame(animate);
        } else {
          // Animation complete, resume auto-rotation
          controlsRef.current.autoRotate = true;
        }
      }
      
      requestAnimationFrame(animate);
    }
  }, [globeConfig.focusPoint]);

  return (
    <Canvas scene={scene} camera={new PerspectiveCamera(50, aspect, 180, 1800)}>
      <WebGLRendererConfig />
      <ambientLight color={globeConfig.ambientLight} intensity={0.6} />
      <directionalLight
        color={globeConfig.directionalLeftLight}
        position={new Vector3(-400, 100, 400)}
      />
      <directionalLight
        color={globeConfig.directionalTopLight}
        position={new Vector3(-200, 500, 200)}
      />
      <pointLight
        color={globeConfig.pointLight}
        position={new Vector3(-200, 500, 200)}
        intensity={0.8}
      />
      <Globe {...props} />
      <OrbitControls
        ref={controlsRef}
        enablePan={false}
        enableZoom={false}
        minDistance={cameraZ}
        maxDistance={cameraZ}
        autoRotateSpeed={1}
        autoRotate={true}
        minPolarAngle={Math.PI / 3.5}
        maxPolarAngle={Math.PI - Math.PI / 3}
      />
    </Canvas>
  );
});

export function hexToRgb(hex: string) {
  var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  hex = hex.replace(shorthandRegex, function (_, r, g, b) {
    return r + r + g + g + b + b;
  });

  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function genRandomNumbers(min: number, max: number, count: number) {
  const arr = [];
  while (arr.length < count) {
    const r = Math.floor(Math.random() * (max - min)) + min;
    if (arr.indexOf(r) === -1) arr.push(r);
  }

  return arr;
}
