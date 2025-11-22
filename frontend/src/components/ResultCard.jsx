import React from 'react';
import WeatherForecast from './WeatherForecast.jsx';
import ItineraryBuilder from './ItineraryBuilder.jsx';

const ResultCard = ({ result }) => {
  const { place, weather, places, text, errors, lat, lon, intents, places_geo } = result || {};
  
  // Check if intents were requested
  const weatherRequested = intents?.includes('weather');
  const placesRequested = intents?.includes('places');
  
  const hasWeather = !!(weather && !weather.error);
  const hasWeatherError = !!(weather && weather.error);
  const hasPlaces = Array.isArray(places) && places.length > 0;

  return (
    <div className="result-card-grid" style={{ marginTop: '1rem', display: 'grid', gap: '1rem' }}>
      <section className="result-section summary-section">
        <h2 className="section-heading">Summary</h2>
        <p>{text || 'No summary available.'}</p>
        {errors && errors.length > 0 && (
          <ul style={{ color: '#ff6b6b', margin: '0.5rem 0 0', paddingLeft: '1.2rem' }}>
            {errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        )}
      </section>

      {weatherRequested && hasWeather && (
        <section className="result-section weather-section">
          <h3 className="section-subheading">Current Weather</h3>
          <p><strong>Temperature:</strong> {weather.temperature != null ? `${weather.temperature}°C` : 'N/A'}</p>
          <p><strong>Precipitation Probability:</strong> {weather.precipitation_probability != null ? `${weather.precipitation_probability}%` : 'N/A'}</p>
          <p><strong>Summary:</strong> {weather.summary || 'N/A'}</p>
        </section>
      )}

      {weatherRequested && hasWeatherError && (
        <section className="result-section weather-error-section" style={{ border: '1px solid #ff6b6b', background: 'rgba(255,107,107,0.08)' }}>
          <h3 className="section-subheading">Weather</h3>
          <p style={{ color: '#ff6b6b' }}>{weather.error}</p>
        </section>
      )}

      {placesRequested && hasPlaces && (
        <section className="result-section places-section">
          <h3 className="section-subheading">Places to Visit</h3>
          <ul style={{ listStyle: 'disc', paddingLeft: '1.25rem', margin: 0 }}>
            {places.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
          <ItineraryBuilder places={places} placesGeo={places_geo} />
        </section>
      )}

      {weatherRequested && hasWeather && weather.forecast && weather.forecast.length > 0 && (
        <section className="result-section forecast-section">
          <h3 className="section-subheading">7-Day Weather Forecast</h3>
          <WeatherForecast forecast={weather.forecast} />
        </section>
      )}

      <section className="result-section meta-section" style={{ fontSize: '0.85rem', opacity: 0.75 }}>
        <p><strong>Resolved Place:</strong> {place || 'Unknown'}</p>
        {lat != null && lon != null && (
          <p><strong>Coordinates:</strong> {lat.toFixed(4)}, {lon.toFixed(4)}</p>
        )}
        {result?.geocode_source === 'static' && (
          <p style={{ marginTop: '0.25rem', color: '#ffc107' }}>Using static location fallback.</p>
        )}
        {!weatherRequested && !placesRequested && (
          <p style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>No data blocks requested.</p>
        )}
        {(weatherRequested || placesRequested) && !hasWeather && !hasPlaces && (
          <p style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>Requested data not available.</p>
        )}
      </section>
    </div>
  );
};

export default ResultCard;
