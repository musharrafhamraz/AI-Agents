// Integration Service
// Handles syncing notes and action items to external platforms (Slack, Notion, etc.)

import type { Note } from '@/types';

export interface IntegrationConfig {
    slack?: {
        enabled: boolean;
        webhookUrl?: string;
        botToken?: string;
        channel?: string;
    };
    notion?: {
        enabled: boolean;
        apiKey?: string;
        databaseId?: string;
    };
}

export interface SyncResult {
    platform: string;
    success: boolean;
    error?: string;
    itemId?: string;
}

class IntegrationService {
    private config: IntegrationConfig = {};

    /**
     * Configure integrations
     */
    configure(config: IntegrationConfig): void {
        this.config = config;
        console.log('Integration service configured:', {
            slack: config.slack?.enabled,
            notion: config.notion?.enabled,
        });
    }

    /**
     * Check if any integration is enabled
     */
    isEnabled(): boolean {
        return !!(this.config.slack?.enabled || this.config.notion?.enabled);
    }

    /**
     * Sync a note to all enabled platforms
     */
    async syncNote(note: Note, meetingTitle: string): Promise<SyncResult[]> {
        const results: SyncResult[] = [];

        // Sync to Slack
        if (this.config.slack?.enabled) {
            const result = await this.syncToSlack(note, meetingTitle);
            results.push(result);
        }

        // Sync to Notion
        if (this.config.notion?.enabled) {
            const result = await this.syncToNotion(note, meetingTitle);
            results.push(result);
        }

        return results;
    }

    /**
     * Sync multiple notes at once
     */
    async syncNotes(notes: Note[], meetingTitle: string): Promise<SyncResult[]> {
        const results: SyncResult[] = [];

        for (const note of notes) {
            const noteResults = await this.syncNote(note, meetingTitle);
            results.push(...noteResults);
        }

        return results;
    }

    /**
     * Sync to Slack
     */
    private async syncToSlack(note: Note, meetingTitle: string): Promise<SyncResult> {
        if (!this.config.slack) {
            return { platform: 'slack', success: false, error: 'Slack not configured' };
        }

        try {
            const { webhookUrl, botToken, channel } = this.config.slack;

            // Format message based on note type
            const emoji = this.getNoteEmoji(note.note_type);
            const message = this.formatSlackMessage(note, meetingTitle, emoji);

            // Use webhook if available (simpler)
            if (webhookUrl) {
                const response = await fetch(webhookUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(message),
                });

                if (!response.ok) {
                    throw new Error(`Slack webhook failed: ${response.statusText}`);
                }

                console.log(`Synced to Slack: ${note.note_type} - ${note.content}`);
                return { platform: 'slack', success: true };
            }

            // Use bot token if webhook not available
            if (botToken && channel) {
                const response = await fetch('https://slack.com/api/chat.postMessage', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${botToken}`,
                    },
                    body: JSON.stringify({
                        channel,
                        ...message,
                    }),
                });

                const data = await response.json();

                if (!data.ok) {
                    throw new Error(`Slack API error: ${data.error}`);
                }

                console.log(`Synced to Slack: ${note.note_type} - ${note.content}`);
                return { platform: 'slack', success: true, itemId: data.ts };
            }

            throw new Error('Slack webhook URL or bot token required');
        } catch (error) {
            console.error('Slack sync error:', error);
            return {
                platform: 'slack',
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }

    /**
     * Sync to Notion
     */
    private async syncToNotion(note: Note, meetingTitle: string): Promise<SyncResult> {
        if (!this.config.notion?.apiKey || !this.config.notion?.databaseId) {
            return { platform: 'notion', success: false, error: 'Notion not configured' };
        }

        try {
            const { apiKey, databaseId } = this.config.notion;

            // Create page in Notion database
            const response = await fetch('https://api.notion.com/v1/pages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`,
                    'Notion-Version': '2022-06-28',
                },
                body: JSON.stringify({
                    parent: { database_id: databaseId },
                    properties: this.formatNotionProperties(note, meetingTitle),
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(`Notion API error: ${data.message || response.statusText}`);
            }

            console.log(`Synced to Notion: ${note.note_type} - ${note.content}`);
            return { platform: 'notion', success: true, itemId: data.id };
        } catch (error) {
            console.error('Notion sync error:', error);
            return {
                platform: 'notion',
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }

    /**
     * Format Slack message
     */
    private formatSlackMessage(note: Note, meetingTitle: string, emoji: string) {
        const timestamp = new Date(note.timestamp).toLocaleTimeString();
        
        let text = `${emoji} *${this.getNoteTypeLabel(note.note_type)}* from "${meetingTitle}"`;
        
        const blocks = [
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `${emoji} *${this.getNoteTypeLabel(note.note_type)}*\n${note.content}`,
                },
            },
            {
                type: 'context',
                elements: [
                    {
                        type: 'mrkdwn',
                        text: `From: *${meetingTitle}* | Time: ${timestamp}`,
                    },
                ],
            },
        ];

        // Add assignee if it's an action item
        if (note.note_type === 'action-item' && note.assignee) {
            blocks.splice(1, 0, {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `👤 *Assignee:* ${note.assignee}`,
                },
            });
        }

        // Add deadline if present
        if (note.deadline) {
            const deadline = new Date(note.deadline).toLocaleDateString();
            blocks.splice(1, 0, {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `📅 *Deadline:* ${deadline}`,
                },
            });
        }

