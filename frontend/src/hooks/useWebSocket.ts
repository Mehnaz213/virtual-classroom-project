import { useEffect, useRef } from 'react';

import { WS_BASE_URL } from '../config';
import { useAuth } from '../context/AuthContext';

type MessageHandler = (data: unknown) => void;

const useSessionWebSocket = (sessionId: number | null, onMessage: MessageHandler) => {
  const { token } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId || !token) {
      return;
    }

    const url = `${WS_BASE_URL}/session/${sessionId}?token=${token}`;
    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        onMessage(payload);
      } catch {
        // ignore malformed payloads
      }
    };

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'ping' }));
    };

    const interval = window.setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 25000);

    return () => {
      window.clearInterval(interval);
      ws.close();
    };
  }, [sessionId, token, onMessage]);

  const send = (payload: unknown) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  };

  return { send };
};

export default useSessionWebSocket;

