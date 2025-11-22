import React from 'react';

const WeatherForecast = ({ forecast }) => {
  if (!forecast || forecast.length === 0) return null;

  const getWeatherEmoji = (summary) => {
    if (!summary) return '🌤️';
    const lower = summary.toLowerCase();
    if (lower.includes('clear')) return '☀️';
    if (lower.includes('cloud')) return '☁️';
    if (lower.includes('rain') || lower.includes('drizzle')) return '🌧️';
    if (lower.includes('snow')) return '❄️';
    if (lower.includes('thunder')) return '⛈️';
    if (lower.includes('fog')) return '🌫️';
    return '🌤️';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
    
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className="forecast-container">
      <h3 className="forecast-title">7-Day Forecast</h3>
      <div className="forecast-grid">
        {forecast.map((day, index) => (
          <div key={index} className="forecast-card">
            <div className="forecast-date">{formatDate(day.date)}</div>
            <div className="forecast-emoji">{getWeatherEmoji(day.summary)}</div>
            <div className="forecast-temps">
              <span className="temp-max">{day.temp_max ? `${Math.round(day.temp_max)}°` : 'N/A'}</span>
              <span className="temp-min">{day.temp_min ? `${Math.round(day.temp_min)}°` : 'N/A'}</span>
            </div>
            {day.precipitation_probability !== null && (
              <div className="forecast-precip">💧 {day.precipitation_probability}%</div>
            )}
            <div className="forecast-summary">{day.summary || 'Unknown'}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeatherForecast;
