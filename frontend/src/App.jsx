import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar.jsx';
import Landing from './components/Landing.jsx';
import InputForm from './components/InputForm.jsx';
import ResultCard from './components/ResultCard.jsx';
import MapView from './components/MapView.jsx';
import Features from './components/Features.jsx';
import HowItWorks from './components/HowItWorks.jsx';
import './styles.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [theme, setTheme] = useState('default');
  const [showSearchBar, setShowSearchBar] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [showWelcome, setShowWelcome] = useState(true);
  const [welcomeComplete, setWelcomeComplete] = useState(false);

  // Handle welcome animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowWelcome(false);
      setTimeout(() => setWelcomeComplete(true), 600);
    },1500);
    return () => clearTimeout(timer);
  }, []);

  // Handle scroll to hide/show search bar
  useEffect(() => {
    if (!hasSearched) return;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const searchBar = document.querySelector('.search-bar-sticky');
      
      if (!searchBar) return;
      
      const searchBarRect = searchBar.getBoundingClientRect();
      const searchBarTop = searchBar.offsetTop;
      
      // Show search bar only when user scrolls back to its original position
      if (currentScrollY <= searchBarTop - 80) {
        setShowSearchBar(true);
      } else {
        setShowSearchBar(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [hasSearched]);

  // Load shared plan from URL on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const planId = urlParams.get('plan');
    if (planId) {
      const savedPlan = localStorage.getItem(`plan_${planId}`);
      if (savedPlan) {
        try {
          const planData = JSON.parse(savedPlan);
          setResult(planData);
          setHasSearched(true);
        } catch (err) {
          console.error('Failed to load shared plan', err);
        }
      }
    }
  }, []);

  const handleResult = (r) => {
    setResult(r);
    if (r) {
      setHasSearched(true);
      // Auto-save to localStorage with timestamp
      const planId = Date.now().toString(36);
      localStorage.setItem(`plan_${planId}`, JSON.stringify(r));
      localStorage.setItem('lastPlanId', planId);
    }
  };

  const sharePlan = () => {
    const planId = localStorage.getItem('lastPlanId');
    if (!planId) {
      alert('No plan to share yet!');
      return;
    }
    const shareUrl = `${window.location.origin}${window.location.pathname}?plan=${planId}`;
    navigator.clipboard.writeText(shareUrl).then(() => {
      alert('📋 Share link copied to clipboard!');
    }).catch(() => {
      prompt('Copy this link to share:', shareUrl);
    });
  };

  return (
    <div className={`app-shell theme-${theme}`}>
      {showWelcome && (
        <div className={`welcome-screen ${!showWelcome ? 'fade-out' : ''}`}>
          <div className="welcome-content">
            <div className="welcome-icon">✈️</div>
            <h1 className="welcome-title">Welcome to Tourism Orchestrator</h1>
            <p className="welcome-subtitle">Your journey begins here...</p>
          </div>
        </div>
      )}
      {welcomeComplete && <Navbar />}
      {welcomeComplete && !hasSearched && (
        <>
          <Landing>
            <InputForm onResult={handleResult} setLoading={setLoading} setError={setError} />
          </Landing>
          <Features />
          <HowItWorks />
          <footer className="footer">
            <div className="footer-icons">
              <span>✈️</span>
              <span>🌍</span>
              <span>🧳</span>
            </div>
            <p className="footer-text">Built with FastAPI + React • Powered by Open-Meteo, Nominatim & Overpass</p>
          </footer>
        </>
      )}
      {welcomeComplete && hasSearched && (
        <main className="results-area">
          <div className={`search-bar-sticky ${showSearchBar ? 'visible' : 'hidden'}`}>
            <InputForm onResult={handleResult} setLoading={setLoading} setError={setError} />
          </div>
          {loading && (
            <div className="loading-container">
              <div className="plane-loader">
                <div className="plane">✈️</div>
                <div className="cloud cloud1">☁️</div>
                <div className="cloud cloud2">☁️</div>
                <div className="cloud cloud3">☁️</div>
              </div>
              <p className="loading-text">Planning your adventure...</p>
              <div className="skeleton-grid">
                <div className="skeleton-card" />
                <div className="skeleton-card" />
                <div className="skeleton-card" />
              </div>
            </div>
          )}
          {error && <p className="status error">{error}</p>}
          {result && (
            <>
              <div className="share-actions">
                <button onClick={sharePlan} className="share-btn" title="Share this plan">
                  🔗 Share Plan
                </button>
              </div>
              <div className="result-layout">
                <ResultCard result={result} />
                <MapView data={result} />
              </div>
            </>
          )}
          <footer className="footer">
            <div className="footer-icons">
              <span>✈️</span>
              <span>🌍</span>
              <span>🧳</span>
            </div>
            <p className="footer-text">Data sourced live from Nominatim, Overpass, and Open-Meteo</p>
          </footer>
        </main>
      )}
    </div>
  );
}

export default App;
