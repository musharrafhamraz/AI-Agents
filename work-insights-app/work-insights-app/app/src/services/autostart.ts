import { invoke } from '@tauri-apps/api/core';

export const autostartService = {
  async enable(): Promise<void> {
    try {
      await invoke('plugin:autostart|enable');
    } catch (error) {
      console.error('Failed to enable autostart:', error);
      throw error;
    }
  },

  async disable(): Promise<void> {
    try {
      await invoke('plugin:autostart|disable');
    } catch (error) {
      console.error('Failed to disable autostart:', error);
      throw error;
    }
  },

  async isEnabled(): Promise<boolean> {
    try {
      return await invoke('plugin:autostart|is_enabled');
    } catch (error) {
      console.error('Failed to check autostart status:', error);
      return false;
    }
  },
};
