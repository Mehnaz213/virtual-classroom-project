import { useEffect, useRef } from 'react';
import api from '../services/api';

type TabSwitchDetectorProps = {
  sessionId: number | null;
  attendanceId: number | null;
  enabled: boolean;
};

const useTabSwitchDetector = ({ sessionId, attendanceId, enabled }: TabSwitchDetectorProps) => {
  const lastEventTime = useRef(0);
  const tabSwitchCount = useRef(0);

  const sendTabSwitchEvent = async (tabVisible: boolean) => {
    if (!sessionId || !attendanceId || !enabled) return;

    // Throttle events (max 1 per 2 seconds)
    const now = Date.now();
    if (now - lastEventTime.current < 2000) return;
    lastEventTime.current = now;

    if (!tabVisible) {
      tabSwitchCount.current++;
    }

    try {
      await api.post('/events/tab-switch', {
        session_id: sessionId,
        attendance_id: attendanceId,
        tab_visible: tabVisible,
        event_type: 'tab_switch',
        timestamp: new Date().toISOString(),
        tab_count: tabSwitchCount.current,
        note: 'built-in-detector'
      });
      
      console.log(`[Tab Switch] Event sent: visible=${tabVisible}, count=${tabSwitchCount.current}`);
    } catch (error) {
      console.error('[Tab Switch] Failed to send event:', error);
    }
  };

  useEffect(() => {
    if (!enabled) return;

    const handleVisibilityChange = () => {
      const isVisible = document.visibilityState === 'visible';
      sendTabSwitchEvent(isVisible);
    };

    const handleWindowBlur = () => {
      sendTabSwitchEvent(false);
    };

    const handleWindowFocus = () => {
      sendTabSwitchEvent(true);
    };

    const handlePageHide = () => {
      sendTabSwitchEvent(false);
    };

    // Add event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus);
    window.addEventListener('pagehide', handlePageHide);

    console.log('[Tab Switch] Detector enabled');

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('focus', handleWindowFocus);
      window.removeEventListener('pagehide', handlePageHide);
      console.log('[Tab Switch] Detector disabled');
    };
  }, [sessionId, attendanceId, enabled]);

  return { tabSwitchCount: tabSwitchCount.current };
};

export default useTabSwitchDetector;