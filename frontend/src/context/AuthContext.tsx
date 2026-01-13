import type { PropsWithChildren } from 'react';
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { fetchProfile, login as loginRequest, register as registerRequest, TOKEN_KEY } from '../services/api';

export type UserProfile = {
  id: number;
  email: string;
  full_name: string;
  role: 'teacher' | 'student';
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  role: 'teacher' | 'student';
};

type AuthContextValue = {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue>({
  user: null,
  token: null,
  loading: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

const USER_KEY = 'vc_user';

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<UserProfile | null>(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as UserProfile) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token || user) {
      return;
    }
    (async () => {
      try {
        const { data } = await fetchProfile();
        setUser(data);
        localStorage.setItem(USER_KEY, JSON.stringify(data));
      } catch {
        setToken(null);
        localStorage.removeItem(TOKEN_KEY);
      }
    })();
  }, [token, user]);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const { data } = await loginRequest({ email, password });
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      const profile = await fetchProfile();
      setUser(profile.data);
      localStorage.setItem(USER_KEY, JSON.stringify(profile.data));
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    setLoading(true);
    try {
      const { data } = await registerRequest(payload);
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      const profile = await fetchProfile();
      setUser(profile.data);
      localStorage.setItem(USER_KEY, JSON.stringify(profile.data));
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      register,
      logout,
    }),
    [loading, login, register, logout, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);

