import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DropboxFile {
  name: string;
  path: string;
  size: number;
  modified: string;
  shared_url: string;
  is_audio: boolean;
}

// Types
export interface AudioAsset {
  id: string;
  title: string;
  type: 'mix' | 'track';
  audio_url: string;
  duration_seconds: number;
  file_size?: number;
  dropbox_path?: string;
  created_at: string;
}

export interface ScheduleEvent {
  id: string;
  audio_asset_id: string;
  start_at: string;
  end_at: string;
  created_at: string;
  audio_asset?: AudioAsset;
}

export interface NowPlaying {
  is_playing: boolean;
  current_asset?: AudioAsset;
  seek_position?: number;
  next_event?: ScheduleEvent;
  message?: string;
}

// API Functions
export const nowPlayingApi = {
  getNowPlaying: () => apiClient.get<NowPlaying>('/api/now-playing'),
  getSchedule: () => apiClient.get<ScheduleEvent[]>('/api/schedule'),
};

export const adminApi = {
  // Assets
  createAsset: (data: Omit<AudioAsset, 'id' | 'created_at'>) =>
    apiClient.post<AudioAsset>('/api/admin/assets', data),
  listAssets: () => apiClient.get<AudioAsset[]>('/api/admin/assets'),
  getAsset: (id: string) => apiClient.get<AudioAsset>(`/api/admin/assets/${id}`),
  deleteAsset: (id: string) => apiClient.delete(`/api/admin/assets/${id}`),
  
  // Schedule
  createScheduleEvent: (data: Omit<ScheduleEvent, 'id' | 'created_at' | 'audio_asset'>) =>
    apiClient.post<ScheduleEvent>('/api/admin/schedule', data),
  listScheduleEvents: () => apiClient.get<ScheduleEvent[]>('/api/admin/schedule'),
  deleteScheduleEvent: (id: string) => apiClient.delete(`/api/admin/schedule/${id}`),
  
  // Upload
  uploadFile: (file: File, folder: string = '/dj-assets') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);
    return apiClient.post('/api/admin/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  listDropboxFiles: (folder: string = '/dj-assets') =>
    apiClient.get<{ files: DropboxFile[]; total: number }>('/api/admin/dropbox/files', { params: { folder } }),
  
  importFromDropbox: (data: { file_path: string; title: string; type: string; duration_seconds: number }) => {
    return apiClient.post<AudioAsset>('/api/admin/dropbox/import', data);
  },
};
