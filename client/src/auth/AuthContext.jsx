import React, { createContext, useState, useEffect } from "react";
import api from "../api/axiosConfig";

export const AuthContext = createContext({
  user: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api
        .get("/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("access_token");
          setUser(null);
        });
    }
  }, []);

  const login = async (username, password) => {
    const res = await api.post("/auth/login", { username, password });
    const { access_token } = res.data;
    localStorage.setItem("access_token", access_token);
    const me = await api.get("/auth/me");
    setUser(me.data);
  };

  const register = async (username, email, password) => {
    await api.post("/auth/register", { username, email, password });

    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
