import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.express as px
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import openrouteservice

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="N-H Facilities Engine", page_icon="🏥", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .emergency-box {
        background-color: #FF4B4B;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .nav-btn {
        display: inline-block;
        background-color: #4285F4;
        color: white !important;
        padding: 8px 16px;
        text-align: center;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 5px;
    }
    .nav-btn:hover {
        background-color: #3367D6;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    # REMOVED 'func_stats' to match your specific CSV version
    cols = ['facility_name', 'facility_level', 'ownership', 'ward', 'lga', 'state', 'latitude', 'longitude']
    try:
        df = pd.read_csv("nigeria_health_facilities.csv", usecols=cols)
        df = df.dropna(subset=['latitude', 'longitude'])
        return df
    except Exception as e:
        st.error(f"❌ Data Error: {e}")
        return pd.DataFrame()

data = load_data()

# --- 3. HELPER FUNCTIONS ---

def get_coordinates(address):
    geolocator = Nominatim(user_agent="naija_health_mapper_fixed")
    try:
        location = geolocator.geocode(f"{address}, Nigeria")
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

def get_drive_time(start_coords, end_coords, api_key):
    try:
        client = openrouteservice.Client(key=api_key)
        routes = client.directions(
            coordinates=[start_coords, end_coords],
            profile='driving-car',
            format='geojson'
        )
        summary = routes['features'][0]['properties']['summary']
        duration_mins = summary['duration'] / 60
        distance_km = summary['distance'] / 1000
        return duration_mins, distance_km
    except:
        return None, None

# --- 4. MAIN APP UI ---

st.title("Nigerian Health Infrastructure Engine")

if not data.empty:
    tab1, tab2, tab3 = st.tabs(["Map Explorer", " Analytics Dashboard", " Emergency Finder"])

    # ==========================================
    # TAB 1: MAP EXPLORER
    # ==========================================
    with tab1:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Filters")
            states = sorted(data['state'].astype(str).unique())
            selected_state = st.selectbox("Select State", states)
            
            state_data = data[data['state'] == selected_state]
            
            lgas = sorted(state_data['lga'].astype(str).unique())
            selected_lga = st.multiselect("LGA (Optional)", lgas)
            
            levels = state_data['facility_level'].unique()
            selected_level = st.multiselect("Facility Level", levels)
            
            map_df = state_data.copy()
            if selected_lga: map_df = map_df[map_df['lga'].isin(selected_lga)]
            if selected_level: map_df = map_df[map_df['facility_level'].isin(selected_level)]

        with col2:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Facilities", len(map_df))
            if len(map_df) > 0:
                public_pct = (len(map_df[map_df['ownership']=='Public']) / len(map_df)) * 100
                m2.metric("Public Owned", f"{public_pct:.1f}%")
            m3.metric("Selected State", selected_state)
            
            if not map_df.empty:
                avg_lat = map_df['latitude'].mean()
                avg_lon = map_df['longitude'].mean()
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=9)
                marker_cluster = MarkerCluster().add_to(m)
                
                for _, row in map_df.iterrows():
                    color = "green" if row['ownership'] == "Public" else "red"
                    gmaps_link = f"https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}"
                    
                    popup_html = f"""
                    <div style="font-family:sans-serif; width:180px;">
                        <b>{row['facility_name']}</b><br>
                        <span style="color:grey;">{row['facility_level']}</span><br>
                        <a href="{gmaps_link}" target="_blank" 
                           style="background-color:#4285F4; color:white; padding:6px 10px; text-decoration:none; border-radius:4px; font-weight:bold;">
                           Navigate
                        </a>
                    </div>
                    """
                    
                    folium.Marker(
                        [row['latitude'], row['longitude']],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=row['facility_name'],
                        icon=folium.Icon(color=color, icon="plus", prefix="fa")
                    ).add_to(marker_cluster)
                
                st_folium(m, width="100%", height=500)
            else:
                st.warning("No facilities match filters.")

    # ==========================================
    # TAB 2: ANALYTICS
    # ==========================================
    with tab2:
        st.header(f"Healthcare Analytics: {selected_state}")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Ownership Structure")
            fig_pie = px.pie(state_data, names='ownership', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.subheader("Facility Levels")
            level_counts = state_data['facility_level'].value_counts().reset_index()
            level_counts.columns = ['Level', 'Count']
            fig_bar = px.bar(level_counts, x='Level', y='Count', color='Level')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.subheader("Density by LGA")
        lga_counts = state_data['lga'].value_counts().reset_index()
        lga_counts.columns = ['LGA', 'Facilities']
        fig_lga = px.bar(lga_counts, x='LGA', y='Facilities', color='Facilities')
        st.plotly_chart(fig_lga, use_container_width=True)

    # ==========================================
    # TAB 3: EMERGENCY FINDER
    # ==========================================
    with tab3:
        st.markdown('<div class="emergency-box"><h2> AI Emergency Finder</h2></div>', unsafe_allow_html=True)
        
        st.info("Enter OpenRouteService API Key for real traffic data (Optional).")
        user_api_key = st.text_input("API Key", type="password")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            user_loc = st.text_input("Enter your location", placeholder="e.g. Bodija Market, Ibadan")
            confirm_state = st.selectbox("Confirm State", states, key="emer_state")
            
        with c2:
            st.write("")
            st.write("")
            find_btn = st.button("🚑 Find Closest Help", type="primary")
            
        if find_btn and user_loc:
            with st.spinner("Triangulating location..."):
                u_lat, u_lon = get_coordinates(f"{user_loc}, {confirm_state}")
                
                if u_lat:
                    st.success(f"📍 Found: {u_lat:.4f}, {u_lon:.4f}")
                    
                    # REMOVED filtering by 'func_stats' since the column is missing
                    candidates = data[data['state'] == confirm_state].copy()
                    
                    if candidates.empty:
                        st.error("No facilities found in this state.")
                    else:
                        candidates['geo_dist'] = candidates.apply(
                            lambda row: geodesic((u_lat, u_lon), (row['latitude'], row['longitude'])).km, 
                            axis=1
                        )
                        
                        top_5 = candidates.sort_values('geo_dist').head(5)
                        
                        st.subheader("Top 5 Nearest Facilities")
                        
                        for _, row in top_5.iterrows():
                            drive_mins, drive_km = None, None
                            if user_api_key:
                                drive_mins, drive_km = get_drive_time(
                                    (u_lon, u_lat), 
                                    (row['longitude'], row['latitude']), 
                                    user_api_key
                                )
                            
                            with st.expander(f" {row['facility_name']} ({row['facility_level']})", expanded=True):
                                k1, k2, k3 = st.columns(3)
                                
                                if drive_mins:
                                    k1.metric("Est. Time", f"{drive_mins:.0f} mins")
                                    k2.metric("Drive Dist", f"{drive_km:.1f} km")
                                else:
                                    k1.metric("Straight Line", f"{row['geo_dist']:.2f} km")
                                    k2.caption("Traffic data disabled")
                                    
                                nav_link = f"https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}"
                                k3.markdown(f'<a href="{nav_link}" target="_blank" class="nav-btn">🚗 GO NOW</a>', unsafe_allow_html=True)
                else:
                    st.error("Address not found. Try adding a landmark.")

else:
    st.info("Loading Database...")