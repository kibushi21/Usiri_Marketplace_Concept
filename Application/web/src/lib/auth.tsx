"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api, ApiError } from "./api";
import { clearSession, getStoredUser, getToken, saveSession, saveUser } from "./session";
import type { Address, Me, Session, User } from "./types";

interface RegisterInput {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  locale?: "sw" | "en";
  consent_marketing?: boolean;
}

interface AuthState {
  user: User | null;
  addresses: Address[];
  token: string | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (input: RegisterInput) => Promise<User>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const refresh = useCallback(async () => {
    const current = getToken();
    if (!current) {
      setUser(null);
      setToken(null);
      setAddresses([]);
      return;
    }
    try {
      const me = await api<Me>("/auth/me", { token: current });
      setUser(me.user);
      setAddresses(me.addresses);
      saveUser(me.user);
      setToken(current);
    } catch (error) {
      if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
        clearSession();
        setUser(null);
        setToken(null);
        setAddresses([]);
      }
    }
  }, []);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      setReady(true);
      return;
    }
    const storedUser = getStoredUser<User>();
    setToken(storedToken);
    if (storedUser) setUser(storedUser);
    void refresh().finally(() => setReady(true));
  }, [refresh]);

  const login = useCallback(
    async (email: string, password: string) => {
      const session = await api<Session>("/auth/login", {
        method: "POST",
        body: { email, password },
        auth: false,
      });
      saveSession(session.access_token, session.user);
      setToken(session.access_token);
      setUser(session.user);
      await refresh();
      return session.user;
    },
    [refresh],
  );

  const register = useCallback(
    async (input: RegisterInput) => {
      const session = await api<Session>("/auth/register", {
        method: "POST",
        body: {
          locale: "sw",
          consent_marketing: false,
          ...input,
        },
        auth: false,
      });
      saveSession(session.access_token, session.user);
      setToken(session.access_token);
      setUser(session.user);
      await refresh();
      return session.user;
    },
    [refresh],
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    setToken(null);
    setAddresses([]);
  }, []);

  const value = useMemo<AuthState>(
    () => ({ user, addresses, token, ready, login, register, logout, refresh }),
    [user, addresses, token, ready, login, register, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (context === null) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

export function homeForRole(role: string): string {
  switch (role) {
    case "supplier":
      return "/supplier";
    case "ops_admin":
    case "ops_finance":
    case "ops_support":
    case "superadmin":
      return "/ops";
    default:
      return "/orders";
  }
}
