import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    plugins: [react()],

    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@components': path.resolve(__dirname, './src/components'),
            '@hooks': path.resolve(__dirname, './src/hooks'),
            '@services': path.resolve(__dirname, './src/services'),
            '@store': path.resolve(__dirname, './src/store'),
            '@types': path.resolve(__dirname, './src/types'),
        },
    },

    // Tauri expects a fixed port
    server: {
        port: 1420,
        strictPort: true,
    },

    // Env prefix for Tauri
    envPrefix: ['VITE_', 'TAURI_'],

    build: {
        // Tauri supports ES2021
        target: process.env.TAURI_PLATFORM === 'windows' ? 'chrome105' : 'safari13',
        // Disable minification in debug builds
        minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
        // Enable source maps in debug builds
        sourcemap: !!process.env.TAURI_DEBUG,
    },
});
