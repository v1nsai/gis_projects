// Fairfax County Walkability Hotspots Map
// Loads hotspots.geojson and points_in_hotspots.geojson, displays on Leaflet map

const CATEGORY_CONFIG = {
  "Grocery": {
    color: "#2ecc71",
    icon: "shopping-cart",
    group: "grocery",
  },
  "Housing": {
    color: "#3498db",
    icon: "home",
    group: "housing",
  },
  "FFX Connector Bus Stop": {
    color: "#e74c3c",
    icon: "bus",
    group: "transit",
  },
  "WMATA Bus Stop": {
    color: "#e74c3c",
    icon: "bus",
    group: "transit",
  },
  "WMATA Train Station": {
    color: "#9b59b6",
    icon: "train",
    group: "transit",
  },
};

// Fairfax County approximate center
const MAP_CENTER = [38.84, -77.25];
const MAP_ZOOM = 11;

let map;
let hotspotLayer, groceryLayer, housingLayer, transitLayer;
let allMarkers = [];

function getCategoryConfig(category) {
  return CATEGORY_CONFIG[category] || { color: "#999", icon: "circle", group: "other" };
}

function createMarkerIcon(color) {
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: ${color};
      border: 2px solid white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    "></div>`,
    iconSize: [10, 10],
    iconAnchor: [5, 5],
  });
}

function formatPopupContent(properties, layerType) {
  let html = `<div class="popup-content">`;
  html += `<h3>${properties.name || properties.stop_name || "Feature"}</h3>`;
  html += `<div class="popup-category">${properties.category || layerType}</div>`;

  // Show relevant properties
  const skipFields = new Set(["geometry", "category"]);
  for (const [key, value] of Object.entries(properties)) {
    if (skipFields.has(key) || value === null || value === undefined || value === "") continue;
    const label = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    let displayValue = value;
    if (Array.isArray(value)) {
      displayValue = value.join(", ");
    }
    html += `<div class="popup-field"><span class="popup-label">${label}:</span> ${displayValue}</div>`;
  }

  html += `</div>`;
  return html;
}

function initMap() {
  map = L.map("map", {
    center: MAP_CENTER,
    zoom: MAP_ZOOM,
    zoomControl: true,
  });

  // Basemap - OSM tiles with CSS dark filter
  const osmLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    className: "dark-tiles",
  }).addTo(map);

  // Initialize layer groups
  hotspotLayer = L.featureGroup();
  groceryLayer = L.markerClusterGroup({ maxClusterRadius: 40 });
  housingLayer = L.markerClusterGroup({ maxClusterRadius: 40 });
  transitLayer = L.markerClusterGroup({ maxClusterRadius: 40 });

  loadData();
}

async function loadData() {
  try {
    const [hotspotsResp, pointsResp] = await Promise.all([
      fetch("hotspots.geojson"),
      fetch("points_in_hotspots.geojson"),
    ]);

    const hotspotsData = await hotspotsResp.json();
    const pointsData = await pointsResp.json();

    // Load hotspots
    L.geoJSON(hotspotsData, {
      style: {
        color: "#ffa500",
        weight: 2,
        fillColor: "#ffa500",
        fillOpacity: 0.15,
        opacity: 0.7,
      },
    }).eachLayer(layer => {
      layer.bindPopup(
        formatPopupContent(layer.feature.properties, "Hotspot"),
        { maxWidth: 300 }
      );
      hotspotLayer.addLayer(layer);
    });

    // Load points by category
    let groceryCount = 0, housingCount = 0, transitCount = 0;
    pointsData.features.forEach(feature => {
      const props = feature.properties;
      const coords = feature.geometry.coordinates;
      const config = getCategoryConfig(props.category);

      const marker = L.marker([coords[1], coords[0]], {
        icon: createMarkerIcon(config.color),
      });

      marker.bindPopup(formatPopupContent(props), { maxWidth: 300 });

      switch (config.group) {
        case "grocery":
          groceryLayer.addLayer(marker);
          groceryCount++;
          break;
        case "housing":
          housingLayer.addLayer(marker);
          housingCount++;
          break;
        case "transit":
          transitLayer.addLayer(marker);
          transitCount++;
          break;
      }

      allMarkers.push(marker);
    });

    // Add all layers to map
    hotspotLayer.addTo(map);
    groceryLayer.addTo(map);
    housingLayer.addTo(map);
    transitLayer.addTo(map);

    // Fit map to hotspots bounds
    if (hotspotLayer.getLayers().length > 0) {
      map.fitBounds(hotspotLayer.getBounds(), { padding: [20, 20] });
    }

    // Update stats
    document.getElementById("stats").innerHTML = `
      <p><strong>${hotspotsData.features.length}</strong> hotspot polygons</p>
      <p><strong>${groceryCount}</strong> grocery stores</p>
      <p><strong>${housingCount}</strong> housing units</p>
      <p><strong>${transitCount}</strong> transit stops</p>
    `;

    // Setup layer controls
    setupControls();
  } catch (err) {
    console.error("Failed to load data:", err);
    document.getElementById("stats").innerHTML = `<p style="color: red;">Error loading data</p>`;
  }
}

function setupControls() {
  document.getElementById("toggle-hotspots").addEventListener("change", e => {
    if (e.target.checked) map.addLayer(hotspotLayer);
    else map.removeLayer(hotspotLayer);
  });

  document.getElementById("toggle-grocery").addEventListener("change", e => {
    if (e.target.checked) map.addLayer(groceryLayer);
    else map.removeLayer(groceryLayer);
  });

  document.getElementById("toggle-housing").addEventListener("change", e => {
    if (e.target.checked) map.addLayer(housingLayer);
    else map.removeLayer(housingLayer);
  });

  document.getElementById("toggle-transit").addEventListener("change", e => {
    if (e.target.checked) map.addLayer(transitLayer);
    else map.removeLayer(transitLayer);
  });
}

document.addEventListener("DOMContentLoaded", initMap);
