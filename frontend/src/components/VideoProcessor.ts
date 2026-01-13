import type { AttentionLabel, LabelConfidence } from '../types';
import { ATTENTION_LABELS } from '../utils/labels';

export type CalibrationData = {
  yawOffset: number;
  pitchOffset: number;
};

export type AttentionInference = {
  labels: LabelConfidence[];
  gaze: { yaw: number; pitch: number };
  headPose: { x: number; y: number; z: number };
  eyesOpen: number;
  facePresent: boolean;
  confidence: number;
};

const normalizeLabels = (items: LabelConfidence[]) => {
  const map = new Map<AttentionLabel, number>();
  items.forEach(({ name, confidence }) => {
    const prev = map.get(name) ?? 0;
    map.set(name, Math.max(prev, confidence));
  });
  return Array.from(map.entries())
    .map(([name, confidence]) => ({ name, confidence }))
    .sort((a, b) => b.confidence - a.confidence);
};

const detectFaceAndGaze = (ctx: CanvasRenderingContext2D, w: number, h: number) => {
  const imageData = ctx.getImageData(0, 0, w, h);
  const { data } = imageData;
  
  const centerX = w / 2;
  const centerY = h / 2;
  
  // Divide frame into left and right halves
  let leftHalfSkin = 0;
  let rightHalfSkin = 0;
  let topHalfSkin = 0;
  let bottomHalfSkin = 0;
  let totalSkin = 0;
  let faceSumX = 0;
  let faceSumY = 0;
  
  // Scan entire frame for skin pixels
  for (let y = 0; y < h; y += 2) {
    for (let x = 0; x < w; x += 2) {
      const idx = (y * w + x) * 4;
      const r = data[idx];
      const g = data[idx + 1];
      const b = data[idx + 2];
      
      // Skin tone detection
      const isSkin = (
        r > 95 && g > 40 && b > 20 &&
        r > g && r > b &&
        Math.abs(r - g) > 15 &&
        r - g < 100 &&
        (r + g + b) > 200
      );
      
      if (isSkin) {
        totalSkin++;
        faceSumX += x;
        faceSumY += y;
        
        // Track which half has more skin
        if (x < centerX) leftHalfSkin++;
        else rightHalfSkin++;
        
        if (y < centerY) topHalfSkin++;
        else bottomHalfSkin++;
      }
    }
  }
  
  const faceDetected = totalSkin > 200;
  
  if (!faceDetected) {
    return {
      facePresent: false,
      yaw: 0,
      pitch: 0,
      eyesOpen: 0,
      confidence: 0.1,
    };
  }
  
  const faceCenterX = faceSumX / totalSkin;
  const faceCenterY = faceSumY / totalSkin;
  
  // CRITICAL: Accurate left/right detection
  // When you look LEFT: your face moves RIGHT in the frame (more skin on right half)
  // When you look RIGHT: your face moves LEFT in the frame (more skin on left half)
  
  // Calculate asymmetry ratio
  const horizontalAsymmetry = (rightHalfSkin - leftHalfSkin) / totalSkin;
  
  // Yaw calculation: NEGATIVE asymmetry = looking RIGHT, POSITIVE = looking LEFT
  const yaw = -horizontalAsymmetry * 80; // Amplify for sensitivity
  
  // Pitch calculation
  const verticalAsymmetry = (bottomHalfSkin - topHalfSkin) / totalSkin;
  const pitch = verticalAsymmetry * 60;
  
  // Better eye openness detection
  let eyeRegionBrightness = 0;
  let eyePixels = 0;
  const eyeY = Math.max(0, faceCenterY - 25);
  const eyeHeight = 20;
  
  for (let y = eyeY; y < Math.min(h, eyeY + eyeHeight); y++) {
    for (let x = Math.max(0, faceCenterX - 40); x < Math.min(w, faceCenterX + 40); x++) {
      const idx = (Math.floor(y) * w + Math.floor(x)) * 4;
      const brightness = (data[idx] + data[idx + 1] + data[idx + 2]) / 3;
      eyeRegionBrightness += brightness;
      eyePixels++;
    }
  }
  
  const avgEyeBrightness = eyePixels > 0 ? eyeRegionBrightness / eyePixels : 128;
  const eyesOpen = Math.min(1, Math.max(0.4, avgEyeBrightness / 170));
  
  return {
    facePresent: true,
    yaw,
    pitch,
    eyesOpen,
    confidence: Math.min(0.9, totalSkin / 800),
  };
};

