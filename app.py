import streamlit as st
import geopandas as gpd
import plotly.express as px
import os
import pandas as pd

# ===========================================================================
# 1. PAGE CONFIGURATION & INITIALIZATION
# ===========================================================================
st.set_page_config(page_title="REC WebGIS Dashboard", layout="wide")
st.title("Renewable Energy Communities (RECs) Dashboard - Southern Italy")

# ===========================================================================
# 2. DATA ACQUISITION & PROCESSING MODULE
# ===========================================================================
@st.cache_data
def load_data():
    """
    Loads and processes the geospatial dataset containing REC Key Performance Indicators.
    Utilizes caching to optimize performance during interactive re-rendering.
    """
    # Dynamically construct the absolute file path to ensure execution stability
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "cabins_kpi.geojson")
    
    # Verify file existence to prevent runtime errors
    if not os.path.exists(file_path):
        st.error(f"System Error: Spatial data file not found at {file_path}")
        return None
        
    # Load the spatial data and project it to the standard web mapping CRS (WGS 84)
    gdf = gpd.read_file(file_path)
    gdf = gdf.to_crs(epsg=4326)
    
    # Coerce KPI attributes to numeric data types to ensure compatibility with Plotly
    # This specifically resolves potential "blank map" rendering issues
    cols_to_convert = ['ssi', 'sci', 'opi']
    for col in cols_to_convert:
        if col in gdf.columns:
            gdf[col] = pd.to_numeric(gdf[col], errors='coerce')
            
    return gdf

# ===========================================================================
# 3. MAIN APPLICATION LOGIC & VISUALIZATION
# ===========================================================================
st.write("Initializing spatial engine and loading geographical data...")
gdf = load_data()

if gdf is not None:
    st.success("Spatial dataset loaded and validated successfully.")

    # Establish a mapping dictionary to display professional uppercase acronyms in the UI
    # while utilizing the corresponding lowercase column names for dataframe queries.
    indicator_map = {
        "SSI (Self-Sufficiency Index)": "ssi",
        "SCI (Self-Consumption Index)": "sci",
        "OPI (Over-Production Index)": "opi"
    }

    # User Interface: Select Box for KPI filtering
    selected_display = st.selectbox(
        "Select the Key Performance Indicator (KPI) to visualize:", 
        list(indicator_map.keys())
    )
    
    # Retrieve the backend column name based on user selection
    indicator = indicator_map[selected_display]

    st.subheader(f"Choropleth Spatial Analysis: {selected_display}")

    # Index the GeoDataFrame by the Primary Substation identifier (cod_ac) for accurate geometric mapping
    if "cod_ac" in gdf.columns:
        gdf = gdf.set_index("cod_ac")

    # Generate the interactive Choropleth Mapbox using Plotly Express
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=indicator,
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 37.5, "lon": 14.0}, # Coordinates centered on Southern Italy
        opacity=0.7,
        labels={indicator: selected_display.split(" ")[0]} # Extracts just 'SSI', 'SCI', or 'OPI' for the legend
    )
    
    # Remove default margins to maximize map display area
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # Render the figure within the Streamlit interface
    st.plotly_chart(fig, use_container_width=True)