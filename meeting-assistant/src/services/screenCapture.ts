// Screen Capture Service
// Captures screen content periodically for AI context

import { appDataDir } from '@tauri-apps/api/path';
import { writeBinaryFile, createDir } from '@tauri-apps/api/fs';
import type { ScreenCapture } from '@/types';

export interface ScreenCaptureConfig {
    enabled: boolean;
    interval: number; // milliseconds between captures
    quality: number; // 0-1, JPEG quality
    captureMode: 'full-screen' | 'active-window';
    enableOCR: boolean;
    privacyZones: Array<{ x: number; y: number; width: number; height: number }>;
}

type CaptureCallback = (capture: ScreenCapture) => void;

class ScreenCaptureService {
    private config: ScreenCaptureConfig = {
        enabled: false,
        interval: 10000, // Every 10 seconds
        quality: 0.7,
        captureMode: 'active-window',
        enableOCR: false,
        privacyZones: [],
    };

    private intervalId: number | null = null;
    private callbacks: CaptureCallback[] = [];
    private lastCaptureHash: string | null = null;
    private captureCount = 0;

    /**
     * Configure screen capture
     */
    configure(config: Partial<ScreenCaptureConfig>): void {
        this.config = { ...this.config, ...config };
        console.log('Screen capture configured:', this.config);
    }

    /**
     * Check if service is enabled
     */
    isEnabled(): boolean {
        return this.config.enabled;
    }

    /**
     * Start screen capture
     */
    async start(meetingId: string): Promise<void> {
        if (this.intervalId || !this.config.enabled) return;

        // Check if screen capture API is available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
            console.error('Screen capture not supported in this browser');
            return;
        }

        this.captureCount = 0;
        this.lastCaptureHash = null;

        // Start periodic capture
        this.intervalId = window.setInterval(() => {
            this.captureScreen(meetingId);
        }, this.config.interval);

        // Take first capture immediately
        await this.captureScreen(meetingId);

