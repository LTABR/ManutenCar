import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import * as authApi from "./api/auth";
import type { AuthUser } from "./api/auth";
import { setAccessToken } from "./api/client";

type AuthContextType = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const token = localStorage.getItem("manutencar-access-token");
    if (token) {
      setAccessToken(token);
      try {
        return JSON.parse(localStorage.getItem("manutencar-user") || "null") as AuthUser | null;
      } catch {
        return null;
      }
    }
    return null;
  });

  const login = useCallback(async (email: string, password: string) => {
    const authenticatedUser = await authApi.login(email, password);
    localStorage.setItem("manutencar-user", JSON.stringify(authenticatedUser));
    setUser(authenticatedUser);
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    const authenticatedUser = await authApi.signUp(email, password);
    localStorage.setItem("manutencar-user", JSON.stringify(authenticatedUser));
    setUser(authenticatedUser);
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    localStorage.removeItem("manutencar-access-token");
    localStorage.removeItem("manutencar-user");
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, loading: false, login, signUp, logout }), [user, login, signUp, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth must be used within AuthProvider");
  return auth;
}
