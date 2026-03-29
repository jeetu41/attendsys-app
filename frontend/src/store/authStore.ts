import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'platform_admin' | 'school_admin' | 'teacher' | 'parent';
  is_approved?: boolean;
  is_class_teacher?: boolean;
  school_id?: string;
  subscription_active?: boolean;
  message_balance?: number;
}

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  loading: false,

  login: async (email: string, password: string) => {
    try {
      set({ loading: true });
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      });
      const { token, user } = response.data;
      await AsyncStorage.setItem('token', token);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      set({ token, user, loading: false });
    } catch (error: any) {
      set({ loading: false });
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  register: async (data: any) => {
    try {
      set({ loading: true });
      const response = await axios.post(`${API_URL}/api/auth/register`, data);
      const { token, user } = response.data;
      await AsyncStorage.setItem('token', token);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      set({ token, user, loading: false });
    } catch (error: any) {
      set({ loading: false });
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  },

  logout: async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    set({ token: null, user: null });
  },

  checkAuth: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      const userStr = await AsyncStorage.getItem('user');
      if (token && userStr) {
        const user = JSON.parse(userStr);
        set({ token, user });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    }
  },

  updateUser: (user: User) => {
    set({ user });
    AsyncStorage.setItem('user', JSON.stringify(user));
  },
}));

export const getAuthHeader = async () => {
  const token = await AsyncStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};
