import pandas as pd

# Load data
df = pd.read_csv('data/alerts.csv')

# Filter active alerts
today = pd.Timestamp.now().normalize()
df['Fin'] = pd.to_datetime(df['Fin'])
active = df[df['Fin'] >= today]

print(f"Total registros en CSV: {len(df)}")
print(f"Alertas únicas: {df['Nro'].nunique()}")
print(f"Distritos únicos en TODAS las alertas: {df['Distrito'].nunique()}")
print(f"\nAlertas ACTIVAS: {len(active)}")
print(f"Distritos únicos en alertas ACTIVAS: {active['Distrito'].nunique()}")
print(f"\nLista de distritos activos:")
for d in sorted(active['Distrito'].unique()):
    print(f"  - {d}")
