// Volume Meter Component
// Visual audio level indicator

import { useEffect, useRef } from 'react';
import './VolumeMeter.css';

interface VolumeMeterProps {
  volume: number; // 0-1
  isActive: boolean;
  variant?: 'horizontal' | 'vertical';
  size?: 'sm' | 'md' | 'lg';
}

export function VolumeMeter({ 
  volume, 
  isActive, 
  variant = 'horizontal',
  size = 'md' 
}: VolumeMeterProps) {
  const barCount = size === 'sm' ? 5 : size === 'md' ? 10 : 15;
  const bars = Array.from({ length: barCount }, (_, i) => i);

  return (
    <div 
      className={`volume-meter ${variant} ${size} ${isActive ? 'active' : ''}`}
      role="meter"
      aria-valuenow={Math.round(volume * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Audio volume level"
    >
      {bars.map((index) => {
        const threshold = (index + 1) / barCount;
        const isLit = volume >= threshold;
        const isHigh = threshold > 0.8;
        const isMedium = threshold > 0.5 && threshold <= 0.8;
        
        return (
          <div
            key={index}
            className={`volume-bar ${isLit ? 'lit' : ''} ${isHigh ? 'high' : isMedium ? 'medium' : 'low'}`}
            style={{
              transitionDelay: `${index * 10}ms`,
            }}
          />
        );
      })}
    </div>
  );
}

// Waveform visualization component
interface WaveformProps {
  isRecording: boolean;
  volume: number;
}

export function Waveform({ isRecording, volume }: WaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const barsRef = useRef<number[]>(Array(32).fill(0));

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      const { width, height } = canvas;
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height);
      
      // Update bar values
      const bars = barsRef.current;
      for (let i = 0; i < bars.length; i++) {
        if (isRecording) {
          // Animate based on volume with some randomness
          const target = volume * (0.3 + Math.random() * 0.7);
          bars[i] = bars[i] * 0.9 + target * 0.1;
        } else {
          // Decay when not recording
          bars[i] *= 0.95;
        }
      }

      // Draw bars
      const barWidth = width / bars.length;
      const gap = 2;
      
      ctx.fillStyle = 'url(#waveformGradient)';
      
      // Create gradient
      const gradient = ctx.createLinearGradient(0, height, 0, 0);
      gradient.addColorStop(0, '#6366f1');
      gradient.addColorStop(0.5, '#8b5cf6');
      gradient.addColorStop(1, '#a855f7');
      ctx.fillStyle = gradient;

      for (let i = 0; i < bars.length; i++) {
        const barHeight = Math.max(4, bars[i] * height * 0.8);
        const x = i * barWidth + gap / 2;
        const y = (height - barHeight) / 2;
        
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth - gap, barHeight, 2);
        ctx.fill();
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRecording, volume]);

  return (
    <canvas
      ref={canvasRef}
      className="waveform-canvas"
      width={200}
      height={40}
    />
  );
}