        return { text, blocks };
    }

    /**
     * Format Notion properties
     */
    private formatNotionProperties(note: Note, meetingTitle: string) {
        const properties: any = {
            Name: {
                title: [
                    {
                        text: {
                            content: note.content.substring(0, 100), // Notion title limit
                        },
                    },
                ],
            },
            Type: {
                select: {
                    name: this.getNoteTypeLabel(note.note_type),
                },
            },
            Meeting: {
                rich_text: [
                    {
                        text: {
                            content: meetingTitle,
                        },
                    },
                ],
            },
            Status: {
                select: {
                    name: note.completed ? 'Done' : 'To Do',
                },
            },
        };

        // Add assignee if present
        if (note.assignee) {
            properties.Assignee = {
                rich_text: [
                    {
                        text: {
                            content: note.assignee,
                        },
                    },
                ],
            };
        }

        // Add deadline if present
        if (note.deadline) {
            properties.Deadline = {
                date: {
                    start: new Date(note.deadline).toISOString().split('T')[0],
                },
            };
        }

        return properties;
    }

    /**
     * Get emoji for note type
     */
    private getNoteEmoji(noteType: string): string {
        const emojiMap: Record<string, string> = {
            'action-item': '✅',
            'key-point': '📌',
            'decision': '🎯',
            'question': '❓',
            'follow-up': '📝',
        };
        return emojiMap[noteType] || '📄';
    }

    /**
     * Get label for note type
     */
    private getNoteTypeLabel(noteType: string): string {
        const labelMap: Record<string, string> = {
            'action-item': 'Action Item',
            'key-point': 'Key Point',
            'decision': 'Decision',
            'question': 'Question',
            'follow-up': 'Follow-up',
        };
        return labelMap[noteType] || 'Note';
    }

    /**
     * Test Slack connection
     */
    async testSlack(): Promise<{ success: boolean; error?: string }> {
        if (!this.config.slack?.enabled) {
            return { success: false, error: 'Slack not enabled' };
        }

        try {
            const { webhookUrl, botToken } = this.config.slack;

            if (webhookUrl) {
                const response = await fetch(webhookUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: '✅ Meeting Assistant integration test successful!',
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Webhook test failed: ${response.statusText}`);
                }

                return { success: true };
            }

            if (botToken) {
                const response = await fetch('https://slack.com/api/auth.test', {
                    headers: {
                        'Authorization': `Bearer ${botToken}`,
                    },
                });

                const data = await response.json();

                if (!data.ok) {
                    throw new Error(`Bot token test failed: ${data.error}`);
                }

                return { success: true };
            }

            throw new Error('No webhook URL or bot token configured');
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }

    /**
     * Test Notion connection
     */
    async testNotion(): Promise<{ success: boolean; error?: string }> {
        if (!this.config.notion?.enabled || !this.config.notion?.apiKey) {
            return { success: false, error: 'Notion not enabled or API key missing' };
        }

        try {
            const { apiKey, databaseId } = this.config.notion;

            // Test by retrieving database info
            if (databaseId) {
                const response = await fetch(`https://api.notion.com/v1/databases/${databaseId}`, {
                    headers: {
                        'Authorization': `Bearer ${apiKey}`,
                        'Notion-Version': '2022-06-28',
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(`Database test failed: ${data.message || response.statusText}`);
                }

                return { success: true };
            }

            // Just test auth if no database ID
            const response = await fetch('https://api.notion.com/v1/users/me', {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Notion-Version': '2022-06-28',
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(`Auth test failed: ${data.message || response.statusText}`);
            }

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
}

// Singleton instance
export const integrationService = new IntegrationService();
