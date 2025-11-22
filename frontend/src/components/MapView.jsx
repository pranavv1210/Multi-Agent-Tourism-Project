import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

const MapView = ({ data }) => {
  const mapRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!data || !data.lat || !data.lon || !containerRef.current) return;

    const center = [data.lat, data.lon];

    if (!mapRef.current) {
      // Initialize map with settings that reduce scroll jitter
      mapRef.current = L.map(containerRef.current, {
        zoomControl: true,
        scrollWheelZoom: true,
        preferCanvas: true,
        inertia: false,
      }).setView(center, 12);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(mapRef.current);
    } else {
      mapRef.current.setView(center);
    }

    // Remove existing markers (keep tile layer)
    mapRef.current.eachLayer(layer => {
      if (layer instanceof L.Marker) {
        mapRef.current.removeLayer(layer);
      }
    });

    // Add place marker
    L.marker(center).addTo(mapRef.current).bindPopup(data.place || 'Location');

    if (Array.isArray(data.places_geo)) {
      data.places_geo.forEach(p => {
        if (p.lat != null && p.lon != null) {
          L.marker([p.lat, p.lon]).addTo(mapRef.current).bindPopup(p.name);
        }
      });
    }
  }, [data]);

  return (
    <div className="map-wrapper">
      <h3 className="map-title">Map</h3>
      <div ref={containerRef} className="map-container" />
    </div>
  );
};

export default MapView;
