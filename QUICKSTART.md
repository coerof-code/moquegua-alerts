# Moquegua Alert Monitoring System - Quick Start Guide

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
cd moquegua-alerts
pip install -r requirements.txt
```

### 2. Ejecutar Extracción Manual

```bash
python src/get_alerts.py
```

### 3. Generar Mapas

```bash
python src/generate_maps.py
```

### 4. Iniciar Dashboard

```bash
streamlit run app/streamlit_app.py
```

El dashboard se abrirá en: http://localhost:8501

### 5. Activar Monitoreo Automático (Opcional)

```bash
python src/scheduler.py
```

Esto ejecutará verificaciones automáticas a las 08:00, 14:00 y 20:00 (hora de Lima).

## ⚙️ Configuración

Edita `config.yaml` para personalizar:

- **Rutas de salida**: Dónde guardar CSV y mapas
- **Horarios**: Cuándo ejecutar verificaciones automáticas
- **Colores de mapas**: Personalizar visualización

## 📁 Estructura de Archivos

```
moquegua-alerts/
├── config.yaml          # Configuración
├── data/
│   ├── alerts.csv       # Alertas actuales
│   ├── alerts.db        # Base de datos histórica
│   └── maps/            # Mapas PNG generados
├── src/
│   ├── get_alerts.py    # Extracción de alertas
│   ├── generate_maps.py # Generación de mapas
│   ├── database.py      # Gestión de BD
│   └── scheduler.py     # Automatización
└── app/
    └── streamlit_app.py # Dashboard web
```

## 🌐 Deployment en Streamlit Cloud

1. Sube el proyecto a GitHub
2. Ve a https://streamlit.io/cloud
3. Conecta tu repositorio
4. ¡Listo! Tu dashboard estará en línea

## 📝 Notas

- El sistema verifica alertas 3 veces al día por defecto
- Los mapas se regeneran automáticamente cuando hay cambios
- El historial se guarda en SQLite (data/alerts.db)
- Los logs se guardan en logs/
