import { useState, useEffect } from 'react';
import { 
  Zap, 
  Save, 
  Check,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { integrationService } from '@/services';
import './IntegrationsPage.css';

interface IntegrationSettings {
  slack: {
    enabled: boolean;
    webhookUrl: string;
    botToken: string;
    channel: string;
  };
  notion: {
    enabled: boolean;
    apiKey: string;
    databaseId: string;
  };
}

export function IntegrationsPage() {
  const [settings, setSettings] = useState<IntegrationSettings>({
    slack: {
      enabled: false,
      webhookUrl: '',
      botToken: '',
      channel: '',
    },
    notion: {
      enabled: false,
      apiKey: '',
      databaseId: '',
    },
  });

  const [saved, setSaved] = useState(false);
  const [testResults, setTestResults] = useState<{
    slack?: boolean;
    notion?: boolean;
  }>({});

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('meeting-assistant-integrations');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (e) {
        console.error('Failed to parse integration settings:', e);
      }
    }
  }, []);

  // Save settings
  const handleSave = () => {
    localStorage.setItem('meeting-assistant-integrations', JSON.stringify(settings));

    // Configure integration service
    integrationService.configure({
      slack: settings.slack.enabled ? {
        enabled: true,
        webhookUrl: settings.slack.webhookUrl || undefined,
        botToken: settings.slack.botToken || undefined,
        channel: settings.slack.channel || undefined,
      } : { enabled: false },
      notion: settings.notion.enabled ? {
        enabled: true,
        apiKey: settings.notion.apiKey || undefined,
        databaseId: settings.notion.databaseId || undefined,
      } : { enabled: false },
    });

    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Test Slack connection
  const testSlack = async () => {
    const result = await integrationService.testSlack();
    setTestResults(prev => ({ ...prev, slack: result.success }));
    
    if (!result.success) {
      alert(`Slack test failed: ${result.error}`);
    }
  };

  // Test Notion connection
  const testNotion = async () => {
    const result = await integrationService.testNotion();
    setTestResults(prev => ({ ...prev, notion: result.success }));
    
    if (!result.success) {
      alert(`Notion test failed: ${result.error}`);
    }
  };

  return (
    <div className="integrations-page">
      <div className="integrations-header">
        <Zap className="header-icon" />
        <div>
          <h1>Integrations</h1>
          <p>Connect your meeting notes to external tools</p>
        </div>
      </div>

      <div className="integrations-content">
        {/* Slack Integration */}
        <section className="integration-section">
          <div className="integration-header">
            <div className="integration-title">
              <img 
                src="https://cdn.simpleicons.org/slack" 
                alt="Slack" 
                className="integration-icon"
              />
              <div>
                <h2>Slack</h2>
                <p>Send meeting notes and action items to Slack channels</p>
              </div>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={settings.slack.enabled}
                onChange={e => setSettings(prev => ({
                  ...prev,
                  slack: { ...prev.slack, enabled: e.target.checked }
                }))}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {settings.slack.enabled && (
            <div className="integration-config">
              <div className="config-group">
                <label>Webhook URL (Recommended)</label>
                <input
                  type="text"
                  value={settings.slack.webhookUrl}
                  onChange={e => setSettings(prev => ({
                    ...prev,
                    slack: { ...prev.slack, webhookUrl: e.target.value }
                  }))}
                  placeholder="https://hooks.slack.com/services/..."
                />
                <span className="hint">
                  <a href="https://api.slack.com/messaging/webhooks" target="_blank" rel="noopener noreferrer">
                    Create a webhook <ExternalLink size={12} />
                  </a>
                </span>
              </div>

              <div className="config-divider">OR</div>

              <div className="config-group">
                <label>Bot Token</label>
                <input
                  type="password"
                  value={settings.slack.botToken}
                  onChange={e => setSettings(prev => ({
                    ...prev,
                    slack: { ...prev.slack, botToken: e.target.value }
                  }))}
                  placeholder="xoxb-..."
                />
              </div>

              <div className="config-group">
                <label>Channel</label>
                <input
                  type="text"
                  value={settings.slack.channel}
                  onChange={e => setSettings(prev => ({
                    ...prev,
                    slack: { ...prev.slack, channel: e.target.value }
                  }))}
                  placeholder="#meeting-notes"
                />
              </div>

              <button className="test-button" onClick={testSlack}>
                {testResults.slack === true && <Check className="success" />}
                {testResults.slack === false && <AlertCircle className="error" />}
                {testResults.slack === undefined && 'Test Connection'}
              </button>
            </div>
          )}
        </section>

        {/* Notion Integration */}
        <section className="integration-section">
          <div className="integration-header">
            <div className="integration-title">
              <img 
                src="https://cdn.simpleicons.org/notion" 
                alt="Notion" 
                className="integration-icon"
              />
              <div>
                <h2>Notion</h2>
                <p>Create tasks in your Notion database automatically</p>
              </div>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={settings.notion.enabled}
                onChange={e => setSettings(prev => ({
                  ...prev,
                  notion: { ...prev.notion, enabled: e.target.checked }
                }))}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {settings.notion.enabled && (
            <div className="integration-config">
              <div className="config-group">
                <label>Integration Token</label>
                <input
                  type="password"
                  value={settings.notion.apiKey}
                  onChange={e => setSettings(prev => ({
                    ...prev,
                    notion: { ...prev.notion, apiKey: e.target.value }
                  }))}
                  placeholder="secret_..."
                />
                <span className="hint">
                  <a href="https://www.notion.so/my-integrations" target="_blank" rel="noopener noreferrer">
                    Create an integration <ExternalLink size={12} />
                  </a>
                </span>
              </div>

              <div className="config-group">
                <label>Database ID</label>
                <input
                  type="text"
                  value={settings.notion.databaseId}
                  onChange={e => setSettings(prev => ({
                    ...prev,
                    notion: { ...prev.notion, databaseId: e.target.value }
                  }))}
                  placeholder="abc123..."
                />
                <span className="hint">
                  Found in the database URL after the workspace name
                </span>
              </div>

              <button className="test-button" onClick={testNotion}>
                {testResults.notion === true && <Check className="success" />}
                {testResults.notion === false && <AlertCircle className="error" />}
                {testResults.notion === undefined && 'Test Connection'}
              </button>
            </div>
          )}
        </section>

        {/* Save Button */}
        <div className="integrations-actions">
          <button className={`save-button ${saved ? 'saved' : ''}`} onClick={handleSave}>
            {saved ? (
              <>
                <Check /> Saved!
              </>
            ) : (
              <>
                <Save /> Save Settings
              </>
            )}
          </button>
        </div>

        {/* Info Box */}
        <div className="info-box">
          <h3>How it works</h3>
          <ul>
            <li>When notes are generated during a meeting, they're automatically sent to your connected platforms</li>
            <li>Action items become tasks in Notion with assignees and deadlines</li>
            <li>Key points and decisions are posted to Slack for team visibility</li>
            <li>You can manually sync notes from the meeting history page</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
