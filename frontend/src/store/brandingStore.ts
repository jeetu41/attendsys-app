import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'https://absence-alert-4.preview.emergentagent.com';

interface Branding {
  app_name: string;
  logo_base64: string | null;
  primary_color: string;
  school_name: string;
}

interface BrandingState {
  branding: Branding;
  loadBranding: (cnn_token: string) => Promise<void>;
  resetBranding: () => void;
}

const defaultBranding: Branding = {
  app_name: 'AttendSys',
  logo_base64: null,
  primary_color: '#6366f1',
  school_name: '',
};

export const useBrandingStore = create<BrandingState>((set) => ({
  branding: defaultBranding,

  loadBranding: async (cnn_token: string) => {
    try {
      const response = await axios.get(`${API_URL}/api/school/branding/${cnn_token}`);
      const branding = response.data;
      await AsyncStorage.setItem('branding', JSON.stringify(branding));
      set({ branding });
    } catch (error) {
      console.error('Failed to load branding:', error);
      // Use default branding on error
      set({ branding: defaultBranding });
    }
  },

  resetBranding: () => {
    AsyncStorage.removeItem('branding');
    set({ branding: defaultBranding });
  },
}));
