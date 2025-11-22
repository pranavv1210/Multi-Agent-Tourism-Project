import React, { useState, useEffect, useRef } from 'react';
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
  const [showNavbar, setShowNavbar] = useState(true);
  const [showTextbox, setShowTextbox] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [showWelcome, setShowWelcome] = useState(true);
  const [welcomeComplete, setWelcomeComplete] = useState(false);
  const [showColdStart, setShowColdStart] = useState(false);
  const scrollDir = useRef('up');

  // Handle welcome animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowWelcome(false);
      setTimeout(() => setWelcomeComplete(true), 600);
    },1500);
    return () => clearTimeout(timer);
  }, []);

  // Mobile scroll: hide navbar and textbox on scroll down, show on scroll up
  useEffect(() => {
    let ticking = false;
    let lastY = lastScrollY;
    const threshold = 12; // px
    const handleScroll = () => {
      if (window.innerWidth > 768) return;
      const currentScrollY = window.scrollY;
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (currentScrollY > lastY + threshold && currentScrollY > 40) {
            setShowNavbar(false);
            setShowTextbox(false);
            scrollDir.current = 'down';
            lastY = currentScrollY;
          } else if (currentScrollY < lastY - threshold) {
            setShowNavbar(true);
            setShowTextbox(true);
            scrollDir.current = 'up';
            lastY = currentScrollY;
          }
          setLastScrollY(currentScrollY);
          ticking = false;
        });
        ticking = true;
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
    // eslint-disable-next-line
  }, []);

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
      <div className={`navbar-anim${showNavbar ? ' shown' : ' hidden'}`}>{welcomeComplete && <>{showNavbar && <Navbar />}</>}</div>
      {welcomeComplete && !hasSearched && (
        <>
          <Landing>
            {showTextbox && (
              <InputForm onResult={handleResult} setLoading={setLoading} setError={setError} clearOnMount={true} setShowColdStart={setShowColdStart} />
            )}
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
          <div className={`search-bar-sticky${showTextbox ? ' visible' : ' hidden'}`}>
            {showTextbox && (
              <InputForm onResult={handleResult} setLoading={setLoading} setError={setError} clearOnMount={true} setShowColdStart={setShowColdStart} />
            )}
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
