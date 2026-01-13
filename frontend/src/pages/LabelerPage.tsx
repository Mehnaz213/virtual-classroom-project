import { useEffect, useMemo, useState } from 'react';

import api from '../services/api';
import type { TimelinePoint } from '../types';
import { ATTENTION_LABELS, formatLabel } from '../utils/labels';

type ReviewItem = TimelinePoint & { attendance_id?: number; meta?: { frame_url?: string } };

const LabelerPage = () => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  const current = items[index];

  useEffect(() => {
    const loadQueue = async () => {
      setLoading(true);
      try {
        const { data } = await api.get('/labeler/queue');
        setItems(data);
        setIndex(0);
      } catch (err) {
        console.error(err);
        setError('Unable to load queue.');
      } finally {
        setLoading(false);
      }
    };
    loadQueue().catch(console.error);
  }, []);

  const assignLabel = (label: string) => {
    if (!current) return;
    const updated: ReviewItem = {
      ...current,
      labels: [{ name: label as any, confidence: 1 }],
    };
    setItems((prev) => {
      const copy = [...prev];
      copy[index] = updated;
      return copy;
    });
    setMessage(`Assigned ${label} to frame ${index + 1}/${items.length}`);
  };

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const idx = Number(event.key) - 1;
      if (idx >= 0 && idx < ATTENTION_LABELS.length) {
        assignLabel(ATTENTION_LABELS[idx]);
      }
      if (event.key === 'ArrowRight') {
        setIndex((prev) => Math.min(prev + 1, Math.max(items.length - 1, 0)));
      }
      if (event.key === 'ArrowLeft') {
        setIndex((prev) => Math.max(prev - 1, 0));
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [items, index, current]);

  const exportLabels = () => {
    const blob = new Blob([JSON.stringify(items, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'focusmate-labels.json';
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const labelButtons = useMemo(
    () =>
      ATTENTION_LABELS.map((label) => (
        <button
          type="button"
          key={label}
          className={current?.labels?.[0]?.name === label ? 'selected' : ''}
          onClick={() => assignLabel(label)}
        >
          {label}
        </button>
      )),
    [assignLabel, current],
  );

  if (loading) {
    return (
      <main className="page-layout">
        <p>Loading labeling queue…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-layout">
        <p className="error-text">{error}</p>
      </main>
    );
  }

  if (!current) {
    return (
      <main className="page-layout">
        <p>No frames awaiting labeling.</p>
      </main>
    );
  }

  return (
    <main className="page-layout">
      <header className="page-header">
        <div>
          <h2>Labeling Console</h2>
          <p className="muted">
            Use keys 1–{ATTENTION_LABELS.length} to tag frames. Arrow keys to navigate. Export JSON to feed active
            learning / fine-tuning.
          </p>
        </div>
        <div className="header-actions">
          <button type="button" onClick={exportLabels}>
            Export Labels
          </button>
        </div>
      </header>

      <section className="grid two-col">
        <div className="card">
          <header className="card-header">
            <h3>
              Frame {index + 1} / {items.length}
            </h3>
            <span className="badge">{current.student_name}</span>
          </header>
          <img src={current.meta?.frame_url ?? ''} alt="frame" className="video-feed" />
          <p className="muted">{new Date(current.timestamp).toLocaleString()}</p>
          <div className="label-buttons">{labelButtons}</div>
        </div>
        <div className="card">
          <header className="card-header">
            <h3>Current Label</h3>
          </header>
          <p className="muted">
            {current.labels?.[0]
              ? `${formatLabel(current.labels[0].name)} (${Math.round(current.labels[0].confidence * 100)}%)`
              : 'Unlabeled'}
          </p>
          {message && <p className="muted">{message}</p>}
          <p className="muted">Keyboard shortcuts:</p>
          <ul className="label-legend">
            {ATTENTION_LABELS.map((label, idx) => (
              <li key={label}>
                <span>
                  <span className="swatch" />
                  {formatLabel(label)}
                </span>
                <span>Key {idx + 1}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
};

export default LabelerPage;