        console.log('Screen capture started');
    }

    /**
     * Stop screen capture
     */
    stop(): void {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        console.log('Screen capture stopped');
    }

    /**
     * Subscribe to screen captures
     */
    onCapture(callback: CaptureCallback): () => void {
        this.callbacks.push(callback);
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
        };
    }

    /**
     * Capture screen
     */
    private async captureScreen(meetingId: string): Promise<void> {
        try {
            // Create a canvas to capture the screen
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            // For now, we'll use a placeholder approach
            // In a real implementation, you'd use:
            // 1. Tauri's screenshot API for desktop
            // 2. getDisplayMedia for web
            // 3. Native screen capture for better performance

            // Placeholder: Capture current window content
            const screenshot = await this.captureCurrentView();
            if (!screenshot) return;

            // Check if content has changed significantly
            const contentHash = await this.hashImage(screenshot);
            if (contentHash === this.lastCaptureHash) {
                console.log('Screen content unchanged, skipping capture');
                return;
            }

            this.lastCaptureHash = contentHash;
            this.captureCount++;

            // Apply privacy zones (blur sensitive areas)
            const processedImage = await this.applyPrivacyZones(screenshot);

            // Extract text if OCR is enabled
            let ocrText = '';
            if (this.config.enableOCR) {
                ocrText = await this.extractText(processedImage);
            }

            // Save capture
            const capture: ScreenCapture = {
                id: crypto.randomUUID(),
                meetingId,
                timestamp: Date.now(),
                imagePath: await this.saveImage(processedImage, meetingId),
                ocrText,
                relevanceScore: 0.8,
                createdAt: new Date(),
            };

            // Notify callbacks
            this.callbacks.forEach(cb => cb(capture));

            console.log(`Screen captured: ${capture.id}`);
        } catch (error) {
            console.error('Failed to capture screen:', error);
        }
    }

    /**
     * Capture current view (placeholder implementation)
     */
    private async captureCurrentView(): Promise<HTMLCanvasElement | null> {
        try {
            // This is a simplified version
            // In production, use Tauri's screenshot API or getDisplayMedia

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return null;

            // Set canvas size (reduced for performance)
            canvas.width = 1280;
            canvas.height = 720;

            // Draw a placeholder (in real implementation, this would be actual screen content)
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Add timestamp
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px monospace';
            ctx.fillText(`Screen Capture - ${new Date().toLocaleTimeString()}`, 20, 40);
            ctx.fillText('(Placeholder - Use Tauri screenshot API for real captures)', 20, 70);

            return canvas;
        } catch (error) {
            console.error('Failed to capture view:', error);
            return null;
        }
    }

    /**
     * Hash image for change detection
     */
    private async hashImage(canvas: HTMLCanvasElement): Promise<string> {
        // Simple hash based on image data
        const ctx = canvas.getContext('2d');
        if (!ctx) return '';

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        // Sample pixels for quick hash
        let hash = 0;
        const step = Math.floor(data.length / 1000); // Sample 1000 points

        for (let i = 0; i < data.length; i += step) {
            hash = ((hash << 5) - hash) + data[i];
            hash = hash & hash; // Convert to 32-bit integer
        }

        return hash.toString(36);
    }

    /**
     * Apply privacy zones to image
     */
    private async applyPrivacyZones(canvas: HTMLCanvasElement): Promise<HTMLCanvasElement> {
        if (this.config.privacyZones.length === 0) return canvas;

        const ctx = canvas.getContext('2d');
        if (!ctx) return canvas;

        // Blur privacy zones
        for (const zone of this.config.privacyZones) {
            // Scale zone coordinates to canvas size
            const x = (zone.x / 100) * canvas.width;
            const y = (zone.y / 100) * canvas.height;
            const width = (zone.width / 100) * canvas.width;
            const height = (zone.height / 100) * canvas.height;

            // Apply blur effect (simple pixelation)
            const imageData = ctx.getImageData(x, y, width, height);
            const pixelSize = 20;

            for (let py = 0; py < height; py += pixelSize) {
                for (let px = 0; px < width; px += pixelSize) {
                    const i = (py * width + px) * 4;
                    const r = imageData.data[i];
                    const g = imageData.data[i + 1];
                    const b = imageData.data[i + 2];

                    // Fill block with average color
                    for (let by = 0; by < pixelSize && py + by < height; by++) {
                        for (let bx = 0; bx < pixelSize && px + bx < width; bx++) {
                            const bi = ((py + by) * width + (px + bx)) * 4;
                            imageData.data[bi] = r;
                            imageData.data[bi + 1] = g;
                            imageData.data[bi + 2] = b;
                        }
                    }
                }
            }

            ctx.putImageData(imageData, x, y);
        }

        return canvas;
    }

    /**
     * Extract text from image using OCR
     */
    private async extractText(canvas: HTMLCanvasElement): Promise<string> {
        // This would use Tesseract.js or a cloud OCR service
        // For now, return placeholder
        console.log('OCR not yet implemented');
        return '';
    }

    /**
     * Save image to file
     */
    private async saveImage(canvas: HTMLCanvasElement, meetingId: string): Promise<string> {
        try {
            // Convert canvas to blob
            const blob = await new Promise<Blob>((resolve, reject) => {
                canvas.toBlob(
                    (blob) => {
                        if (blob) resolve(blob);
                        else reject(new Error('Failed to create blob'));
                    },
                    'image/jpeg',
                    this.config.quality
                );
            });

            // Get app data directory
            const dataDir = await appDataDir();
            const screenshotsDir = `${dataDir}screenshots/${meetingId}`;

            // Create directory
            await createDir(screenshotsDir, { recursive: true });

            // Save file
            const fileName = `capture_${this.captureCount}_${Date.now()}.jpg`;
            const filePath = `${screenshotsDir}/${fileName}`;

            const arrayBuffer = await blob.arrayBuffer();
            await writeBinaryFile(filePath, new Uint8Array(arrayBuffer));

            return filePath;
        } catch (error) {
            console.error('Failed to save screenshot:', error);
            return '';
        }
    }

    /**
     * Get recent captures for AI context
     */
    getRecentCapturesContext(captures: ScreenCapture[], count: number = 3): string {
        const recent = captures.slice(-count);
        
        if (recent.length === 0) return '';

        const context = recent
            .map(c => {
                const time = new Date(c.timestamp).toLocaleTimeString();
                return `[${time}] Screen content: ${c.ocrText || '(No text extracted)'}`;
            })
            .join('\n');

        return `\n\n## Recent Screen Context:\n${context}`;
    }

    /**
     * Reset service
     */
    reset(): void {
        this.captureCount = 0;
        this.lastCaptureHash = null;
        console.log('Screen capture service reset');
    }
}

// Singleton instance
export const screenCaptureService = new ScreenCaptureService();
