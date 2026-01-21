// AI Chat Service
// Handles AI-powered question answering about meeting content using OpenAI, Anthropic, or Groq

export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export interface AIProvider {
    type: 'openai' | 'anthropic' | 'groq';
    apiKey: string;
    model?: string;
}

export interface AIConfig {
    provider: AIProvider;
    systemPrompt?: string;
    maxTokens?: number;
    temperature?: number;
}

export interface AIResponse {
    content: string;
    usage?: {
        promptTokens: number;
        completionTokens: number;
        totalTokens: number;
    };
}

const DEFAULT_SYSTEM_PROMPT = `You are a helpful AI meeting assistant. You have access to the meeting transcript and can answer questions about the meeting content. Be concise but thorough in your responses.

When answering questions:
- Reference specific parts of the transcript when relevant
- Identify action items, decisions, and key points
- Summarize discussions when asked
- Help clarify any unclear points from the meeting

If you don't have enough information to answer a question, say so clearly.`;

class AIChatService {
    private config: AIConfig | null = null;
    private conversationHistory: ChatMessage[] = [];
    private transcriptContext: string = '';

    /**
     * Configure the AI service
     */
    configure(config: AIConfig): void {
        this.config = {
            ...config,
            systemPrompt: config.systemPrompt || DEFAULT_SYSTEM_PROMPT,
            maxTokens: config.maxTokens || 1024,
            temperature: config.temperature ?? 0.7,
        };
        this.conversationHistory = [];
        console.log(`AI Chat service configured with ${config.provider.type}`);
    }

    /**
     * Check if service is configured
     */
    isConfigured(): boolean {
        return this.config !== null && this.config.provider.apiKey.length > 0;
    }

    /**
     * Update the transcript context for the AI
     */
    updateTranscriptContext(transcript: string): void {
        this.transcriptContext = transcript;
    }

    /**
     * Clear conversation history
     */
    clearHistory(): void {
        this.conversationHistory = [];
    }

    /**
     * Send a message and get AI response
     */
    async sendMessage(userMessage: string): Promise<AIResponse> {
        if (!this.config) {
            throw new Error('AI Chat service not configured');
        }

        // Build messages array
        const messages: ChatMessage[] = [
            {
                role: 'system',
                content: this.buildSystemPrompt(),
            },
            ...this.conversationHistory,
            {
                role: 'user',
                content: userMessage,
            },
        ];

        let response: AIResponse;

        if (this.config.provider.type === 'openai') {
            response = await this.callOpenAI(messages);
        } else if (this.config.provider.type === 'groq') {
            response = await this.callGroq(messages);
        } else {
            response = await this.callAnthropic(messages);
        }

        // Add to conversation history
        this.conversationHistory.push({ role: 'user', content: userMessage });
        this.conversationHistory.push({ role: 'assistant', content: response.content });

        // Keep history manageable (last 20 messages)
        if (this.conversationHistory.length > 20) {
            this.conversationHistory = this.conversationHistory.slice(-20);
        }

        return response;
    }

    /**
     * Build system prompt with transcript context
     */
    private buildSystemPrompt(): string {
        let prompt = this.config?.systemPrompt || DEFAULT_SYSTEM_PROMPT;

        if (this.transcriptContext) {
            prompt += `\n\n## Current Meeting Transcript:\n${this.transcriptContext}`;
        }

        return prompt;
    }

    /**
     * Call OpenAI API
     */
    private async callOpenAI(messages: ChatMessage[]): Promise<AIResponse> {
        if (!this.config) throw new Error('Not configured');

        const model = this.config.provider.model || 'gpt-4o-mini';

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.config.provider.apiKey}`,
            },
            body: JSON.stringify({
                model,
                messages,
                max_tokens: this.config.maxTokens,
                temperature: this.config.temperature,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'OpenAI API error');
        }

        const data = await response.json();

        return {
            content: data.choices[0]?.message?.content || '',
            usage: {
                promptTokens: data.usage?.prompt_tokens || 0,
                completionTokens: data.usage?.completion_tokens || 0,
                totalTokens: data.usage?.total_tokens || 0,
            },
        };
    }

    /**
     * Call Anthropic API
     */
    private async callAnthropic(messages: ChatMessage[]): Promise<AIResponse> {
        if (!this.config) throw new Error('Not configured');

        const model = this.config.provider.model || 'claude-3-haiku-20240307';

        // Extract system message
        const systemMessage = messages.find(m => m.role === 'system')?.content || '';
        const conversationMessages = messages
            .filter(m => m.role !== 'system')
            .map(m => ({
                role: m.role as 'user' | 'assistant',
                content: m.content,
            }));

        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': this.config.provider.apiKey,
                'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify({
                model,
                max_tokens: this.config.maxTokens,
                system: systemMessage,
                messages: conversationMessages,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Anthropic API error');
        }

        const data = await response.json();

        return {
            content: data.content[0]?.text || '',
            usage: {
                promptTokens: data.usage?.input_tokens || 0,
                completionTokens: data.usage?.output_tokens || 0,
                totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
            },
        };
    }

    /**
     * Call Groq API (OpenAI-compatible)
     */
    private async callGroq(messages: ChatMessage[]): Promise<AIResponse> {
        if (!this.config) throw new Error('Not configured');

        const model = this.config.provider.model || 'llama-3.3-70b-versatile';

        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.config.provider.apiKey}`,
            },
            body: JSON.stringify({
                model,
                messages,
                max_tokens: this.config.maxTokens,
                temperature: this.config.temperature,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Groq API error');
        }

        const data = await response.json();

        return {
            content: data.choices[0]?.message?.content || '',
            usage: {
                promptTokens: data.usage?.prompt_tokens || 0,
                completionTokens: data.usage?.completion_tokens || 0,
                totalTokens: data.usage?.total_tokens || 0,
            },
        };
    }

    /**
     * Generate meeting summary
     */
    async generateSummary(): Promise<string> {
        if (!this.transcriptContext) {
            return 'No transcript available to summarize.';
        }

        const response = await this.sendMessage(
            'Please provide a comprehensive summary of this meeting including: main topics discussed, key decisions made, and any action items identified.'
        );

        return response.content;
    }

    /**
     * Extract action items from the meeting
     */
    async extractActionItems(): Promise<string> {
        if (!this.transcriptContext) {
            return 'No transcript available to extract action items from.';
        }

        const response = await this.sendMessage(
            'Please identify and list all action items from this meeting. For each action item, include who is responsible (if mentioned) and any deadlines discussed.'
        );

        return response.content;
    }

    /**
     * Get key decisions from the meeting
     */
    async getKeyDecisions(): Promise<string> {
        if (!this.transcriptContext) {
            return 'No transcript available to identify decisions from.';
        }

        const response = await this.sendMessage(
            'What were the key decisions made during this meeting? Please list each decision clearly.'
        );

        return response.content;
    }
}

// Singleton instance
export const aiChatService = new AIChatService();
