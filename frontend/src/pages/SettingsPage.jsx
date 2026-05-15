import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Save, 
  Trash2, 
  ShieldCheck, 
  Cpu, 
  Key, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { useConfig } from '../context/ConfigContext';

const SettingsPage = () => {
  const { llmConfig, updateConfig, clearConfig } = useConfig();
  const [formData, setFormData] = useState({
    provider: llmConfig.provider || '',
    model: llmConfig.model || '',
    apiKey: llmConfig.apiKey || '',
    customModel: ''
  });
  const [saved, setSaved] = useState(false);

  const providerOptions = ["OpenAI", "Groq", "Gemini", "Anthropic"];
  const modelOptionsMap = {
    "OpenAI": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "gpt-4o"],
    "Groq": ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
    "Gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    "Anthropic": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-latest"]
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
      // Reset model if provider changes
      ...(name === 'provider' ? { model: modelOptionsMap[value]?.[0] || '' } : {})
    }));
    setSaved(false);
  };

  const handleSave = () => {
    const finalModel = formData.model === 'Custom' ? formData.customModel : formData.model;
    updateConfig({
      provider: formData.provider.toLowerCase(),
      model: finalModel,
      apiKey: formData.apiKey
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleClear = () => {
    clearConfig();
    setFormData({
      provider: '',
      model: '',
      apiKey: '',
      customModel: ''
    });
  };

  const currentModels = modelOptionsMap[formData.provider] || [];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <div className="ds-brand-line" />
            <span className="ds-label-brand">System Configuration</span>
          </div>
          <h1 className="ds-heading-lg text-[var(--ds-text)]">AI Provider Settings</h1>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="ds-card p-8"
      >
        <div className="space-y-8">
          {/* Provider Selection */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Cpu size={20} className="text-brand" />
              <label className="ds-label text-[var(--ds-text)]">AI Provider</label>
            </div>
            <select
              name="provider"
              value={formData.provider}
              onChange={handleChange}
              className="w-full bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-xl px-4 py-3 text-[var(--ds-text)] outline-none focus:border-brand/50 transition-colors"
            >
              <option value="">Select a provider</option>
              {providerOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Model Selection */}
          {formData.provider && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="space-y-4"
            >
              <div className="flex items-center gap-3">
                <Settings size={20} className="text-brand" />
                <label className="ds-label text-[var(--ds-text)]">Model</label>
              </div>
              <select
                name="model"
                value={formData.model}
                onChange={handleChange}
                className="w-full bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-xl px-4 py-3 text-[var(--ds-text)] outline-none focus:border-brand/50 transition-colors"
              >
                {currentModels.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
                <option value="Custom">Custom Model ID</option>
              </select>

              {formData.model === 'Custom' && (
                <motion.input
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  type="text"
                  name="customModel"
                  value={formData.customModel}
                  onChange={handleChange}
                  placeholder="Enter custom model ID..."
                  className="w-full bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-xl px-4 py-3 text-[var(--ds-text)] outline-none focus:border-brand/50 transition-colors mt-2"
                />
              )}
            </motion.div>
          )}

          {/* API Key */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Key size={20} className="text-brand" />
              <label className="ds-label text-[var(--ds-text)]">API Key</label>
            </div>
            <div className="relative">
              <input
                type="password"
                name="apiKey"
                value={formData.apiKey}
                onChange={handleChange}
                placeholder="Enter your API key..."
                className="w-full bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-xl px-4 py-3 text-[var(--ds-text)] outline-none focus:border-brand/50 transition-colors"
              />
              <ShieldCheck className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--ds-text-faint)]" size={18} />
            </div>
            <p className="text-[11px] text-[var(--ds-text-faint)] italic">
              * Your API key is stored locally in your browser and is only sent to the AI provider bridge.
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button
              onClick={handleSave}
              disabled={!formData.provider || !formData.apiKey || (!formData.model && !formData.customModel)}
              className="ds-btn-primary flex-1 flex items-center justify-center gap-3 h-12 disabled:opacity-50"
            >
              <Save size={18} />
              SAVE CONFIGURATION
            </button>
            <button
              onClick={handleClear}
              className="flex-1 flex items-center justify-center gap-3 h-12 bg-[var(--ds-surface-2)] border border-[var(--ds-border)] text-[var(--ds-text)] rounded-xl hover:bg-[var(--ds-surface-3)] transition-colors ds-caption font-bold"
            >
              <Trash2 size={18} />
              CLEAR ALL
            </button>
          </div>

          {saved && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500"
            >
              <CheckCircle2 size={18} />
              <span className="text-sm font-bold">Configuration saved successfully!</span>
            </motion.div>
          )}

          {!llmConfig.apiKey && (
            <div className="flex items-center gap-3 p-4 bg-brand/10 border border-brand/20 rounded-xl text-brand">
              <AlertCircle size={18} />
              <span className="text-sm font-bold">No active configuration. AI features will be disabled.</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Info Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="ds-card p-6 border-l-4 border-brand">
          <h4 className="ds-label mb-2 text-brand uppercase">Active Session</h4>
          <div className="space-y-2">
            <p className="text-[13px] text-[var(--ds-text-muted)]">
              Provider: <span className="text-[var(--ds-text)] font-mono">{llmConfig.provider || 'None'}</span>
            </p>
            <p className="text-[13px] text-[var(--ds-text-muted)]">
              Model: <span className="text-[var(--ds-text)] font-mono">{llmConfig.model || 'None'}</span>
            </p>
            <p className="text-[13px] text-[var(--ds-text-muted)]">
              Key Status: <span className={llmConfig.apiKey ? "text-green-500" : "text-brand"}>
                {llmConfig.apiKey ? '✓ Configured' : '✗ Missing'}
              </span>
            </p>
          </div>
        </div>
        
        <div className="ds-card p-6 bg-gradient-to-br from-[var(--ds-surface-2)] to-transparent">
          <h4 className="ds-label mb-2 text-[var(--ds-text-faint)] uppercase">Security Note</h4>
          <p className="text-[12px] text-[var(--ds-text-muted)] leading-relaxed">
            Settings are persisted in your browser's local storage. We recommend clearing your configuration when using public devices.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
