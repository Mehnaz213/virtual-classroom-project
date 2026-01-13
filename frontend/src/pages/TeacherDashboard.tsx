import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';

import EngagementMeter from '../components/EngagementMeter';
import LabelLegend from '../components/LabelLegend';
import ReportExportButton from '../components/ReportExportButton';
import TimelineChart from '../components/TimelineChart';
import { useAuth } from '../context/AuthContext';
import useInterval from '../hooks/useInterval';
import useSessionWebSocket from '../hooks/useWebSocket';
import api from '../services/api';
import type { DashboardResponse, SessionSummary } from '../types';

type SocketEnvelope = {
  type: string;
  payload?: DashboardResponse;
  timestamp?: string;
  enabled?: unknown;
};

const isSocketEnvelope = (value: unknown): value is SocketEnvelope => {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  return typeof (value as { type?: unknown }).type === 'string';
};

const TeacherDashboard = () => {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionSummary | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [topic, setTopic] = useState('');
  const [creating, setCreating] = useState(false);
  const [lockMode, setLockMode] = useState(false);

  const loadSessions = useCallback(async () => {
    const { data } = await api.get<SessionSummary[]>('/class/mine');
    setSessions(data);
    if (!selectedSession && data.length) {
      setSelectedSession(data[0]);
    }
  }, [selectedSession]);

  const loadDashboard = useCallback(async () => {
    if (!selectedSession) {
      return;
    }
    const { data } = await api.get<DashboardResponse>(`/class/${selectedSession.id}/dashboard`);
    setDashboard(data);
  }, [selectedSession]);

  useEffect(() => {
    loadSessions().catch((err) => console.error(err));
  }, [loadSessions]);

  useEffect(() => {
    if (selectedSession) {
      loadDashboard().catch((err) => console.error(err));
    }
  }, [selectedSession, loadDashboard]);

  useInterval(() => {
    loadDashboard().catch((err) => console.error(err));
  }, selectedSession ? 5000 : null);

  const handleCreateSession = async (event: FormEvent) => {
    event.preventDefault();
    if (!topic.trim()) {
      return;
    }
    setCreating(true);
    try {
      const { data } = await api.post('/class/create', { topic });
      const summary: SessionSummary = {
        ...data,
        attendee_count: 0,
        avg_engagement: 0,
      };
      setSessions((prev) => [summary, ...prev]);
      setSelectedSession(summary);
      setTopic('');
    } finally {
      setCreating(false);
    }
  };

  const toggleLockMode = async (enabled: boolean) => {
    if (!selectedSession) return;
    await api.post(`/class/${selectedSession.id}/lock`, { enabled });
    setLockMode(enabled);
  };

  const handleSocketMessage = useCallback((payload: unknown) => {
    if (!isSocketEnvelope(payload)) {
      return;
    }
    if (payload.type === 'snapshot' && payload.payload) {
      setDashboard(payload.payload);
      return;
    }
    if (payload.type === 'event') {
      const message = `Event received at ${payload.timestamp ?? new Date().toISOString()}`;
      setAlerts((prev) => [message, ...prev].slice(0, 6));
    }
    if (payload.type === 'lock_mode') {
      setLockMode(Boolean(payload.enabled));
    }
  }, []);

  useSessionWebSocket(selectedSession?.id ?? null, handleSocketMessage);

  const attendance = dashboard?.attendance ?? [];

  const selectedCode = selectedSession?.code ?? '—';

  return (
    <main className="page-layout">
      <header className="page-header">
        <div>
          <h2>Teacher Dashboard</h2>
          <p className="muted">
            Monitor live engagement, detect tab switching, and export compliance-ready reports.
          </p>
        </div>
        <div className="header-actions">
          <span>{user?.full_name}</span>
          <Link to="/labeler" className="link-btn">
            Labeler
          </Link>
          <button type="button" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <section className="grid two-col">
        <div className="card">
          <header className="card-header">
            <h3>Start a Session</h3>
          </header>
          <form onSubmit={handleCreateSession} className="create-form">
            <input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Topic (e.g., Algebra Basics)"
            />
            <button type="submit" disabled={creating}>
              {creating ? 'Creating…' : 'Create & Go Live'}
            </button>
          </form>
        </div>
        <div className="card">
          <header className="card-header">
            <h3>Active Sessions</h3>
          </header>
          <ul className="session-list">
            {sessions.map((session) => {
              const isActive = selectedSession?.id === session.id;
              return (
                <li key={session.id}>
                  <button
                    type="button"
                    className={`session-button ${isActive ? 'selected' : ''}`}
                    onClick={() => setSelectedSession(session)}
                  >
                    <div>
                      <strong>{session.topic}</strong>
                      <p className="muted">
                        Code {session.code} — {new Date(session.start_time).toLocaleTimeString()}
                      </p>
                    </div>
                    <span>{Math.round(session.avg_engagement * 100)}%</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      </section>

      {dashboard && (
        <>
          <section className="grid three-col">
            <EngagementMeter ratio={dashboard.engagement_ratio} />
            <div className="card">
              <header className="card-header">
                <h3>Session Details</h3>
                <span className="badge">{selectedCode}</span>
              </header>
              <p>Students present: {attendance.length}</p>
              <p>Tab alerts: {dashboard.tab_switch_alerts.length}</p>
              <p>Lock violations: {(dashboard.lock_violations || []).length}</p>
              <div className="lock-controls">
                <label>
                  <input
                    type="checkbox"
                    checked={lockMode}
                    onChange={(e) => toggleLockMode(e.target.checked)}
                  />
                  Enforce lock mode for everyone
                </label>
              </div>
              <ReportExportButton sessionId={dashboard.session_id} />
              {selectedSession && (
                <button
                  type="button"
                  onClick={async () => {
                    if (confirm('End this session? Students will no longer be able to join.')) {
                      try {
                        await api.post(`/class/${selectedSession.id}/end`);
                        await loadSessions();
                        setSelectedSession(null);
                        setDashboard(null);
                      } catch (err) {
                        console.error('Failed to end session', err);
                      }
                    }
                  }}
                  className="btn-danger"
                >
                  End Session
                </button>
              )}
            </div>
            <div className="card alerts">
              <header className="card-header">
                <h3>Live Alerts</h3>
              </header>
              <ul>
                {[
                  ...dashboard.sleepy_alerts,
                  ...dashboard.tab_switch_alerts,
                  ...(dashboard.lock_violations || []),
                  ...alerts
                ]
                  .slice(0, 8)
                  .map((alert, idx) => (
                  <li key={`${alert}-${idx}`}>{alert}</li>
                ))}
              </ul>
            </div>
            <LabelLegend data={dashboard.label_breakdown} />
          </section>

          <section className="grid two-col">
            <div className="card">
              <header className="card-header">
                <h3>Attendance</h3>
              </header>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Lock Mode</th>
                      <th>Last Seen</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendance.map((row) => (
                      <tr key={row.attendance_id}>
                        <td>{row.student_name}</td>
                        <td>{row.lock_mode ? 'On' : 'Off'}</td>
                        <td>{new Date(row.last_seen_at).toLocaleTimeString()}</td>
                        <td>{row.latest_level}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <TimelineChart data={dashboard.timeline} />
          </section>
        </>
      )}
    </main>
  );
};

export default TeacherDashboard;

