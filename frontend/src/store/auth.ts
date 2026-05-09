import { create } from 'zustand';
import { authApi } from '../services/api';

interface AuthState {
  isAuthenticated: boolean;
  username: string | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  username: null,
  token: null,

  login: async (username: string, password: string) => {
    try {
      const response = await authApi.login(username, password);
      localStorage.setItem('admin_token', response.access_token);
      localStorage.setItem('admin_username', username);
      set({
        isAuthenticated: true,
        username,
        token: response.access_token,
      });
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    set({
      isAuthenticated: false,
      username: null,
      token: null,
    });
  },

  checkAuth: () => {
    const token = localStorage.getItem('admin_token');
    const username = localStorage.getItem('admin_username');
    if (token && username) {
      set({
        isAuthenticated: true,
        username,
        token,
      });
    }
  },
}));
