// Speaker Diarization Service
// Identifies different speakers in audio using voice characteristics

import type { TranscriptEntry } from '@/types';

export interface SpeakerSegment {
    speakerId: string;
    startTime: number;
    endTime: number;
    confidence: number;
}

export interface DiarizationConfig {
    minSpeakers?: number;
    maxSpeakers?: number;
    method: 'simple' | 'assemblyai' | 'pyannote';
    apiKey?: string;
}

interface SpeakerProfile {
    id: string;
    name: string;
    color: string;
    voiceCharacteristics: {
        avgPitch: number;
        avgEnergy: number;
        speakingRate: number;
    };
    utteranceCount: number;
}

class SpeakerDiarizationService {
    private config: DiarizationConfig | null = null;
    private speakers: Map<string, SpeakerProfile> = new Map();
    private speakerColors = [
        '#3b82f6', // blue
        '#10b981', // green
        '#f59e0b', // amber
        '#ef4444', // red
        '#8b5cf6', // purple
        '#ec4899', // pink
        '#06b6d4', // cyan
        '#f97316', // orange
    ];
    private nextSpeakerIndex = 0;

    /**
     * Configure the diarization service
     */
    configure(config: DiarizationConfig): void {
        this.config = config;
        console.log(`Speaker diarization configured with method: ${config.method}`);
    }

    /**
     * Check if service is configured
     */
    isConfigured(): boolean {
        return this.config !== null;
    }

    /**
     * Identify speaker for a transcript entry using simple heuristics
     * This is a basic implementation - for production, use AssemblyAI or pyannote
     */
    async identifySpeaker(
        entry: TranscriptEntry,
        audioFeatures?: {
            pitch: number;
            energy: number;
            duration: number;
        }
    ): Promise<{ speakerId: string; speakerName: string; confidence: number }> {
        if (!this.config) {
            return {
                speakerId: 'speaker-1',
                speakerName: 'Speaker 1',
                confidence: 0.5,
            };
        }

        // For simple method, use basic heuristics
        if (this.config.method === 'simple') {
            return this.simpleIdentification(entry, audioFeatures);
        }

        // For cloud methods, would call external API
        if (this.config.method === 'assemblyai') {
            return this.assemblyAIIdentification(entry);
        }

        // Default fallback
        return {
            speakerId: 'speaker-1',
            speakerName: 'Speaker 1',
            confidence: 0.5,
        };
    }

    /**
     * Simple speaker identification based on timing and text patterns
     */
    private simpleIdentification(
        _entry: TranscriptEntry, // Reserved for future timing-based analysis
        audioFeatures?: {
            pitch: number;
            energy: number;
            duration: number;
        }
    ): { speakerId: string; speakerName: string; confidence: number } {
        // Check if this follows immediately after another speaker
        const recentSpeakers = Array.from(this.speakers.values())
            .filter(s => s.utteranceCount > 0)
            .sort((a, b) => b.utteranceCount - a.utteranceCount);

        // If we have audio features, try to match with existing speakers
        if (audioFeatures && recentSpeakers.length > 0) {
            let bestMatch: SpeakerProfile | null = null;
            let bestScore = 0;

            for (const speaker of recentSpeakers) {
                const pitchDiff = Math.abs(speaker.voiceCharacteristics.avgPitch - audioFeatures.pitch);
                const energyDiff = Math.abs(speaker.voiceCharacteristics.avgEnergy - audioFeatures.energy);
                
                // Simple similarity score (lower is better)
                const score = 1 / (1 + pitchDiff + energyDiff);

                if (score > bestScore && score > 0.6) {
                    bestScore = score;
                    bestMatch = speaker;
                }
            }

            if (bestMatch) {
                // Update speaker profile
                this.updateSpeakerProfile(bestMatch.id, audioFeatures);
                return {
                    speakerId: bestMatch.id,
                    speakerName: bestMatch.name,
                    confidence: bestScore,
                };
            }
        }

        // Detect speaker changes based on timing gaps
        // If more than 2 seconds since last utterance, might be a different speaker
        const timeSinceLastUtterance = this.getTimeSinceLastUtterance();
        const isLikelyNewSpeaker = timeSinceLastUtterance > 2000;

        if (isLikelyNewSpeaker && recentSpeakers.length > 0) {
            // Alternate between speakers
            const lastSpeaker = recentSpeakers[0];
            const otherSpeaker = recentSpeakers.find(s => s.id !== lastSpeaker.id);

            if (otherSpeaker) {
                this.updateSpeakerProfile(otherSpeaker.id, audioFeatures);
                return {
                    speakerId: otherSpeaker.id,
                    speakerName: otherSpeaker.name,
                    confidence: 0.7,
                };
            }
        }

        // Create new speaker if needed
        if (this.speakers.size === 0 || (isLikelyNewSpeaker && this.speakers.size < (this.config?.maxSpeakers || 4))) {
            const newSpeaker = this.createNewSpeaker(audioFeatures);
            return {
                speakerId: newSpeaker.id,
                speakerName: newSpeaker.name,
                confidence: 0.6,
            };
        }

        // Default to most recent speaker
        const defaultSpeaker = recentSpeakers[0] || this.createNewSpeaker(audioFeatures);
        this.updateSpeakerProfile(defaultSpeaker.id, audioFeatures);
        
        return {
            speakerId: defaultSpeaker.id,
            speakerName: defaultSpeaker.name,
            confidence: 0.5,
        };
    }

