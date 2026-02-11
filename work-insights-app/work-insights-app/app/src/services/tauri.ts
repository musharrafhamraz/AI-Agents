import { invoke } from '@tauri-apps/api/core';
import { TodayStats, Activity } from '../types';

export const tauriService = {
  async startTracking(): Promise<void> {
    return invoke('start_tracking');
  },

  async stopTracking(): Promise<void> {
    return invoke('stop_tracking');
  },

  async getTrackingStatus(): Promise<boolean> {
    return invoke('get_tracking_status');
  },

  async getTodayStatistics(): Promise<TodayStats> {
    return invoke('get_today_statistics');
  },

  async getActivities(startTimestamp: number, endTimestamp: number): Promise<Activity[]> {
    return invoke('get_activities', { startTimestamp, endTimestamp });
  },

  async getCurrentTime(): Promise<number> {
    return invoke('get_current_time');
  },
};
