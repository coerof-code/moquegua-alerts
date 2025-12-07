# Moquegua Alert Monitoring System

Sistema automatizado de monitoreo de alertas meteorológicas para Moquegua usando GitHub Actions y Streamlit Cloud.

## 🌟 Características

- ✅ **100% Gratuito** - GitHub Actions + Streamlit Cloud
- ✅ **100% Automatizado** - Actualizaciones 3x/día (08:00, 11:45, 17:00 hora Perú)
- ✅ **Sin Servidor** - Todo en la nube
- ✅ **Datos Precisos** - Usa geoidep R package oficial

## 🚀 Deployment Rápido

### 1. Fork este Repositorio

Haz click en "Fork" en GitHub para crear tu copia.

### 2. Habilitar GitHub Actions

1. Ve a tu repositorio fork
2. Click en "Actions"
3. Click "I understand my workflows, go ahead and enable them"

### 3. Deploy en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio fork
4. Main file path: `app/streamlit_app.py`
5. Click "Deploy"

¡Listo! Tu dashboard estará en línea en ~5 minutos.

## 📊 Cómo Funciona

```
GitHub Actions (3x/día)
    ↓
Ejecuta R script
    ↓
Genera data/alerts.csv
    ↓
Commit automático
    ↓
Streamlit Cloud detecta cambio
    ↓
Dashboard se actualiza
```

## 🕐 Horarios de Actualización

- **08:00 AM** (Perú UTC-5) = 13:00 UTC
- **11:45 AM** (Perú UTC-5) = 16:45 UTC
- **05:00 PM** (Perú UTC-5) = 22:00 UTC

## 📁 Estructura del Proyecto

```
moquegua-alerts/
├── .github/workflows/
│   └── update_alerts.yml      # GitHub Actions workflow
├── R_scripts/
│   └── get_moquegua_warnings.R # Script R de extracción
├── app/
│   └── streamlit_app.py       # Dashboard Streamlit
├── data/
│   └── alerts.csv             # Datos actualizados automáticamente
├── .streamlit/
│   └── config.toml            # Configuración Streamlit
└── requirements.txt           # Dependencias Python
```

## 🔧 Configuración Avanzada

### Cambiar Horarios de Actualización

Edita `.github/workflows/update_alerts.yml`:

```yaml
schedule:
  - cron: '0 13 * * *'  # 08:00 AM Perú
  - cron: '45 16 * * *' # 11:45 AM Perú
  - cron: '0 22 * * *'  # 05:00 PM Perú
```

### Ejecutar Manualmente

1. Ve a "Actions" en tu repositorio
2. Selecciona "Update Moquegua Alerts"
3. Click "Run workflow"

## 📝 Datos

Los datos provienen de:
- **SENAMHI** - Servicio Nacional de Meteorología e Hidrología del Perú
- **geoidep** - Paquete R para datos geoespaciales de Perú

## 🛠️ Tecnologías

- **R** - Extracción de datos (geoidep, sf, dplyr)
- **Python** - Dashboard (Streamlit, pandas, folium)
- **GitHub Actions** - Automatización
- **Streamlit Cloud** - Hosting

## 📄 Licencia

MIT License - Uso libre

## 👤 JPABDOINO

Sistema desarrollado para monitoreo de alertas meteorológicas en Moquegua, Perú.

---

**¿Problemas?** Abre un Issue en GitHub
**¿Mejoras?** Pull Requests son bienvenidos
