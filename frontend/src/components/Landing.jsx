import React from 'react';

const Landing = ({ children }) => {
  return (
    <section className="hero-section">
      <div className="hero-background">
        <svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="skyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#1a4070', stopOpacity: 1 }} />
              <stop offset="50%" style={{ stopColor: '#0A2540', stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: '#051628', stopOpacity: 1 }} />
            </linearGradient>
            <linearGradient id="mountainGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#2d5a7b', stopOpacity: 0.9 }} />
              <stop offset="100%" style={{ stopColor: '#1a3a54', stopOpacity: 0.9 }} />
            </linearGradient>
          </defs>
          <rect width="1200" height="800" fill="url(#skyGradient)" />
          <circle cx="100" cy="80" r="2" fill="white" opacity="0.8" />
          <circle cx="250" cy="120" r="1.5" fill="white" opacity="0.6" />
          <circle cx="400" cy="60" r="2" fill="white" opacity="0.9" />
          <circle cx="650" cy="100" r="1" fill="white" opacity="0.7" />
          <circle cx="900" cy="70" r="2" fill="white" opacity="0.8" />
          <circle cx="1050" cy="110" r="1.5" fill="white" opacity="0.6" />
          <path d="M 0 500 L 200 300 L 400 500 Z" fill="url(#mountainGradient)" opacity="0.7" />
          <path d="M 300 500 L 500 250 L 700 500 Z" fill="url(#mountainGradient)" opacity="0.8" />
          <path d="M 600 500 L 800 200 L 1000 500 Z" fill="url(#mountainGradient)" opacity="0.9" />
          <path d="M 900 500 L 1100 280 L 1200 500 Z" fill="url(#mountainGradient)" opacity="0.7" />
          <ellipse cx="600" cy="400" rx="300" ry="150" fill="#4CC9F0" opacity="0.05" />
        </svg>
      </div>
      <div className="floating-elements">
        <div className="float-icon">✈️</div>
        <div className="float-icon">🗺️</div>
        <div className="float-icon">🧳</div>
        <div className="float-icon">🌴</div>
      </div>
      <div className="hero-content">
        <div className="icon-row">
          <span className="icon-item">✈️</span>
          <span className="icon-item">📍</span>
          <span className="icon-item">🌍</span>
          <span className="icon-item">🧭</span>
        </div>
        <h1 className="hero-title">Discover Your Next Adventure</h1>
        <p className="hero-subtitle">Your Personal AI Travel Planner • Real-time Weather • Top Attractions • Smart Recommendations</p>
        <div className="glass-input-container">
          {children}
        </div>
      </div>
    </section>
  );
};

export default Landing;
