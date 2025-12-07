"""
Alert Extraction Script for Moquegua
Pure Python implementation - no R dependency
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import geopandas as gpd
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from src.database import AlertDatabase
from src.geoidep_python import (
    senamhi_get_meteorological_table,
    senamhi_get_spatial_alerts,
    get_districts,
    get_provinces
)


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_moquegua_alerts(config):
    """
    Extract active alerts for Moquegua region
    Returns: DataFrame with alerts and affected districts
    """
    print("🔍 Fetching meteorological alerts from SENAMHI...")
    
    # Get alerts table
    alerts_table = senamhi_get_meteorological_table()
    
    # Filter for active alerts (end date >= today)
    print("📅 Filtering active alerts...")
    alerts_table['fin_date'] = pd.to_datetime(alerts_table['fin'])
    today = pd.Timestamp.now().normalize()
    active_alerts = alerts_table[alerts_table['fin_date'] >= today].copy()
    
    print(f"✅ Found {len(active_alerts)} active alerts")
    
    if len(active_alerts) == 0:
        print("ℹ️  No active alerts found")
        return pd.DataFrame()
    
    # Get Moquegua districts
    print("🗺️  Loading Moquegua district boundaries...")
    all_districts = get_districts(show_progress=False)
    moquegua_dists = all_districts[all_districts['ubigeo'].str.startswith('18')].copy()
    
    # Get provinces for mapping
    print("🗺️  Loading province data...")
    all_provs = get_provinces(show_progress=False)
    all_provs['prov_code'] = all_provs['ccdd'] + all_provs['ccpp']
    
    prov_map = all_provs[['prov_code', 'nombprov']].drop_duplicates()
    
    # Add province names to districts
    moquegua_dists['prov_code'] = moquegua_dists['ubigeo'].str[:4]
    moquegua_dists = moquegua_dists.merge(prov_map, on='prov_code', how='left')
    
    # Ensure valid geometries
    moquegua_dists['geometry'] = moquegua_dists['geometry'].make_valid()
    
    print(f"📍 Loaded {len(moquegua_dists)} Moquegua districts")
    
    # Process each alert
    detailed_warnings = []
    
    print(f"\n🔄 Processing {len(active_alerts)} alerts for spatial intersection...")
    
    for idx, alert in active_alerts.iterrows():
        print(f"  Processing alert {idx + 1}/{len(active_alerts)}: {alert['nro']}")
        
        try:
            # Get spatial data for alert
            alert_geom = senamhi_get_spatial_alerts(alert, show_progress=False)
            
            if alert_geom is None or len(alert_geom) == 0:
                print(f"    ⚠️  No geometry found for alert {alert['nro']}")
                continue
            
            # Ensure valid geometry
            alert_geom['geometry'] = alert_geom['geometry'].make_valid()
            
            # Filter out "Nivel 1" background geometry - EXACT logic from R
            if 'nivel' in alert_geom.columns:
                alert_geom = alert_geom[alert_geom['nivel'] != 'Nivel 1']
                
                if len(alert_geom) == 0:
                    print(f"    ℹ️  Only Nivel 1 geometry found (skipping)")
                    continue
            
            # Find intersecting districts - EXACT logic from R (st_intersects)
            intersections = gpd.sjoin(
                moquegua_dists, 
                alert_geom, 
                how='inner', 
                predicate='intersects'
            )
            
            if len(intersections) == 0:
                print(f"    ℹ️  No intersections with Moquegua")
                continue
            
            print(f"    ✅ Found {len(intersections)} affected districts")
            
            # Create detailed records
            for _, dist in intersections.iterrows():
                detailed_warnings.append({
                    'Aviso': alert['aviso'],
                    'Nro': alert['nro'],
                    'Nivel': alert['nivel'],
                    'Inicio': alert['inicio'],
                    'Fin': alert['fin'],
                    'Departamento': 'MOQUEGUA',
                    'Provincia': dist['nombprov'],
                    'Distrito': dist['nombdist']
                })

        
        except Exception as e:
            print(f"    ❌ Error processing alert {alert['nro']}: {str(e)}")
            continue
    
    if not detailed_warnings:
        print("\n⚠️  No alerts affecting Moquegua found")
        return pd.DataFrame()
    
    # Create DataFrame
    warnings_df = pd.DataFrame(detailed_warnings)
    warnings_df = warnings_df.drop_duplicates()
    
    print(f"\n✅ Total affected district records: {len(warnings_df)}")
    
    return warnings_df


def save_to_database(warnings_df, config):
    """Save alerts to database"""
    if warnings_df.empty:
        return
    
    print("\n💾 Saving to database...")
    db = AlertDatabase(config['paths']['database'])
    
    # Get unique alerts
    unique_alerts = warnings_df[['Aviso', 'Nro', 'Nivel', 'Inicio', 'Fin']].drop_duplicates()
    
    for _, alert in unique_alerts.iterrows():
        # Determine status
        fin_date = pd.to_datetime(alert['Fin'])
        status = 'active' if fin_date >= pd.Timestamp.now().normalize() else 'expired'
        
        # Add alert
        alert_data = {
            'aviso': alert['Aviso'],
            'nro': alert['Nro'],
            'nivel': alert['Nivel'],
            'inicio': alert['Inicio'],
            'fin': alert['Fin'],
            'status': status
        }
        alert_id = db.add_alert(alert_data)
        
        # Add affected districts
        districts = warnings_df[warnings_df['Nro'] == alert['Nro']][
            ['Distrito', 'Provincia', 'Departamento']
        ].to_dict('records')
        
        districts_data = [
            {
                'distrito': d['Distrito'],
                'provincia': d['Provincia'],
                'departamento': d['Departamento']
            }
            for d in districts
        ]
        
        db.add_affected_districts(alert_id, districts_data)
    
    print("✅ Database updated")


def main():
    """Main execution function"""
    print("=" * 60)
    print("🌦️  MOQUEGUA ALERT EXTRACTION SYSTEM (Pure Python)")
    print("=" * 60)
    print(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load configuration
    config = load_config()
    
    # Get alerts
    warnings_df = get_moquegua_alerts(config)
    
    if warnings_df.empty:
        print("\n✅ No active alerts affecting Moquegua at this time")
        return
    
    # Save to CSV
    csv_path = Path(config['paths']['output_csv'])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    warnings_df.to_csv(csv_path, index=False)
    print(f"\n💾 Saved to: {csv_path}")
    
    # Save to database
    save_to_database(warnings_df, config)
    
    print("\n" + "=" * 60)
    print("✅ EXTRACTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
