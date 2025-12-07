"""
Map Generation Script for Moquegua Alerts
Migrated from generate_alert_maps.R to Python
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import yaml

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.geoidep_python import get_districts



def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_alert_maps(config):
    """Generate maps for each active alert"""
    
    # Read alerts CSV
    csv_path = Path(config['paths']['output_csv'])
    if not csv_path.exists():
        print("❌ No alerts CSV found. Run get_alerts.py first.")
        return
    
    warnings_df = pd.read_csv(csv_path)
    
    if warnings_df.empty:
        print("ℹ️  No alerts to visualize")
        return
    
    print(f"📊 Generating maps for {len(warnings_df['Nro'].unique())} alerts...")
    
    # Load Moquegua districts
    print("🗺️  Loading district boundaries...")
    all_districts = get_districts(show_progress=False)
    moquegua_dists = all_districts[all_districts['ubigeo'].str.startswith('18')].copy()
    moquegua_dists['geometry'] = moquegua_dists['geometry'].make_valid()
    
    # Get unique alerts
    unique_alerts = warnings_df[['Aviso', 'Nro', 'Nivel', 'Inicio', 'Fin']].drop_duplicates()
    
    # Create output directory
    maps_dir = Path(config['paths']['output_maps'])
    maps_dir.mkdir(parents=True, exist_ok=True)
    
    # Map settings
    map_settings = config['map_settings']
    colors = map_settings['colors']
    
    # Generate map for each alert
    for idx, alert in unique_alerts.iterrows():
        print(f"\n  📍 Generating map for alert {alert['Nro']}...")
        
        # Get affected districts
        affected = warnings_df[warnings_df['Nro'] == alert['Nro']]['Distrito'].tolist()
        
        # Mark affected districts
        moquegua_dists['affected'] = moquegua_dists['nombdist'].isin(affected)
        
        # Get alert color
        alert_color = colors.get(alert['Nivel'], colors['default'])
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(map_settings['width'], map_settings['height']))
        
        # Plot districts
        moquegua_dists.plot(
            ax=ax,
            color=moquegua_dists['affected'].map({
                True: alert_color,
                False: map_settings['unaffected_color']
            }),
            edgecolor='white',
            linewidth=0.5
        )
        
        # Add district labels
        for idx, row in moquegua_dists.iterrows():
            centroid = row.geometry.centroid
            label_color = 'white' if row['affected'] else 'black'
            
            ax.text(
                centroid.x, centroid.y,
                row['nombdist'],
                fontsize=8,
                ha='center',
                va='center',
                fontweight='bold',
                color=label_color
            )
        
        # Format dates
        fecha_inicio = pd.to_datetime(alert['Inicio']).strftime('%d/%m/%Y')
        fecha_fin = pd.to_datetime(alert['Fin']).strftime('%d/%m/%Y')
        
        # Add title and labels
        ax.set_title(
            f"AVISO {alert['Nro']} - {alert['Nivel']}",
            fontsize=18,
            fontweight='bold',
            pad=20
        )
        
        subtitle = f"{alert['Aviso']}\nVigencia: {fecha_inicio} al {fecha_fin}"
        ax.text(
            0.5, 0.98,
            subtitle,
            transform=ax.transAxes,
            fontsize=12,
            ha='center',
            va='top'
        )
        
        caption = f"Distritos afectados: {len(affected)} de 21\nRegión: Moquegua | Fuente: SENAMHI"
        ax.text(
            0.5, 0.02,
            caption,
            transform=ax.transAxes,
            fontsize=9,
            ha='center',
            va='bottom',
            color='gray'
        )
        
        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor=alert_color, edgecolor='white', label='Afectado'),
            mpatches.Patch(facecolor=map_settings['unaffected_color'], edgecolor='white', label='No afectado')
        ]
        ax.legend(
            handles=legend_elements,
            loc='lower right',
            fontsize=11,
            frameon=True,
            fancybox=True
        )
        
        # Remove axes
        ax.set_axis_off()
        
        # Set background
        fig.patch.set_facecolor('white')
        ax.set_facecolor(map_settings['background_color'])
        
        # Save map
        nro_clean = ''.join(filter(str.isdigit, alert['Nro']))
        filename = maps_dir / f"mapa_aviso_{nro_clean}.png"
        
        plt.tight_layout()
        plt.savefig(
            filename,
            dpi=map_settings['dpi'],
            bbox_inches='tight',
            facecolor='white'
        )
        plt.close()
        
        print(f"    ✅ Saved: {filename}")
    
    print(f"\n✅ All maps generated successfully in: {maps_dir}")


def main():
    """Main execution"""
    print("=" * 60)
    print("🗺️  MOQUEGUA ALERT MAP GENERATION")
    print("=" * 60)
    print(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    config = load_config()
    generate_alert_maps(config)
    
    print("\n" + "=" * 60)
    print("✅ MAP GENERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
