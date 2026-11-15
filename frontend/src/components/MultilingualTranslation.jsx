import React, { useState } from 'react';
import { 
  Languages, 
  Volume2, 
  VolumeX, 
  Copy, 
  Check, 
  Globe, 
  Key, 
  ExternalLink 
} from 'lucide-react';

const REGIONAL_LANGUAGES = [
  { code: 'hi', name: 'Hindi (हिन्दी)', speechCode: 'hi-IN' },
  { code: 'ta', name: 'Tamil (தமிழ்)', speechCode: 'ta-IN' },
  { code: 'te', name: 'Telugu (తెలుగు)', speechCode: 'te-IN' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)', speechCode: 'kn-IN' },
  { code: 'mr', name: 'Marathi (मराठी)', speechCode: 'mr-IN' },
  { code: 'bn', name: 'Bengali (বাংলা)', speechCode: 'bn-IN' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)', speechCode: 'gu-IN' },
  { code: 'ml', name: 'Malayalam (മലയാളം)', speechCode: 'ml-IN' },
  { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)', speechCode: 'pa-IN' },
  { code: 'ur', name: 'Urdu (اردو)', speechCode: 'ur-IN' },
];

export default function MultilingualTranslation({
  synthesizedEnglish,
  targetLang,
  translatedResult,
  isTranslating,
  hasGoogleKey,
  onSelectLanguage,
  onOpenSettings,
}) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [copied, setCopied] = useState(false);

  const selectedLangObj = REGIONAL_LANGUAGES.find(l => l.code === targetLang) || REGIONAL_LANGUAGES[0];

  const handleSpeak = () => {
    if (!translatedResult?.translated_text) return;
    
    // Check Web Speech API support
    if (!('speechSynthesis' in window)) {
      alert('Text-to-Speech is not supported in this browser.');
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(translatedResult.translated_text);
    utterance.lang = selectedLangObj.speechCode || 'en-IN';
    utterance.rate = 0.95;

    // Pick matching voice if available
    const voices = window.speechSynthesis.getVoices();
    const matchingVoice = voices.find(v => v.lang.startsWith(selectedLangObj.code));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = () => setIsPlayingAudio(true);
    utterance.onend = () => setIsPlayingAudio(false);
    utterance.onerror = () => setIsPlayingAudio(false);

    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = () => {
    if (translatedResult?.translated_text) {
      navigator.clipboard.writeText(translatedResult.translated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="multilingual-container">
      {/* Section Header with Language Selector Dropdown */}
      <div className="multilingual-header">
        <div className="multilingual-title-group">
          <Globe size={16} className="globe-icon" />
          <span className="section-label">REGIONAL MULTILINGUAL TRANSLATION</span>
        </div>

        <div className="multilingual-controls">
          <div className="lang-select-wrapper">
            <Languages size={14} className="lang-select-icon" />
            <select
              value={targetLang}
              onChange={(e) => onSelectLanguage(e.target.value)}
              className="lang-select-dropdown"
            >
              {REGIONAL_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div 
            className={`api-source-badge ${hasGoogleKey ? 'badge-google' : 'badge-local'}`}
            title={hasGoogleKey ? 'Using Google Cloud Translation API' : 'Using Offline Linguistic Engine (Configure Google API Key in Settings)'}
          >
            {hasGoogleKey ? 'Google Cloud API' : 'Linguistic Engine'}
          </div>
        </div>
      </div>

      {/* Main Regional Translation Card */}
      <div className="translation-card">
        <div className="translation-card-meta">
          <span className="target-lang-pill font-mono">
            TARGET: {selectedLangObj.name}
          </span>

          <div className="translation-card-actions">
            {translatedResult?.translated_text && (
              <>
                <button
                  onClick={handleSpeak}
                  className={`audio-btn ${isPlayingAudio ? 'playing' : ''}`}
                  title={`Speak aloud in ${selectedLangObj.name}`}
                >
                  <Volume2 size={15} />
                  <span>{isPlayingAudio ? 'Speaking...' : 'Listen Audio'}</span>
                </button>

                <button
                  onClick={handleCopy}
                  className="copy-btn"
                  title="Copy translation text"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </>
            )}
          </div>
        </div>

        <div className="translation-text-area">
          {isTranslating ? (
            <div className="translation-loading">
              <span className="loading-pulse"></span>
              <span>Translating into {selectedLangObj.name}...</span>
            </div>
          ) : translatedResult?.translated_text ? (
            <h2 className="translated-text-display font-display">
              {translatedResult.translated_text}
            </h2>
          ) : (
            <div className="translation-placeholder">
              <span>
                {synthesizedEnglish 
                  ? 'Ready for translation. Select target language above.'
                  : 'Perform signs or add tokens to generate native language translation.'}
              </span>
            </div>
          )}
        </div>

        {/* Footer info bar */}
        <div className="translation-card-footer">
          <div className="footer-source-note">
            <span>Engine: {translatedResult?.source === 'google_api' ? 'Google Cloud Translation (NMT)' : 'Built-in Linguistic Lexicon'}</span>
          </div>

          {!hasGoogleKey && (
            <button onClick={onOpenSettings} className="key-setup-link">
              <Key size={12} /> Add Google Cloud API Key for 100+ languages
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