const heuristicLabels = (yaw: number, pitch: number, eyesOpen: number, facePresent: boolean): LabelConfidence[] => {
  const labels: LabelConfidence[] = [];
  const add = (name: AttentionLabel, confidence: number) =>
    labels.push({ name, confidence: Math.min(1, Math.max(0, confidence)) });

  if (!facePresent) {
    add('no_face', 0.95);
    return normalizeLabels(labels);
  }

  if (eyesOpen < 0.4) {
    add('sleepy', 0.9);
    return normalizeLabels(labels);
  }

  const absYaw = Math.abs(yaw);
  const absPitch = Math.abs(pitch);

  // Ultra-sensitive thresholds for accurate left/right detection
  if (absYaw < 5 && absPitch < 5) {
    // Looking straight - focused
    add('focused', 0.94);
    add('engaged', 0.90);
  }
  else if (yaw > 5 && absYaw > absPitch) {
    // Looking RIGHT - face appears on LEFT side of frame
    const conf = Math.min(0.97, 0.75 + absYaw / 30);
    add('looking_right', conf);
    if (absYaw < 15) add('partial_engaged', 0.5);
  }
  else if (yaw < -5 && absYaw > absPitch) {
    // Looking LEFT - face appears on RIGHT side of frame
    const conf = Math.min(0.97, 0.75 + absYaw / 30);
    add('looking_left', conf);
    if (absYaw < 15) add('partial_engaged', 0.5);
  }
  else if (pitch > 8 && absPitch > absYaw) {
    // Looking down
    const conf = Math.min(0.95, 0.65 + absPitch / 40);
    add('looking_down', conf);
    if (absPitch < 20) add('partial_engaged', 0.5);
  }
  else if (pitch < -8 && absPitch > absYaw) {
    // Looking up
    const conf = Math.min(0.95, 0.65 + absPitch / 40);
    add('looking_up', conf);
    if (absPitch < 20) add('partial_engaged', 0.5);
  }
  else {
    // Slightly off center
    add('engaged', 0.78);
    add('partial_engaged', 0.68);
  }

  return normalizeLabels(labels);
};

export const runAttentionInference = async (
  video: HTMLVideoElement,
  canvas: HTMLCanvasElement,
  calibration?: CalibrationData | null,
): Promise<AttentionInference | null> => {
  const ctx = canvas.getContext('2d');
  if (!ctx || video.readyState < 2) {
    return null;
  }

  const w = 320;
  const h = 240;
  canvas.width = w;
  canvas.height = h;
  ctx.drawImage(video, 0, 0, w, h);

  const detection = detectFaceAndGaze(ctx, w, h);
  
  // Apply calibration
  const calibratedYaw = detection.yaw - (calibration?.yawOffset ?? 0);
  const calibratedPitch = detection.pitch - (calibration?.pitchOffset ?? 0);

  const labels = heuristicLabels(calibratedYaw, calibratedPitch, detection.eyesOpen, detection.facePresent);
  const headPose = { x: calibratedYaw, y: calibratedPitch, z: 0 };

  console.log('[VideoProcessor] Detection:', {
    facePresent: detection.facePresent,
    rawYaw: detection.yaw.toFixed(1),
    calibratedYaw: calibratedYaw.toFixed(1),
    pitch: calibratedPitch.toFixed(1),
    eyesOpen: detection.eyesOpen.toFixed(2),
    topLabel: labels[0]?.name,
    confidence: labels[0]?.confidence.toFixed(2),
  });

  return {
    labels,
    gaze: { yaw: calibratedYaw, pitch: calibratedPitch },
    headPose,
    eyesOpen: detection.eyesOpen,
    facePresent: detection.facePresent,
    confidence: detection.confidence,
  };
};

export const labelsToEngagement = (labels: LabelConfidence[]): 'ENGAGED' | 'PARTIAL' | 'NOT_ENGAGED' => {
  const top = labels[0]?.name;
  if (!top) return 'PARTIAL';
  if (top === 'sleepy' || top === 'no_face' || top === 'distracted_by_multi_face') return 'NOT_ENGAGED';
  if (top === 'focused' || top === 'engaged') return 'ENGAGED';
  return 'PARTIAL';
};
