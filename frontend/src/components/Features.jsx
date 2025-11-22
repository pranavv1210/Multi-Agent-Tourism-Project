import React from 'react';

const Features = () => {
  return (
    <>
      <div className="wave-divider">
        <svg viewBox="0 0 1200 100" preserveAspectRatio="none">
          <path d="M0,50 Q300,0 600,50 T1200,50 L1200,100 L0,100 Z" fill="#F8F9FB" />
        </svg>
      </div>
      <section id="features" className="features-section">
        <h2 className="section-title">Powerful Features for Smarter Travel</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3 className="feature-title">AI-Powered Travel Agent</h3>
            <p className="feature-description">Get intelligent recommendations tailored to your preferences and travel style</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌤️</div>
            <h3 className="feature-title">Real-Time Weather Insights</h3>
            <p className="feature-description">Stay informed with accurate weather forecasts for your destination</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🗺️</div>
            <h3 className="feature-title">Top Attractions & Must-Visit Places</h3>
            <p className="feature-description">Discover popular landmarks and hidden gems at every destination</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">�</div>
            <h3 className="feature-title">Smart Itinerary Suggestions</h3>
            <p className="feature-description">Optimized travel plans that make the most of your time</p>
          </div>
        </div>
      </section>
      <section id="about" className="about-section">
        <div className="about-content">
          <h2 className="about-title">Plan Smarter Trips with Real Data</h2>
          <p className="about-text">
            Plan smarter trips with accurate, API-driven insights. Powered by real data from Open-Meteo, Nominatim, and Overpass.
          </p>
          <div className="tech-badges">
            <span className="tech-badge">Open-Meteo API</span>
            <span className="tech-badge">Nominatim</span>
            <span className="tech-badge">Overpass API</span>
            <span className="tech-badge">FastAPI</span>
            <span className="tech-badge">React</span>
          </div>
        </div>
      </section>
    </>
  );
};

export default Features;
