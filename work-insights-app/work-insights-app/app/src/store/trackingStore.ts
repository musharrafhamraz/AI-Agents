import { create } from 'zustand';
import { TodayStats } from '../types';
import { tauriService } from '../services/tauri';

interface TrackingState {
  isTracking: boolean;
  todayStats: TodayStats | null;
  isLoading: boolean;
  error: string | null;
  
  startTracking: () => Promise<void>;
  stopTracking: () => Promise<void>;
  fetchStatus: () => Promise<void>;
  fetchTodayStats: () => Promise<void>;
}

export const useTrackingStore = create<TrackingState>((set) => ({
  isTracking: false,
  todayStats: null,
  isLoading: false,
  error: null,

  startTracking: async () => {
    try {
      set({ isLoading: true, error: null });
      await tauriService.startTracking();
      set({ isTracking: true, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  stopTracking: async () => {
    try {
      set({ isLoading: true, error: null });
      await tauriService.stopTracking();
      set({ isTracking: false, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  fetchStatus: async () => {
    try {
      const status = await tauriService.getTrackingStatus();
      set({ isTracking: status });
    } catch (error) {
      set({ error: String(error) });
    }
  },

  fetchTodayStats: async () => {
    try {
      const stats = await tauriService.getTodayStatistics();
      set({ todayStats: stats });
    } catch (error) {
      set({ error: String(error) });
    }
  },
}));
