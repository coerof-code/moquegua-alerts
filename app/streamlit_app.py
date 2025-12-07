"""
Moquegua Alert Dashboard - Streamlit Cloud Version
Simplified version that reads directly from CSV (no database)
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Alertas Moquegua",
    page_icon="🌦️",
    layout="wide"
)

# Title
st.title("🌦️ Sistema de Alertas Meteorológicas - Moquegua")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_alerts():
    """Load alerts from CSV"""
    csv_path = Path(__file__).parent.parent / "data" / "alerts.csv"
    
    if not csv_path.exists():
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        if len(df) > 0:
            df['Inicio'] = pd.to_datetime(df['Inicio'])
            df['Fin'] = pd.to_datetime(df['Fin'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# District coordinates (simplified)
DISTRICT_COORDS = {
    'MOQUEGUA': (-17.195, -70.935),
    'CARUMAS': (-16.780, -70.700),
    'SAMEGUA': (-17.177, -70.917),
    'TORATA': (-17.077, -70.846),
    'ILO': (-17.640, -71.338),
    'EL ALGARROBAL': (-17.600, -71.300),
    'PACOCHA': (-17.650, -71.350),
    'OMATE': (-16.670, -70.970),
    'PUQUINA': (-16.620, -70.950),
    'UBINAS': (-16.370, -70.850),
}

# Load data
alerts_df = load_alerts()

# Sidebar
st.sidebar.header("Navegación")
page = st.sidebar.radio("Seleccionar página:", ["🏠 Tiempo Real", "📊 Historial", "📍 Por Distrito"])

# Main content
if page == "🏠 Tiempo Real":
    st.header("Alertas Activas en Tiempo Real")
    
    if alerts_df.empty:
        st.info("✅ No hay alertas activas en este momento")
    else:
        # Filter active alerts
        today = pd.Timestamp.now().normalize()
        active_alerts = alerts_df[alerts_df['Fin'] >= today]
        
        if active_alerts.empty:
            st.info("✅ No hay alertas activas en este momento")
        else:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Alertas Activas", len(active_alerts['Nro'].unique()))
            
            with col2:
                st.metric("Distritos Afectados", len(active_alerts['Distrito'].unique()))
            
            with col3:
                nivel_counts = active_alerts['Nivel'].value_counts()
                max_nivel = nivel_counts.index[0] if len(nivel_counts) > 0 else "N/A"
                st.metric("Nivel Máximo", max_nivel)
            
            with col4:
                last_update = active_alerts['Inicio'].max().strftime('%Y-%m-%d')
                st.metric("Última Actualización", last_update)
            
            # Map
            st.subheader("Mapa de Distritos Afectados")
            
            # Create map centered on Moquegua
            m = folium.Map(location=[-17.195, -70.935], zoom_start=9)
            
            # Color mapping
            colors = {
                'ROJO': 'red',
                'NARANJA': 'orange',
                'AMARILLO': 'yellow',
                'VERDE': 'green',
                'default': 'blue'
            }
            
            # Add markers for affected districts
            for distrito in active_alerts['Distrito'].unique():
                if distrito in DISTRICT_COORDS:
                    lat, lon = DISTRICT_COORDS[distrito]
                    
                    # Get alerts for this district
                    dist_alerts = active_alerts[active_alerts['Distrito'] == distrito]
                    max_nivel = dist_alerts['Nivel'].iloc[0]
                    
                    # Create popup
                    popup_html = f"<b>{distrito}</b><br>"
                    for _, alert in dist_alerts.iterrows():
                        popup_html += f"{alert['Aviso']}<br>Nivel: {alert['Nivel']}<br>"
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(color=colors.get(max_nivel, colors['default']), icon='info-sign')
                    ).add_to(m)
            
            st_folium(m, width=700, height=500)
            
            # Active alerts list
            st.subheader("Detalle de Alertas Activas")
            
            for nro in active_alerts['Nro'].unique():
                alert_data = active_alerts[active_alerts['Nro'] == nro].iloc[0]
                
                with st.expander(f"🚨 {alert_data['Aviso']} ({nro})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nivel:** {alert_data['Nivel']}")
                        st.write(f"**Inicio:** {alert_data['Inicio'].strftime('%Y-%m-%d')}")
                        st.write(f"**Fin:** {alert_data['Fin'].strftime('%Y-%m-%d')}")
                    
                    with col2:
                        affected = active_alerts[active_alerts['Nro'] == nro]['Distrito'].unique()
                        st.write(f"**Distritos Afectados:** {len(affected)}")
                        st.write(", ".join(affected))

elif page == "📊 Historial":
    st.header("Historial de Alertas")
    
    if alerts_df.empty:
        st.info("No hay datos históricos disponibles")
    else:
        # Date filter
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.selectbox("Período", [7, 15, 30, 60, 90], index=2)
        
        # Filter by date
        cutoff_date = pd.Timestamp.now() - timedelta(days=days)
        filtered_df = alerts_df[alerts_df['Inicio'] >= cutoff_date]
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alertas", len(filtered_df['Nro'].unique()))
        
        with col2:
            st.metric("Distritos Afectados", len(filtered_df['Distrito'].unique()))
        
        with col3:
            st.metric("Registros", len(filtered_df))
        
        # Data table
        st.subheader("Tabla de Alertas")
        st.dataframe(
            filtered_df[['Aviso', 'Nro', 'Nivel', 'Inicio', 'Fin', 'Provincia', 'Distrito']],
            use_container_width=True
        )

elif page == "📍 Por Distrito":
    st.header("Alertas por Distrito")
    
    if alerts_df.empty:
        st.info("No hay datos disponibles")
    else:
        # District selector
        districts = sorted(alerts_df['Distrito'].unique())
        selected_district = st.selectbox("Seleccionar Distrito", districts)
        
        # Filter by district
        district_alerts = alerts_df[alerts_df['Distrito'] == selected_district]
        
        # Filter active
        today = pd.Timestamp.now().normalize()
        active = district_alerts[district_alerts['Fin'] >= today]
        
        st.subheader(f"Alertas Activas en {selected_district}")
        
        if active.empty:
            st.success(f"✅ No hay alertas activas para {selected_district}")
        else:
            for _, alert in active.iterrows():
                st.warning(f"🚨 **{alert['Aviso']}** ({alert['Nro']}) - Nivel: {alert['Nivel']}")
                st.write(f"Vigencia: {alert['Inicio'].strftime('%Y-%m-%d')} al {alert['Fin'].strftime('%Y-%m-%d')}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.caption("Datos: SENAMHI | Sistema: GitHub Actions + Streamlit Cloud")
