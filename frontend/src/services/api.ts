import axios from 'axios';

import { API_BASE_URL } from '../config';

export const TOKEN_KEY = 'vc_token';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  role: 'TEACHER' | 'STUDENT';
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export const login = (payload: LoginPayload) =>
  api.post<TokenResponse>('/auth/login/json', payload);

export const register = (payload: RegisterPayload) =>
  api.post<TokenResponse>('/auth/register', payload);

export const fetchProfile = () => api.get('/auth/me');

export default api;

