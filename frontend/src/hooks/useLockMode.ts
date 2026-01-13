import { useCallback, useEffect, useState } from 'react';

const useLockMode = (enabled: boolean) => {
  const [attempts, setAttempts] = useState(0);

  const requestFullscreen = useCallback(async () => {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
      }
    } catch {
      setAttempts((prev) => prev + 1);
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
      return undefined;
    }

    requestFullscreen();
    const listenerOptions: AddEventListenerOptions = { capture: true };
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        setAttempts((prev) => prev + 1);
        requestFullscreen();
      }
    };
    window.addEventListener('keydown', handleKey, listenerOptions);
    return () => window.removeEventListener('keydown', handleKey, listenerOptions);
  }, [enabled, requestFullscreen]);

  return { attempts, reEngage: requestFullscreen };
};

export default useLockMode;

