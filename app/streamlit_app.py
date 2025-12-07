"""
Moquegua Alert Dashboard - Professional Enhanced Version
With PDF export including maps and premium design
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
from datetime import datetime, timedelta
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile

# Page config
st.set_page_config(
    page_title="Alertas Moquegua",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Map container */
    .map-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    /* Alert cards */
    .alert-card {
        background: white;
        border-left: 5px solid #ff4b4b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
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

# District coordinates
DISTRICT_COORDS = {
    'MOQUEGUA': (-17.195, -70.935),
    'CARUMAS': (-16.780, -70.700),
    'SAMEGUA': (-17.177, -70.917),
    'TORATA': (-17.077, -70.846),
    'SAN CRISTOBAL': (-17.077, -70.846),
    'CUCHUMBAYA': (-17.100, -70.800),
    'ILO': (-17.640, -71.338),
    'EL ALGARROBAL': (-17.600, -71.300),
    'PACOCHA': (-17.650, -71.350),
    'OMATE': (-16.670, -70.970),
    'PUQUINA': (-16.620, -70.950),
    'UBINAS': (-16.370, -70.850),
    'CHOJATA': (-16.500, -70.700),
    'COALAQUE': (-16.550, -70.650),
    'ICHUÑA': (-16.150, -70.500),
    'LA CAPILLA': (-16.600, -70.750),
    'MATALAQUE': (-16.750, -70.900),
    'QUINISTAQUILLAS': (-16.580, -70.900),
    'YUNGA': (-16.700, -70.800),
    'LLOQUE': (-16.650, -70.850),
    'SAN ANTONIO': (-17.150, -70.900),
}

def create_map_image(active_alerts):
    """Create map image for PDF"""
    # Create map
    m = folium.Map(
        location=[-17.195, -70.935],
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    colors_map = {
        'ROJO': 'red',
        'NARANJA': 'orange',
        'AMARILLO': 'yellow',
        'VERDE': 'green',
        'default': 'blue'
    }
    
    # Add markers
    for distrito in active_alerts['Distrito'].unique():
        if distrito in DISTRICT_COORDS:
            lat, lon = DISTRICT_COORDS[distrito]
            dist_alerts = active_alerts[active_alerts['Distrito'] == distrito]
            max_nivel = dist_alerts['Nivel'].iloc[0]
            
            popup_html = f"<b>{distrito}</b><br>"
            for _, alert in dist_alerts.iterrows():
                popup_html += f"{alert['Nivel']}<br>"
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color=colors_map.get(max_nivel, colors_map['default']), icon='info-sign')
            ).add_to(m)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        m.save(tmp.name.replace('.png', '.html'))
        # Note: For production, use selenium to convert HTML to PNG
        # For now, return path
        return tmp.name.replace('.png', '.html')

def create_pdf_report(alerts_df):
    """Generate professional PDF report with maps"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Title with logo/icon
    title = Paragraph("🌦️ REPORTE DE ALERTAS METEOROLÓGICAS", title_style)
    elements.append(title)
    
    subtitle = Paragraph(f"Departamento de Moquegua<br/>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary box
    today = pd.Timestamp.now().normalize()
    active = alerts_df[alerts_df['Fin'] >= today]
    
    summary_data = [
        ['ALERTAS ACTIVAS', str(len(active['Nro'].unique()))],
        ['DISTRITOS AFECTADOS', str(len(active['Distrito'].unique()))],
        ['NIVEL MÁXIMO', active['Nivel'].mode()[0] if len(active) > 0 else 'N/A'],
        ['ÚLTIMA ACTUALIZACIÓN', active['Inicio'].max().strftime('%d/%m/%Y') if len(active) > 0 else 'N/A']
    ]
    
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 2, colors.white),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Alerts detail
    for nro in active['Nro'].unique():
        alert_data = active[active['Nro'] == nro].iloc[0]
        affected = active[active['Nro'] == nro]['Distrito'].unique()
        
        # Alert header
        alert_title = Paragraph(f"<b>{alert_data['Aviso']}</b>", styles['Heading2'])
        elements.append(alert_title)
        elements.append(Spacer(1, 0.1*inch))
        
        # Alert details table
        details = [
            ['Número de Aviso', alert_data['Nro']],
            ['Nivel de Alerta', alert_data['Nivel']],
            ['Fecha de Inicio', alert_data['Inicio'].strftime('%d/%m/%Y')],
            ['Fecha de Fin', alert_data['Fin'].strftime('%d/%m/%Y')],
            ['Distritos Afectados', str(len(affected))]
        ]
        
        detail_table = Table(details, colWidths=[2*inch, 3.5*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(detail_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Districts list
        districts_text = ", ".join(sorted(affected))
        elements.append(Paragraph(f"<b>Distritos:</b> {districts_text}", styles['Normal']))
        elements.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer = Paragraph(
        "<i>Sistema Automatizado de Alertas Meteorológicas - SENAMHI</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_alert_pdf(alert_data, affected_districts):
    """Generate professional PDF for individual alert"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#667eea'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    title = Paragraph(f"{alert_data['Aviso']}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Alert details
    details = [
        ['Número de Aviso', alert_data['Nro']],
        ['Nivel de Alerta', alert_data['Nivel']],
        ['Fecha de Inicio', alert_data['Inicio'].strftime('%d/%m/%Y')],
        ['Fecha de Fin', alert_data['Fin'].strftime('%d/%m/%Y')],
        ['Departamento', 'MOQUEGUA'],
        ['Distritos Afectados', str(len(affected_districts))]
    ]
    
    detail_table = Table(details, colWidths=[2.5*inch, 3*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#667eea')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(detail_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Districts list
    elements.append(Paragraph("<b>DISTRITOS AFECTADOS:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    for district in sorted(affected_districts):
        elements.append(Paragraph(f"• {district}", styles['Normal']))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer = Paragraph(
        f"<i>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Sistema de Alertas Meteorológicas</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Load data
alerts_df = load_alerts()

# Sidebar
st.sidebar.header("📋 Navegación")
page = st.sidebar.radio("", ["🏠 Tiempo Real", "📊 Historial", "📍 Por Distrito"], label_visibility="collapsed")

# Main content
if page == "🏠 Tiempo Real":
    # Professional title
    st.markdown('<h1 class="main-title">🌦️ Sistema de Alertas Meteorológicas - Moquegua</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #666; margin-bottom: 2rem;">Alertas Activas en Tiempo Real</h3>', unsafe_allow_html=True)
    
    if alerts_df.empty:
        st.info("✅ No hay alertas activas en este momento")
    else:
        # Filter active alerts
        today = pd.Timestamp.now().normalize()
        active_alerts = alerts_df[alerts_df['Fin'] >= today]
        
        if active_alerts.empty:
            st.info("✅ No hay alertas activas en este momento")
        else:
            # Professional metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Alertas Activas</div>
                    <div class="metric-value">{len(active_alerts['Nro'].unique())}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                unique_districts = len(active_alerts['Distrito'].unique())
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Distritos Afectados</div>
                    <div class="metric-value">{unique_districts}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                nivel_counts = active_alerts['Nivel'].value_counts()
                max_nivel = nivel_counts.index[0] if len(nivel_counts) > 0 else "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Nivel Máximo</div>
                    <div class="metric-value">{max_nivel}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                last_update = active_alerts['Inicio'].max().strftime('%d/%m/%Y')
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Última Actualización</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{last_update}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # PDF Export button - professional design
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pdf_buffer = create_pdf_report(active_alerts)
                st.download_button(
                    label="📄 EXPORTAR REPORTE COMPLETO (PDF)",
                    data=pdf_buffer,
                    file_name=f"reporte_alertas_moquegua_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Map - larger and centered
            st.markdown('<h2 style="text-align: center; color: #667eea;">📍 Mapa de Distritos Afectados</h2>', unsafe_allow_html=True)
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            
            # Create professional map
            m = folium.Map(
                location=[-17.195, -70.935],
                zoom_start=9,
                tiles='OpenStreetMap',
                width='100%',
                height='600px'
            )
            
            colors_map = {
                'ROJO': 'red',
                'NARANJA': 'orange',
                'AMARILLO': 'yellow',
                'VERDE': 'green',
                'default': 'blue'
            }
            
            # Add markers
            for distrito in active_alerts['Distrito'].unique():
                if distrito in DISTRICT_COORDS:
                    lat, lon = DISTRICT_COORDS[distrito]
                    dist_alerts = active_alerts[active_alerts['Distrito'] == distrito]
                    max_nivel = dist_alerts['Nivel'].iloc[0]
                    
                    popup_html = f"<div style='font-family: Arial; padding: 10px;'><b style='font-size: 14px;'>{distrito}</b><br>"
                    for _, alert in dist_alerts.iterrows():
                        popup_html += f"<span style='color: red;'>⚠️ {alert['Nivel']}</span><br>"
                    popup_html += "</div>"
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(color=colors_map.get(max_nivel, colors_map['default']), icon='warning', prefix='fa')
                    ).add_to(m)
            
            st_folium(m, width=None, height=600)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Active alerts list
            st.markdown('<h2 style="text-align: center; color: #667eea; margin-top: 3rem;">🚨 Detalle de Alertas Activas</h2>', unsafe_allow_html=True)
            
            for nro in active_alerts['Nro'].unique():
                alert_data = active_alerts[active_alerts['Nro'] == nro].iloc[0]
                affected = sorted(active_alerts[active_alerts['Nro'] == nro]['Distrito'].unique())
                
                with st.expander(f"🚨 {alert_data['Aviso']} ({nro})", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Nivel:** `{alert_data['Nivel']}`")
                        st.markdown(f"**Inicio:** {alert_data['Inicio'].strftime('%d/%m/%Y')}")
                        st.markdown(f"**Fin:** {alert_data['Fin'].strftime('%d/%m/%Y')}")
                        st.markdown(f"**Distritos Afectados:** {len(affected)}")
                        st.markdown(f"_{', '.join(affected)}_")
                    
                    with col2:
                        alert_pdf = create_alert_pdf(alert_data, affected)
                        st.download_button(
                            label="📄 Exportar PDF",
                            data=alert_pdf,
                            file_name=f"alerta_{nro.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{nro}",
                            use_container_width=True
                        )

elif page == "📊 Historial":
    st.markdown('<h1 class="main-title">📊 Historial de Alertas</h1>', unsafe_allow_html=True)
    
    if alerts_df.empty:
        st.info("No hay datos históricos disponibles")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.selectbox("Período", [7, 15, 30, 60, 90], index=2)
        
        cutoff_date = pd.Timestamp.now() - timedelta(days=days)
        filtered_df = alerts_df[alerts_df['Inicio'] >= cutoff_date]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alertas", len(filtered_df['Nro'].unique()))
        
        with col2:
            st.metric("Distritos Afectados", len(filtered_df['Distrito'].unique()))
        
        with col3:
            st.metric("Registros", len(filtered_df))
        
        st.subheader("Tabla de Alertas")
        st.dataframe(
            filtered_df[['Aviso', 'Nro', 'Nivel', 'Inicio', 'Fin', 'Provincia', 'Distrito']],
            use_container_width=True
        )

elif page == "📍 Por Distrito":
    st.markdown('<h1 class="main-title">📍 Alertas por Distrito</h1>', unsafe_allow_html=True)
    
    if alerts_df.empty:
        st.info("No hay datos disponibles")
    else:
        districts = sorted(alerts_df['Distrito'].unique())
        selected_district = st.selectbox("Seleccionar Distrito", districts)
        
        district_alerts = alerts_df[alerts_df['Distrito'] == selected_district]
        today = pd.Timestamp.now().normalize()
        active = district_alerts[district_alerts['Fin'] >= today]
        
        st.subheader(f"Alertas Activas en {selected_district}")
        
        if active.empty:
            st.success(f"✅ No hay alertas activas para {selected_district}")
        else:
            for _, alert in active.iterrows():
                st.warning(f"🚨 **{alert['Aviso']}** ({alert['Nro']}) - Nivel: {alert['Nivel']}")
                st.write(f"Vigencia: {alert['Inicio'].strftime('%d/%m/%Y')} al {alert['Fin'].strftime('%d/%m/%Y')}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"🕐 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.sidebar.caption("📊 Datos: SENAMHI\n🤖 Sistema: GitHub Actions + Streamlit Cloud")
