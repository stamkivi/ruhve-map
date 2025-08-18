# Ruhve Village Map Web App

A professional web-based map application for Ruhve village on Saaremaa, Estonia.

## Features

- **Interactive Map**: Built with MapLibre GL JS
- **Cadastral Parcels**: Shows all land parcels with farm names
- **Building Locations**: Displays building footprints in red
- **Road Network**: Shows roads with names (toggleable)
- **Village Boundary**: Prominent red dashed border around the village
- **Sea Highlighting**: Subtle blue water background for coastal context
- **T. Family Plots**: Special highlighting for specific family properties (7.06% of village lands)
- **High-Resolution Export**: Generate printable maps at 300 DPI for professional use

## Controls

- **🏠 Tõsta esile hoonetega krundid**: Highlight parcels with buildings
- **🏷️ Näita sildid**: Show/hide farm name labels
- **🛣️ Näita teid**: Show/hide road lines
- **🏷️ Näita tee nimesid**: Show/hide road names
- **🏠 Näita hooneid**: Show/hide building footprints
- **🏘️ Näita küla piiri**: Show/hide village boundary
- **🏘️ T. maad (7.06%)**: Highlight T. family properties with detailed info
- **🖨️ Ekspordi kaart**: Export high-resolution map for printing

## Data Sources

- **Parcels**: `output/parcels_wgs84_proper.geojson` (WGS84 coordinates)
- **Buildings**: `output/buildings_wgs84_proper.geojson` (WGS84 coordinates)
- **Roads**: `output/roads.geojson` (WGS84 coordinates)

## How to Run

1. Start a web server from the project root:
   ```bash
   python3 -m http.server 8000
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/web/
   ```

## Technical Details

- **Coordinate System**: Transformed from EPSG:3301 (Estonian) to WGS84 using pyproj
- **Map Library**: MapLibre GL JS v5.6.2
- **Base Map**: CartoDB Positron style
- **Responsive Design**: Works on desktop and mobile devices

## File Structure

```
web/
├── index.html          # Main application (this file)
├── maplibre-gl.js      # MapLibre GL JS library
├── maplibre-gl.css     # MapLibre GL JS styles
├── maplibre-gl.js.map  # Source maps for debugging
└── favicon.ico         # Browser favicon
```

## Browser Compatibility

- Modern browsers with WebGL support
- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Mobile)
