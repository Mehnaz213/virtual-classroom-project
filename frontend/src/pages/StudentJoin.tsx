import { useCallback, useRef, useState } from 'react';
import type { FormEvent } from 'react';

import LockModeStatus from '../components/LockModeStatus';
import VideoFeed from '../components/VideoFeed';
import { useAuth } from '../context/AuthContext';
import useLockMode from '../hooks/useLockMode';
import useSessionWebSocket from '../hooks/useWebSocket';
import useVisibilityTracker from '../hooks/useVisibilityTracker';
import api from '../services/api';
import type { JoinResponse } from '../types';

type SocketMessage = {
  type: string;
  studentId?: number;
  enabled?: boolean;
  timestamp?: string;
  [key: string]: unknown;
};

const isSocketMessage = (value: unknown): value is SocketMessage => {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  const maybe = value as Partial<SocketMessage>;
  return typeof maybe.type === 'string';
};

const StudentJoin = () => {
  const { user, logout } = useAuth();
  const [sessionCode, setSessionCode] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [attendance, setAttendance] = useState<JoinResponse | null>(null);
  const [lockMode, setLockMode] = useState(false);
  const [tabHidden, setTabHidden] = useState(false);
  const [notice, setNotice] = useState('Enter the session code provided by your instructor.');
  const lastVisibilityPost = useRef(0);

  const { attempts, reEngage } = useLockMode(lockMode);

  const joined = Boolean(attendance && sessionId);

  const handleJoin = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setNotice('Validating session…');
      const { data: session } = await api.get(`/class/code/${sessionCode}`);
      const { data } = await api.post<JoinResponse>(`/class/${session.id}/join`, {
        code: sessionCode,
        lock_mode: lockMode,
      });
      setSessionId(session.id);
      setAttendance(data);
      setLockMode(data.lock_mode);
      setNotice(`Joined ${session.topic}. Waiting for live instructions…`);
    } catch (err) {
      console.error(err);
      setNotice('Unable to join. Check the code or if the class is live.');
    }
  };

  const sendVisibilityEvent = useCallback(
    async (visible: boolean) => {
      if (!sessionId || !attendance?.attendance_id) {
        console.log('[Tab Switch] Not in session, skipping event');
        return;
      }
      const now = Date.now();
      if (now - lastVisibilityPost.current < 1500) {
        console.log('[Tab Switch] Throttled, skipping event');
        return;
      }
      lastVisibilityPost.current = now;
      
      console.log(`[Tab Switch] Sending event: visible=${visible}, session=${sessionId}, attendance=${attendance.attendance_id}`);
      
      try {
        await api.post('/events/tab-switch', {
          session_id: sessionId,
          attendance_id: attendance.attendance_id,
          tab_visible: visible,
          event_type: 'tab_switch',
          timestamp: new Date().toISOString(),
          note: 'student-window'
        });
        console.log(`[Tab Switch] ✓ Event sent successfully`);
      } catch (err) {
        console.error('[Tab Switch] ✗ Failed to send event:', err);
      }
    },
    [attendance?.attendance_id, sessionId],
  );

  useVisibilityTracker((visible) => {
    setTabHidden(!visible);
    void sendVisibilityEvent(visible);
  });

  const handleSocketMessage = useCallback(
    (payload: unknown) => {
      if (!isSocketMessage(payload)) {
        return;
      }
      if (payload.type === 'lock_mode') {
        const target = payload.studentId;
        if (!target || target === user?.id) {
          const nextEnabled =
            typeof payload.enabled === 'boolean' ? payload.enabled : Boolean(payload.enabled);
          setLockMode(nextEnabled);
        }
      }
      if (payload.type === 'session_end') {
        setNotice('Session ended by instructor.');
      }
    },
    [user?.id],
  );

  useSessionWebSocket(sessionId, handleSocketMessage);

  return (
    <main className="page-layout">
      <header className="page-header">
        <div>
          <h2>Student Console</h2>
          <p className="muted">{notice}</p>
        </div>
        <div className="header-actions">
          <span>{user?.full_name}</span>
          <button type="button" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      {!joined && (
        <section className="card join-card">
          <form onSubmit={handleJoin} className="join-form">
            <label>
              Session Code
              <input
                value={sessionCode}
                onChange={(e) => setSessionCode(e.target.value.toUpperCase())}
                maxLength={8}
                placeholder="MATH101"
              />
            </label>
            <label className="lock-toggle">
              <input
                type="checkbox"
                checked={lockMode}
                onChange={(e) => setLockMode(e.target.checked)}
              />
              Opt into lock mode immediately
            </label>
            <button type="submit" disabled={!sessionCode}>
              Join Session
            </button>
          </form>
        </section>
      )}

      {joined && attendance && sessionId && (
        <section className="grid two-col">
          <VideoFeed
            sessionId={sessionId}
            attendanceId={attendance.attendance_id}
            tabHidden={tabHidden}
            lockMode={lockMode}
          />
          <LockModeStatus enabled={lockMode} attempts={attempts} onReengage={reEngage} />
        </section>
      )}
    </main>
  );
};

export default StudentJoin;

