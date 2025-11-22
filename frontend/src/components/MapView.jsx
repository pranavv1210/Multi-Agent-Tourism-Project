
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
// Fix for default marker icon path with Vite/React
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

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
