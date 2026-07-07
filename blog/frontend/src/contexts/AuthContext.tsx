import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { UserPrivate } from '../types/api';
import { fetchApi } from '../lib/api';

interface AuthContextType {
  user: UserPrivate | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  updateUser: (user: UserPrivate) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPrivate | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await fetchApi<UserPrivate>('/users/me');
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          localStorage.removeItem('access_token');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (token: string) => {
    localStorage.setItem('access_token', token);
    try {
      const userData = await fetchApi<UserPrivate>('/users/me');
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user after login:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  const updateUser = (updatedUser: UserPrivate) => {
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
