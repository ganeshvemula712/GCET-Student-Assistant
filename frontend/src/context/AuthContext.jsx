import { createContext, useContext, useEffect, useState } from "react";
import {
  getAccessToken,
  removeTokens,
} from "@/utils/token";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const token = getAccessToken();

    if (token) {
      setAuthenticated(true);
    }
  }, []);

  function login() {
    setAuthenticated(true);
  }

  function logout() {
    removeTokens();
    setAuthenticated(false);
  }

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}