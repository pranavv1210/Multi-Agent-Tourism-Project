import React from 'react';

const Navbar = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleAuthClick = (action) => {
    // Placeholder for future authentication implementation
    console.log(`${action} clicked - authentication not yet implemented`);
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="brand">Tourism Orchestrator</div>
        <div className="nav-center">
          <button className="nav-btn" onClick={() => scrollToSection('features')}>Features</button>
          <button className="nav-btn" onClick={() => scrollToSection('about')}>About</button>
          <button className="nav-btn" onClick={() => scrollToSection('how-it-works')}>How It Works</button>
        </div>
        <div className="nav-auth">
          <button className="auth-btn combined-auth-btn" onClick={() => handleAuthClick('Auth')}>Login / Signup</button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
