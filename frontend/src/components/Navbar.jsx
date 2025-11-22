import React from 'react';

const Navbar = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="brand" onClick={scrollToTop} style={{ cursor: 'pointer' }}>Tourism Orchestrator</div>
        <div className="nav-center" style={{ marginLeft: 'auto' }}>
          <button className="nav-btn" onClick={() => scrollToSection('features')}>Features</button>
          <button className="nav-btn" onClick={() => scrollToSection('about')}>About</button>
          <button className="nav-btn" onClick={() => scrollToSection('how-it-works')}>How It Works</button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
