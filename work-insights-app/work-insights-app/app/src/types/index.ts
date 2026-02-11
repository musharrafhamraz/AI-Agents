export interface Activity {
  id?: number;
  timestamp: number;
  app_name: string;
  window_title?: string;
  duration_seconds: number;
  is_idle: boolean;
  category?: string;
}

export interface TodayStats {
  active_time_seconds: number;
  idle_time_seconds: number;
  context_switches: number;
}

export interface TrackingState {
  isTracking: boolean;
  todayStats: TodayStats | null;
}
