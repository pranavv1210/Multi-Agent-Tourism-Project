import React, { useState, useEffect } from 'react';

const DestinationImage = ({ place }) => {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!place) return;

    // Extract city name (before first comma)
    const cityName = place.split(',')[0].trim();
    
    // Use Unsplash Source API (no API key needed for basic use)
    // Or fallback to Lorem Picsum for testing
    const unsplashUrl = `https://source.unsplash.com/1600x900/?${encodeURIComponent(cityName)},travel,landmark`;
    
    // Preload image
    const img = new Image();
    img.onload = () => {
      setImageUrl(unsplashUrl);
      setLoading(false);
    };
    img.onerror = () => {
      // Fallback to generic travel image
      setImageUrl('https://source.unsplash.com/1600x900/?travel,city');
      setLoading(false);
    };
    img.src = unsplashUrl;

  }, [place]);

  if (!place) return null;

  return (
    <div className="destination-image-container">
      {loading ? (
        <div className="image-skeleton">
          <div className="shimmer"></div>
        </div>
      ) : (
        <div className="destination-image" style={{ backgroundImage: `url(${imageUrl})` }}>
          <div className="image-overlay">
            <h2 className="destination-title">{place.split(',')[0]}</h2>
          </div>
        </div>
      )}
    </div>
  );
};

export default DestinationImage;
