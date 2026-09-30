import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  getAuthToken, 
  setAuthToken, 
  fetchCurrentUser, 
  loginUser, 
  registerUser, 
  logoutUser 
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(getAuthToken());
  const [loading, setLoading] = useState(true);

  // Check auth status on initial load and refresh
  useEffect(() => {
    async function initAuth() {
      const existingToken = getAuthToken();
      if (existingToken) {
        const res = await fetchCurrentUser();
        if (res.success && res.user) {
          setUser(res.user);
          setToken(existingToken);
        } else {
          // Token invalid or expired
          setAuthToken(null);
          setToken(null);
          setUser(null);
        }
      } else {
        setToken(null);
        setUser(null);
      }
      setLoading(false);
    }
    initAuth();
  }, []);

  const login = async (email, password) => {
    const res = await loginUser({ email, password });
    if (res.success && res.data) {
      const newToken = res.data.access_token;
      const userData = res.data.user;
      setAuthToken(newToken);
      setToken(newToken);
      setUser(userData);
      return { success: true, user: userData };
    }
    return { success: false, error: res.error || 'Invalid email or password.' };
  };

  const register = async (name, email, password) => {
    const res = await registerUser({ name, email, password });
    if (res.success) {
      return { success: true, message: 'Registration successful' };
    }
    return { success: false, error: res.error || 'Registration failed' };
  };

  const logout = async () => {
    await logoutUser();
    setAuthToken(null);
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
