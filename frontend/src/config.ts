const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
const baseHost = API_BASE_URL.replace(/\/api$/, '');
const wsHost =
  import.meta.env.VITE_WS_URL ??
  baseHost.replace('https', 'wss').replace('http', 'ws');
const WS_BASE_URL = `${wsHost}/ws`;

export { API_BASE_URL, WS_BASE_URL };

