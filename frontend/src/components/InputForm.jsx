import React, { useState, useEffect } from 'react';
import { planRequest } from '../api/planApi.js';

const InputForm = ({ onResult, setLoading, setError }) => {
  const [message, setMessage] = useState('');
  const [wantWeather, setWantWeather] = useState(true);
  const [wantPlaces, setWantPlaces] = useState(true);
  const [isListening, setIsListening] = useState(false);

  // Load persisted state
  useEffect(() => {
    const savedMsg = localStorage.getItem('lastQuery');
    const savedWeather = localStorage.getItem('wantWeather');
    const savedPlaces = localStorage.getItem('wantPlaces');
    if (savedMsg) setMessage(savedMsg);
    if (savedWeather !== null) setWantWeather(savedWeather === 'true');
    if (savedPlaces !== null) setWantPlaces(savedPlaces === 'true');
  }, []);

  // Persist changes
  useEffect(() => { localStorage.setItem('lastQuery', message); }, [message]);
  useEffect(() => { localStorage.setItem('wantWeather', String(wantWeather)); }, [wantWeather]);
  useEffect(() => { localStorage.setItem('wantPlaces', String(wantPlaces)); }, [wantPlaces]);

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('🎙️ Voice input not supported in this browser. Try Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error !== 'no-speech') {
        setError(`🎙️ Voice input error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate input
    if (!message.trim()) {
      setError('🗺️ Please enter a destination to plan your trip');
      return;
    }
    
    // Validate at least one intent is selected
    if (!wantWeather && !wantPlaces) {
      setError('⚠️ Please select at least Weather or Places');
      return;
    }
    
    setError(null);
    onResult(null);
    setLoading(true);
    try {
      const intents = [];
      if (wantWeather) intents.push('weather');
      if (wantPlaces) intents.push('places');
      const data = await planRequest(message, intents);
      onResult(data);
    } catch (err) {
      setError(err.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <div style={{ position: 'relative', width: '100%' }}>
          <textarea
            className="glass-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            placeholder="Where would you like to travel?"
            rows={1}
            style={{ paddingRight: '50px', resize: 'vertical', minHeight: '56px', maxHeight: '200px', width: '100%' }}
          />
          <button
            type="button"
            onClick={handleVoiceInput}
            className={`voice-btn-inline ${isListening ? 'listening' : ''}`}
            title="Voice input"
            aria-label="Voice input"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>
        </div>
        <button type="submit" className="cta-button" style={{ width: '100%' }}>Plan My Trip</button>
      </div>
      <div className="toggle-row">
        <button 
          type="button"
          className={`toggle-btn ${wantWeather ? 'active' : ''}`}
          onClick={() => setWantWeather(!wantWeather)}
        >
          🌤️ Weather
        </button>
        <button 
          type="button"
          className={`toggle-btn ${wantPlaces ? 'active' : ''}`}
          onClick={() => setWantPlaces(!wantPlaces)}
        >
          🗺️ Places
        </button>
      </div>
    </form>
  );
};

export default InputForm;