    /**
     * AssemblyAI speaker diarization (requires API key)
     */
    private async assemblyAIIdentification(
        // entry parameter reserved for future AssemblyAI integration
        _entry: TranscriptEntry
    ): Promise<{ speakerId: string; speakerName: string; confidence: number }> {
        // This would call AssemblyAI API
        // For now, return placeholder
        console.log('AssemblyAI diarization not yet implemented');
        return {
            speakerId: 'speaker-1',
            speakerName: 'Speaker 1',
            confidence: 0.8,
        };
    }

    /**
     * Create a new speaker profile
     */
    private createNewSpeaker(audioFeatures?: {
        pitch: number;
        energy: number;
        duration: number;
    }): SpeakerProfile {
        const speakerId = `speaker-${this.nextSpeakerIndex + 1}`;
        const speakerName = `Speaker ${this.nextSpeakerIndex + 1}`;
        const color = this.speakerColors[this.nextSpeakerIndex % this.speakerColors.length];

        const speaker: SpeakerProfile = {
            id: speakerId,
            name: speakerName,
            color,
            voiceCharacteristics: {
                avgPitch: audioFeatures?.pitch || 150,
                avgEnergy: audioFeatures?.energy || 0.5,
                speakingRate: audioFeatures?.duration ? 1000 / audioFeatures.duration : 3,
            },
            utteranceCount: 1,
        };

        this.speakers.set(speakerId, speaker);
        this.nextSpeakerIndex++;

        console.log(`Created new speaker: ${speakerName}`);
        return speaker;
    }

    /**
     * Update speaker profile with new audio features
     */
    private updateSpeakerProfile(
        speakerId: string,
        audioFeatures?: {
            pitch: number;
            energy: number;
            duration: number;
        }
    ): void {
        const speaker = this.speakers.get(speakerId);
        if (!speaker || !audioFeatures) return;

        // Update running averages
        const count = speaker.utteranceCount;
        speaker.voiceCharacteristics.avgPitch =
            (speaker.voiceCharacteristics.avgPitch * count + audioFeatures.pitch) / (count + 1);
        speaker.voiceCharacteristics.avgEnergy =
            (speaker.voiceCharacteristics.avgEnergy * count + audioFeatures.energy) / (count + 1);
        speaker.voiceCharacteristics.speakingRate =
            (speaker.voiceCharacteristics.speakingRate * count + 1000 / audioFeatures.duration) / (count + 1);

        speaker.utteranceCount++;
    }

    /**
     * Get time since last utterance
     */
    private getTimeSinceLastUtterance(): number {
        // This would track the last timestamp
        // For now, return a default value
        return 1000;
    }

    /**
     * Get all identified speakers
     */
    getSpeakers(): SpeakerProfile[] {
        return Array.from(this.speakers.values());
    }

    /**
     * Get speaker by ID
     */
    getSpeaker(speakerId: string): SpeakerProfile | undefined {
        return this.speakers.get(speakerId);
    }

    /**
     * Update speaker name (for user customization)
     */
    updateSpeakerName(speakerId: string, name: string): void {
        const speaker = this.speakers.get(speakerId);
        if (speaker) {
            speaker.name = name;
            console.log(`Updated speaker ${speakerId} name to: ${name}`);
        }
    }

    /**
     * Reset all speakers
     */
    reset(): void {
        this.speakers.clear();
        this.nextSpeakerIndex = 0;
        console.log('Speaker diarization reset');
    }

    /**
     * Analyze audio chunk for voice characteristics
     * This is a simplified version - real implementation would use DSP
     */
    analyzeAudioFeatures(audioData: Float32Array, sampleRate: number): {
        pitch: number;
        energy: number;
        duration: number;
    } {
        // Calculate energy (RMS)
        let sumSquares = 0;
        for (let i = 0; i < audioData.length; i++) {
            sumSquares += audioData[i] * audioData[i];
        }
        const energy = Math.sqrt(sumSquares / audioData.length);

        // Estimate pitch using zero-crossing rate (simplified)
        let zeroCrossings = 0;
        for (let i = 1; i < audioData.length; i++) {
            if ((audioData[i] >= 0 && audioData[i - 1] < 0) || (audioData[i] < 0 && audioData[i - 1] >= 0)) {
                zeroCrossings++;
            }
        }
        const zcr = zeroCrossings / audioData.length;
        const estimatedPitch = (zcr * sampleRate) / 2;

        // Duration in milliseconds
        const duration = (audioData.length / sampleRate) * 1000;

        return {
            pitch: Math.max(50, Math.min(400, estimatedPitch)), // Clamp to reasonable range
            energy: Math.min(1, energy * 10), // Normalize
            duration,
        };
    }
}

// Singleton instance
export const speakerDiarizationService = new SpeakerDiarizationService();
