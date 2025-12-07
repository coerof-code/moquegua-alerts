"""
Script to download and save Moquegua district geometries
"""
import geopandas as gpd
import requests
import json

# INEI GeoJSON URL for districts
url = "https://raw.githubusercontent.com/CONCYTEC/ubigeo-peru/master/geojson/distritos.geojson"

print("Downloading district geometries from INEI...")
response = requests.get(url)
geojson_data = response.json()

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])

# Filter for Moquegua (department code 18)
moquegua_gdf = gdf[gdf['IDDPTO'] == '18'].copy()

print(f"Found {len(moquegua_gdf)} districts in Moquegua")
print(moquegua_gdf[['NOMBDIST', 'IDDIST']].to_string())

# Save to file
output_file = 'data/moquegua_districts.geojson'
moquegua_gdf.to_file(output_file, driver='GeoJSON')
print(f"\nSaved to {output_file}")
