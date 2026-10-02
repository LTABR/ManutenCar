import { apiRequest, setAccessToken } from "./client";
import { encryptForApi } from "./crypto";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
};

type LoginResponse = {
  accessToken: string;
  user: AuthUser;
};

export async function login(email: string, password: string) {
  const encrypted = await encryptForApi({ email, password });
  const response = await apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(encrypted),
  });
  setAccessToken(response.accessToken);
  return response.user;
}

export function logout() {
  setAccessToken(null);
}
