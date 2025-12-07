# Moquegua Alert Monitoring System - Sistema Híbrido R+Python

## 🎯 Estado Actual

✅ **Dashboard Streamlit funcionando** en http://localhost:8501
✅ **Visualización de datos** operativa
✅ **Base de datos SQLite** implementada
⚠️ **Extracción de datos** usando scripts R existentes

## 🔄 Flujo de Trabajo Actual

### Opción 1: Usar Scripts R (Recomendado - Ya funciona)

```bash
# 1. Generar datos con R
cd d:/jp/GEOIDEP
Rscript get_moquegua_warnings.R
Rscript generate_alert_maps.R

# 2. Copiar datos al proyecto Python
copy moquegua_warnings_detailed.csv moquegua-alerts/data/alerts.csv
copy mapa_aviso_*.png moquegua-alerts/data/maps/

# 3. El dashboard se actualiza automáticamente
```

### Opción 2: Usar Puente R-Python (Automatizado)

```bash
cd moquegua-alerts
.\venv\Scripts\python.exe src/run_r_bridge.py
```

**Nota**: Requiere que R esté en el PATH del sistema.

## 📊 Dashboard Features

- **🏠 Vista en Tiempo Real**: Mapa interactivo + métricas en vivo
- **📊 Historial**: Tabla completa de alertas (activas/finalizadas)
- **📍 Por Distrito**: Análisis individual por distrito

## ⚙️ Configuración

Edita `config.yaml` para personalizar:
- Rutas de salida
- Horarios de verificación (actualmente: 08:00, 11:45, 17:00)
- Colores de mapas

## 🔧 Próximos Pasos (Opcional)

### Para implementación Python pura:

1. **Completar implementación de web scraping SENAMHI**
   - Usar BeautifulSoup4 para parsear HTML
   - Descargar y procesar shapefiles

2. **Agregar al requirements.txt**:
   ```
   beautifulsoup4>=4.12.0
   lxml>=4.9.0
   ```

3. **Actualizar `src/geoidep_python.py`** con scraping completo

## 🚀 Deployment

### Streamlit Cloud (Gratis)

1. Sube el proyecto a GitHub
2. Conecta en https://streamlit.io/cloud
3. Configura para ejecutar `app/streamlit_app.py`

**Limitación**: Streamlit Cloud no puede ejecutar R scripts. Necesitarás:
- Implementar Python puro, O
- Usar servidor propio con R instalado

## 📝 Notas Técnicas

- **geoidep**: Es un paquete R, no existe versión Python oficial
- **SENAMHI API**: Requiere web scraping (no hay API REST pública)
- **Datos geoespaciales**: INEI proporciona GeoJSON de distritos/provincias

## 🆘 Troubleshooting

**Dashboard no muestra datos:**
```bash
# Ejecuta manualmente los scripts R
cd d:/jp/GEOIDEP
Rscript get_moquegua_warnings.R
```

**Error "geoidep not found":**
- Es normal - el dashboard usa datos pre-generados por R
- Ejecuta los scripts R para actualizar datos

**Scheduler no funciona:**
- Requiere que el script Python pueda llamar a R
- Alternativa: Usar Task Scheduler de Windows para ejecutar scripts R
