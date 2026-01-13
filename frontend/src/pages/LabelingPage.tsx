import { useEffect, useMemo, useState } from 'react';

import { getLabelColor } from '../utils/labels';
import type { AttentionLabel } from '../types';

const LABELS: AttentionLabel[] = [
  'focused',
  'looking_left',
  'looking_right',
  'looking_up',
  'looking_down',
  'engaged',
  'partial_engaged',
  'sleepy',
  'distracted_by_multi_face',
  'no_face',
  'unknown',
];

type Frame = {
  id: string;
  image: string;
};

const generatePlaceholderFrames = (): Frame[] =>
  Array.from({ length: 12 }).map((_, index) => ({
    id: `frame-${index}`,
    image: `https://placehold.co/320x180?text=Frame+${index + 1}`,
  }));

const LabelingPage = () => {
  const [frames] = useState<Frame[]>(generatePlaceholderFrames());
  const [index, setIndex] = useState(0);
  const [labels, setLabels] = useState<Record<string, AttentionLabel>>({});
  const currentFrame = frames[index];

  const exportPayload = useMemo(
    () =>
      frames.map((frame) => ({
        id: frame.id,
        label: labels[frame.id] ?? null,
        source: frame.image,
      })),
    [frames, labels],
  );

  const handleLabel = (label: AttentionLabel) => {
    setLabels((prev) => ({ ...prev, [currentFrame.id]: label }));
    setIndex((prev) => Math.min(frames.length - 1, prev + 1));
  };

  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      const key = Number(event.key);
      if (Number.isNaN(key)) return;
      const label = LABELS[key - 1];
      if (label) {
        handleLabel(label);
      }
    };
    window.addEventListener('keydown', listener);
    return () => window.removeEventListener('keydown', listener);
  }, [currentFrame]);

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'labels.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="page-layout">
      <header className="page-header">
        <div>
          <h2>Labeling UI</h2>
          <p className="muted">Keyboard shortcuts 1..9 assign labels quickly.</p>
        </div>
        <button type="button" onClick={handleExport}>
          Export labels
        </button>
      </header>
      <section className="grid two-col">
        <div className="card">
          <header className="card-header">
            <h3>Preview #{index + 1}</h3>
          </header>
          <img src={currentFrame.image} alt="" style={{ width: '100%', borderRadius: '12px' }} />
        </div>
        <div className="card">
          <header className="card-header">
            <h3>Label</h3>
          </header>
          <div className="label-buttons">
            {LABELS.map((label, idx) => (
              <button
                type="button"
                key={label}
                style={{ borderColor: getLabelColor(label) }}
                className={labels[currentFrame.id] === label ? 'selected' : ''}
                onClick={() => handleLabel(label)}
              >
                {idx + 1}. {label.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
};

export default LabelingPage;


