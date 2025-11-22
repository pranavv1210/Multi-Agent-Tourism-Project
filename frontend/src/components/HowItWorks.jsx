import React from 'react';

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="how-it-works-section">
      <h2 className="section-title">How It Works</h2>
      <div className="steps-container">
        <div className="step-card">
          <div className="step-number">1</div>
          <h3 className="step-title">Enter Destination</h3>
          <p className="step-description">Simply type in where you want to go and let our AI handle the rest</p>
        </div>
        <div className="step-card">
          <div className="step-number">2</div>
          <h3 className="step-title">AI Fetches Data</h3>
          <p className="step-description">We gather real-time weather, attractions, and travel insights instantly</p>
        </div>
        <div className="step-card">
          <div className="step-number">3</div>
          <h3 className="step-title">Get Your Plan</h3>
          <p className="step-description">Receive a personalized travel summary with everything you need</p>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
