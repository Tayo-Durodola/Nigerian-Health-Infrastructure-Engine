# NaijaHealth-Mapper: Emergency Resource Locator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]([https://your-app-link.streamlit.app](https://nigerian-health-infrastructure-engine.streamlit.app/))

## Project Context
In medical emergencies in Nigeria, the biggest bottleneck is often information asymmetry. Patients do not know which nearest hospital is functional, publicly owned, or has the right capacity. NaijaHealth-Mapper solves this using the GRID3 (Geo-Referenced Infrastructure and Demographic Data for Development) dataset.

## Key Features
* **Geospatial Intelligence:** visualizes 40,000+ health facilities across all 36 states + FCT.
* **Smart Filtering:** Drill down by LGA, Ownership (Private/Public), and Functional Status.
* **Emergency Routing:** Uses **OpenRouteService** to calculate *actual* driving time (accounting for traffic/road network) rather than just straight-line distance.
* **Direct Navigation:** One-click integration with Google Maps for turn-by-turn directions.

## Tech Stack
* **Python & Streamlit** (Frontend)
* **Folium & Leaflet.js** (Interactive Mapping)
* **OpenRouteService API** (Isochrones & Routing)
* **GeoPy** (Geocoding addresses)
* **Pandas** (Data Engineering)

## How to Run Locally
1.  Clone the repo.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the app: `streamlit run app.py`
