import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Key, 
  Save, 
  Eye, 
  EyeOff,
  Check,
  AlertCircle,
  Mic,
  MessageSquare
} from 'lucide-react';
import { transcriptionService, aiChatService } from '@/services';
import './SettingsPage.css';

interface APIKeys {
  openaiKey: string;
  anthropicKey: string;
  groqKey: string;
}

interface SettingsState {
  apiKeys: APIKeys;
  aiProvider: 'openai' | 'anthropic' | 'groq';
  aiModel: string;
  transcriptionLanguage: string;
}

const AI_MODELS = {
  openai: [
    { value: 'gpt-4o-mini', label: 'GPT-4 Mini (Fast & Affordable)' },
    { value: 'gpt-4o', label: 'GPT-4 (Most Capable)' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (Legacy)' },
  ],
  anthropic: [
    { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku (Fast)' },
    { value: 'claude-3-sonnet-20240229', label: 'Claude 3 Sonnet (Balanced)' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus (Most Capable)' },
  ],
  groq: [
    { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B (Versatile)' },
    { value: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B (Fast)' },
    { value: 'meta-llama/llama-guard-4-12b', label: 'Llama Guard 4 12B' },
  ],
};

const LANGUAGES = [
  { value: '', label: 'Auto-detect' },
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'ar', label: 'Arabic' },
  { value: 'hi', label: 'Hindi' },
  { value: 'ru', label: 'Russian' },
];

export function SettingsPage() {
  const [settings, setSettings] = useState<SettingsState>({
    apiKeys: {
      openaiKey: '',
      anthropicKey: '',
      groqKey: '',
    },
    aiProvider: 'openai',
    aiModel: 'gpt-4o-mini',
    transcriptionLanguage: '',
  });

  const [showKeys, setShowKeys] = useState({
    openai: false,
    anthropic: false,
    groq: false,
  });

  const [saved, setSaved] = useState(false);
  const [testResults, setTestResults] = useState<{
    transcription?: boolean;
    ai?: boolean;
  }>({});

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('meeting-assistant-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (e) {
        console.error('Failed to parse settings:', e);
      }
    }
  }, []);

  // Save settings
  const handleSave = () => {
    localStorage.setItem('meeting-assistant-settings', JSON.stringify(settings));

    // Configure services
    if (settings.apiKeys.openaiKey) {
      transcriptionService.configure({
        apiKey: settings.apiKeys.openaiKey,
        language: settings.transcriptionLanguage || undefined,
      });
    }

    let aiApiKey: string;
    if (settings.aiProvider === 'openai') {
      aiApiKey = settings.apiKeys.openaiKey;
    } else if (settings.aiProvider === 'groq') {
      aiApiKey = settings.apiKeys.groqKey;
    } else {
      aiApiKey = settings.apiKeys.anthropicKey;
    }

    if (aiApiKey) {
      aiChatService.configure({
        provider: {
          type: settings.aiProvider,
          apiKey: aiApiKey,
          model: settings.aiModel,
        },
      });
    }

    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Test transcription API
  const testTranscription = async () => {
    if (!settings.apiKeys.openaiKey) {
      setTestResults(prev => ({ ...prev, transcription: false }));
      return;
    }

    try {
      // Test Rev.ai API by fetching account info
      const response = await fetch('https://api.rev.ai/speechtotext/v1/account', {
        headers: {
          'Authorization': `Bearer ${settings.apiKeys.openaiKey}`,
        },
      });
      
      setTestResults(prev => ({ ...prev, transcription: response.ok }));
    } catch {
      setTestResults(prev => ({ ...prev, transcription: false }));
    }
  };

  // Test AI API
  const testAI = async () => {
    let apiKey: string;
    if (settings.aiProvider === 'openai') {
      apiKey = settings.apiKeys.openaiKey;
    } else if (settings.aiProvider === 'groq') {
      apiKey = settings.apiKeys.groqKey;
    } else {
      apiKey = settings.apiKeys.anthropicKey;
    }

    if (!apiKey) {
      setTestResults(prev => ({ ...prev, ai: false }));
      return;
    }

    try {
      if (settings.aiProvider === 'openai') {
        const response = await fetch('https://api.openai.com/v1/models', {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
          },
        });
        setTestResults(prev => ({ ...prev, ai: response.ok }));
      } else if (settings.aiProvider === 'groq') {
        const response = await fetch('https://api.groq.com/openai/v1/models', {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
          },
        });
        setTestResults(prev => ({ ...prev, ai: response.ok }));
      } else {
        // Anthropic doesn't have a simple auth test endpoint
        // We'll just validate the key format
        setTestResults(prev => ({ ...prev, ai: apiKey.startsWith('sk-ant-') }));
      }
    } catch {
      setTestResults(prev => ({ ...prev, ai: false }));
    }
  };

  const updateApiKey = (key: 'openaiKey' | 'anthropicKey' | 'groqKey', value: string) => {
    setSettings(prev => ({
      ...prev,
      apiKeys: { ...prev.apiKeys, [key]: value },
    }));
    setTestResults({});
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <SettingsIcon className="header-icon" />
        <div>
          <h1>Settings</h1>
          <p>Configure your API keys and preferences</p>
        </div>
      </div>

      <div className="settings-content">
        {/* API Keys Section */}
        <section className="settings-section">
          <div className="section-header">
            <Key className="section-icon" />
            <h2>API Keys</h2>
          </div>
          <p className="section-description">
            Enter your API keys to enable transcription and AI features.
            Keys are stored locally and never sent to our servers.
            Get your Rev.ai key at: https://www.rev.ai/access_token
          </p>

          <div className="settings-group">
            <label className="settings-label">
              <span>Rev.ai API Key</span>
              <span className="label-hint">Required for transcription with speaker diarization</span>
            </label>
            <div className="input-with-button">
              <input
                type={showKeys.openai ? 'text' : 'password'}
                value={settings.apiKeys.openaiKey}
                onChange={e => updateApiKey('openaiKey', e.target.value)}
                placeholder="02..."
                className="settings-input"
              />
              <button 
                className="icon-button"
                onClick={() => setShowKeys(prev => ({ ...prev, openai: !prev.openai }))}
                title={showKeys.openai ? 'Hide' : 'Show'}
              >
                {showKeys.openai ? <EyeOff /> : <Eye />}
              </button>
              <button 
                className="test-button"
                onClick={testTranscription}
                title="Test API Key"
              >
                {testResults.transcription === true && <Check className="success" />}
                {testResults.transcription === false && <AlertCircle className="error" />}
                {testResults.transcription === undefined && 'Test'}
              </button>
            </div>
          </div>

          <div className="settings-group">
            <label className="settings-label">
              <span>Anthropic API Key</span>
              <span className="label-hint">Optional, for Claude models</span>
            </label>
            <div className="input-with-button">
              <input
                type={showKeys.anthropic ? 'text' : 'password'}
                value={settings.apiKeys.anthropicKey}
                onChange={e => updateApiKey('anthropicKey', e.target.value)}
                placeholder="sk-ant-..."
                className="settings-input"
              />
              <button 
                className="icon-button"
                onClick={() => setShowKeys(prev => ({ ...prev, anthropic: !prev.anthropic }))}
                title={showKeys.anthropic ? 'Hide' : 'Show'}
              >
                {showKeys.anthropic ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </div>

          <div className="settings-group">
            <label className="settings-label">
              <span>Groq API Key</span>
              <span className="label-hint">Optional, for Llama models (fast inference)</span>
            </label>
            <div className="input-with-button">
              <input
                type={showKeys.groq ? 'text' : 'password'}
                value={settings.apiKeys.groqKey}
                onChange={e => updateApiKey('groqKey', e.target.value)}
                placeholder="gsk_..."
                className="settings-input"
              />
              <button 
                className="icon-button"
                onClick={() => setShowKeys(prev => ({ ...prev, groq: !prev.groq }))}
                title={showKeys.groq ? 'Hide' : 'Show'}
              >
                {showKeys.groq ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </div>
        </section>

        {/* Transcription Settings */}
        <section className="settings-section">
          <div className="section-header">
            <Mic className="section-icon" />
            <h2>Transcription</h2>
          </div>

          <div className="settings-group">
            <label className="settings-label">
              <span>Language</span>
              <span className="label-hint">Select the meeting language for better accuracy</span>
            </label>
            <select
              value={settings.transcriptionLanguage}
              onChange={e => setSettings(prev => ({ ...prev, transcriptionLanguage: e.target.value }))}
              className="settings-select"
            >
              {LANGUAGES.map(lang => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>
        </section>

        {/* AI Assistant Settings */}
        <section className="settings-section">
          <div className="section-header">
            <MessageSquare className="section-icon" />
            <h2>AI Assistant</h2>
          </div>

          <div className="settings-group">
            <label className="settings-label">
              <span>AI Provider</span>
            </label>
            <div className="radio-group">
              <label className={`radio-option ${settings.aiProvider === 'openai' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="aiProvider"
                  value="openai"
                  checked={settings.aiProvider === 'openai'}
                  onChange={() => {
                    setSettings(prev => ({ 
                      ...prev, 
                      aiProvider: 'openai',
                      aiModel: 'gpt-4o-mini'
                    }));
                    setTestResults(prev => ({ ...prev, ai: undefined }));
                  }}
                />
                <span>OpenAI (GPT)</span>
              </label>
              <label className={`radio-option ${settings.aiProvider === 'anthropic' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="aiProvider"
                  value="anthropic"
                  checked={settings.aiProvider === 'anthropic'}
                  onChange={() => {
                    setSettings(prev => ({ 
                      ...prev, 
                      aiProvider: 'anthropic',
                      aiModel: 'claude-3-haiku-20240307'
                    }));
                    setTestResults(prev => ({ ...prev, ai: undefined }));
                  }}
                />
                <span>Anthropic (Claude)</span>
              </label>
              <label className={`radio-option ${settings.aiProvider === 'groq' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="aiProvider"
                  value="groq"
                  checked={settings.aiProvider === 'groq'}
                  onChange={() => {
                    setSettings(prev => ({ 
                      ...prev, 
                      aiProvider: 'groq',
                      aiModel: 'llama-3.3-70b-versatile'
                    }));
                    setTestResults(prev => ({ ...prev, ai: undefined }));
                  }}
                />
                <span>Groq (Llama)</span>
              </label>
            </div>
          </div>

          <div className="settings-group">
            <label className="settings-label">
              <span>Model</span>
            </label>
            <div className="input-with-button">
              <select
                value={settings.aiModel}
                onChange={e => setSettings(prev => ({ ...prev, aiModel: e.target.value }))}
                className="settings-select"
              >
                {AI_MODELS[settings.aiProvider].map(model => (
                  <option key={model.value} value={model.value}>
                    {model.label}
                  </option>
                ))}
              </select>
              <button 
                className="test-button"
                onClick={testAI}
                title="Test API Connection"
              >
                {testResults.ai === true && <Check className="success" />}
                {testResults.ai === false && <AlertCircle className="error" />}
                {testResults.ai === undefined && 'Test'}
              </button>
            </div>
          </div>
        </section>

        {/* Save Button */}
        <div className="settings-actions">
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
      </div>
    </div>
  );
}
