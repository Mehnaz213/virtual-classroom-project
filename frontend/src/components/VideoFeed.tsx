import { useCallback, useEffect, useRef, useState } from 'react';

import api from '../services/api';
import type { LabelConfidence } from '../types';
import { ATTENTION_LABEL_COLORS, formatLabel } from '../utils/labels';
import type { CalibrationData } from './VideoProcessor';
import { labelsToEngagement, runAttentionInference } from './VideoProcessor';

type Props = {
  sessionId: number;
  attendanceId: number;
  tabHidden: boolean;
  lockMode: boolean;
};

const FRAME_INTERVAL_MS = 1500; // Update every 1.5 seconds for more responsive monitoring

const CALIBRATION_KEY = 'focusmate_calibration';

const VideoFeed = ({ sessionId, attendanceId, tabHidden, lockMode }: Props) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [status, setStatus] = useState('Initializing camera…');
  const [calibration, setCalibration] = useState<CalibrationData | null>(() => {
    const raw = localStorage.getItem(CALIBRATION_KEY);
    return raw ? (JSON.parse(raw) as CalibrationData) : null;
  });
  const [lastLabel, setLastLabel] = useState('n/a');
  const [labelSummary, setLabelSummary] = useState<LabelConfidence[]>([]);

  useEffect(() => {
    let stream: MediaStream | null = null;
    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 320, height: 240 },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          try {
            await videoRef.current.play();
          } catch (playErr) {
            console.error('Video autoplay blocked', playErr);
          }
        }
        setStatus('Camera ready. Capturing frames.');
      } catch (err) {
        console.error('Camera permission denied', err);
        setStatus('Unable to access webcam. Please allow camera permissions.');
      }
    };
    startCamera();
    return () => {
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const runCalibration = useCallback(async () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) {
      console.log('[Calibration] Missing canvas or video');
      alert('Camera not ready. Please wait for video to load.');
      return;
    }
    console.log('[Calibration] Starting calibration...');
    const inference = await runAttentionInference(video, canvas, null);
    console.log('[Calibration] Inference result:', inference);
    if (!inference) {
      alert('Could not detect face. Please ensure your face is visible and try again.');
      return;
    }
    const next = { yawOffset: inference.gaze.yaw, pitchOffset: inference.gaze.pitch };
    setCalibration(next);
    localStorage.setItem(CALIBRATION_KEY, JSON.stringify(next));
    setStatus('Calibration captured. Continue monitoring.');
    setLastLabel(inference.labels[0]?.name ?? 'n/a');
    setLabelSummary(inference.labels);
    console.log('[Calibration] Calibration complete:', next);
  }, []);

  // Continuous face detection loop (runs even without session)
  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) {
      console.log('[VideoFeed] Missing canvas or video element');
      return;
    }
    let cancelled = false;
    
    const runDetection = async () => {
      if (video.readyState < 2) {
        return;
      }
      
      const inference = await runAttentionInference(video, canvas, calibration);
      if (inference && !cancelled) {
        const topLabel = inference.labels[0]?.name ?? 'n/a';
        setLastLabel(topLabel);
        setLabelSummary(inference.labels);
        setStatus(`Detecting: ${topLabel.replace(/_/g, ' ').toUpperCase()} | Face: ${inference.facePresent ? '✓' : '✗'} | Gaze: ${inference.gaze.yaw.toFixed(0)}°, ${inference.gaze.pitch.toFixed(0)}°`);
        console.log('[VideoFeed] Detection:', topLabel, 'Face:', inference.facePresent, 'Gaze:', inference.gaze);
      }
    };
    
    const detectionInterval = window.setInterval(runDetection, 500);
    return () => {
      cancelled = true;
      window.clearInterval(detectionInterval);
    };
  }, [calibration]);

  // Frame sending loop (only when in session)
  useEffect(() => {
    if (!sessionId || !attendanceId) {
      console.log('[VideoFeed] Missing sessionId or attendanceId - detection still running but not sending to backend');
      return;
    }
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) {
      console.log('[VideoFeed] Missing canvas or video element');
      return;
    }
    let cancelled = false;
    const sendFrame = async () => {
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.log('[VideoFeed] No canvas context');
        return;
      }
      if (video.readyState < 2) {
        console.log('[VideoFeed] Video not ready, readyState:', video.readyState);
        return;
      }
      
      console.log('[VideoFeed] Running inference...');
      const dataUrl = canvas.toDataURL('image/jpeg', 0.5);
      const payload = dataUrl.split(',')[1];

      const inference = await runAttentionInference(video, canvas, calibration);
      console.log('[VideoFeed] Inference result:', inference);
      const topLabel = inference?.labels?.[0]?.name ?? 'n/a';
      const clientLevel = inference ? labelsToEngagement(inference.labels) : undefined;
      
      // Update UI immediately with inference results
      if (inference && !cancelled) {
        console.log('[VideoFeed] Inference SUCCESS:', {
          topLabel,
          gaze: inference.gaze,
          eyesOpen: inference.eyesOpen,
          facePresent: inference.facePresent,
          labels: inference.labels.slice(0, 3)
        });
        setLastLabel(topLabel);
        setLabelSummary(inference.labels);
        setStatus(`Analyzing... Gaze: ${inference.gaze.yaw.toFixed(1)}°, ${inference.gaze.pitch.toFixed(1)}° | Eyes: ${(inference.eyesOpen * 100).toFixed(0)}% | Face: ${inference.facePresent ? 'Yes' : 'No'}`);
      } else {
        console.log('[VideoFeed] No inference result or cancelled');
      }
      
      try {
        const { data } = await api.post('/events/frame', {
          session_id: sessionId,
          attendance_id: attendanceId,
          frame_b64: payload,
          tab_switch: tabHidden,
          multiple_faces: false,
          client_level: clientLevel,
          attention_score: inference?.eyesOpen,
          labels: inference?.labels,
          gaze: inference?.gaze,
          head_pose: inference?.headPose,
          face_present: inference?.facePresent,
          confidence: inference?.confidence,
          reason: lockMode ? 'lock-mode-stream' : 'standard',
        });
        if (!cancelled) {
          setStatus(`Backend ${data.level} | Model ${topLabel}`);
          setLastLabel(topLabel);
          setLabelSummary(inference?.labels ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setStatus('Dropped frame (network). Retrying…');
        }
        console.error(err);
      }
    };

    const interval = window.setInterval(sendFrame, FRAME_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [attendanceId, calibration, lockMode, sessionId, tabHidden]);

  return (
    <div className="card video-card">
      <header className="card-header">
        <h3>Webcam Feed</h3>
        {lockMode && <span className="badge badge-green">Lock mode</span>}
      </header>
      <video ref={videoRef} autoPlay muted playsInline className="video-feed" />
      <canvas ref={canvasRef} className="hidden-canvas" />
      <p className="muted">{status}</p>
      <div style={{ 
        padding: '10px', 
        background: 'rgba(0,0,0,0.3)', 
        borderRadius: '8px',
        marginTop: '10px'
      }}>
        <p style={{ fontSize: '18px', fontWeight: 'bold', margin: '5px 0' }}>
          Current: {lastLabel.replace(/_/g, ' ').toUpperCase()}
        </p>
        <p style={{ fontSize: '12px', opacity: 0.8, margin: '5px 0' }}>
          💡 Tip: Look straight, then click "Run Calibration" for best accuracy
        </p>
      </div>
      {labelSummary.length > 0 && (
        <ul className="label-legend">
          {labelSummary.slice(0, 4).map((label) => (
            <li key={label.name}>
              <span>
                <span className="swatch" style={{ background: ATTENTION_LABEL_COLORS[label.name] }} />
                {formatLabel(label.name)}
              </span>
              <span>{Math.round(label.confidence * 100)}%</span>
            </li>
          ))}
        </ul>
      )}
      {!calibration && (
        <div className="alert alert-info">
          <strong>⚠️ Calibration Required:</strong> Please look straight at the camera and click "Run Calibration" for accurate detection.
        </div>
      )}
      <button type="button" onClick={runCalibration} className={!calibration ? 'btn-primary' : ''}>
        {calibration ? 'Re-run Calibration' : '🎯 Run Calibration (Required)'}
      </button>
      {calibration && (
        <p className="muted">
          ✓ Calibrated offsets: yaw {calibration.yawOffset.toFixed(1)}°, pitch {calibration.pitchOffset.toFixed(1)}°
        </p>
      )}
    </div>
  );
};

export default VideoFeed;

