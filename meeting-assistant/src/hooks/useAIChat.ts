// AI Chat Hook
// Provides React integration for AI chat service

import { useState, useCallback, useEffect } from 'react';
import { aiChatService } from '@/services';
import { useAIChatStore, useTranscriptStore } from '@/store';

interface UseAIChatReturn {
    isConfigured: boolean;
    isLoading: boolean;
    error: string | null;
    sendMessage: (message: string) => Promise<void>;
    generateSummary: () => Promise<string>;
    extractActionItems: () => Promise<string>;
    getKeyDecisions: () => Promise<string>;
    clearChat: () => void;
}

export function useAIChat(): UseAIChatReturn {
    const { addMessage, setIsLoading, isLoading, clearMessages } = useAIChatStore();
    const { entries } = useTranscriptStore();
    const [error, setError] = useState<string | null>(null);
    const [isConfigured, setIsConfigured] = useState(false);

    // Check configuration on mount and when settings change
    useEffect(() => {
        const checkConfig = () => {
            setIsConfigured(aiChatService.isConfigured());
        };

        checkConfig();

        // Re-check when storage changes (settings saved)
        const handleStorageChange = () => {
            const savedSettings = localStorage.getItem('meeting-assistant-settings');
            if (savedSettings) {
                try {
                    const settings = JSON.parse(savedSettings);
                    let aiApiKey: string;
                    if (settings.aiProvider === 'openai') {
                        aiApiKey = settings.apiKeys?.openaiKey;
                    } else if (settings.aiProvider === 'groq') {
                        aiApiKey = settings.apiKeys?.groqKey;
                    } else {
                        aiApiKey = settings.apiKeys?.anthropicKey;
                    }

                    if (aiApiKey) {
                        aiChatService.configure({
                            provider: {
                                type: settings.aiProvider || 'openai',
                                apiKey: aiApiKey,
                                model: settings.aiModel,
                            },
                        });
                        setIsConfigured(true);
                    }
                } catch (e) {
                    console.error('Failed to parse settings:', e);
                }
            }
        };

        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    // Update AI context when transcript changes
    useEffect(() => {
        if (entries.length > 0) {
            const transcriptText = entries
                .map(e => `[${new Date(e.timestamp).toLocaleTimeString()}] ${e.speakerName}: ${e.text}`)
                .join('\n');

            aiChatService.updateTranscriptContext(transcriptText);
        }
    }, [entries]);

    // Send a message to the AI
    const sendMessage = useCallback(async (message: string) => {
        if (!aiChatService.isConfigured()) {
            setError('AI service not configured. Please add your API key in Settings.');
            return;
        }

        setError(null);
        setIsLoading(true);

        // Add user message
        addMessage({
            id: crypto.randomUUID(),
            role: 'user',
            content: message,
            timestamp: new Date(),
        });

        try {
            const response = await aiChatService.sendMessage(message);

            // Add AI response
            addMessage({
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.content,
                timestamp: new Date(),
            });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to get AI response';
            setError(errorMessage);

            // Add error message
            addMessage({
                id: crypto.randomUUID(),
                role: 'assistant',
                content: `Error: ${errorMessage}`,
                timestamp: new Date(),
            });
        } finally {
            setIsLoading(false);
        }
    }, [addMessage, setIsLoading]);

    // Generate meeting summary
    const generateSummary = useCallback(async (): Promise<string> => {
        if (!aiChatService.isConfigured()) {
            throw new Error('AI service not configured');
        }

        setIsLoading(true);
        try {
            const summary = await aiChatService.generateSummary();
            return summary;
        } finally {
            setIsLoading(false);
        }
    }, [setIsLoading]);

    // Extract action items
    const extractActionItems = useCallback(async (): Promise<string> => {
        if (!aiChatService.isConfigured()) {
            throw new Error('AI service not configured');
        }

        setIsLoading(true);
        try {
            const items = await aiChatService.extractActionItems();
            return items;
        } finally {
            setIsLoading(false);
        }
    }, [setIsLoading]);

    // Get key decisions
    const getKeyDecisions = useCallback(async (): Promise<string> => {
        if (!aiChatService.isConfigured()) {
            throw new Error('AI service not configured');
        }

        setIsLoading(true);
        try {
            const decisions = await aiChatService.getKeyDecisions();
            return decisions;
        } finally {
            setIsLoading(false);
        }
    }, [setIsLoading]);

    // Clear chat
    const clearChat = useCallback(() => {
        clearMessages();
        aiChatService.clearHistory();
        setError(null);
    }, [clearMessages]);

    return {
        isConfigured,
        isLoading,
        error,
        sendMessage,
        generateSummary,
        extractActionItems,
        getKeyDecisions,
        clearChat,
    };
}
