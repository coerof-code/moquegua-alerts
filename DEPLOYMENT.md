# Guía de Deployment - Sistema de Alertas Moquegua

## Paso 1: Preparar Repositorio GitHub

### 1.1 Crear Repositorio
```bash
# En GitHub, crear nuevo repositorio público
# Nombre sugerido: moquegua-alerts
```

### 1.2 Subir Código
```bash
cd d:/jp/GEOIDEP/moquegua-alerts

# Inicializar git (si no está)
git init

# Agregar archivos
git add .
git commit -m "Initial commit - Moquegua Alert System"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/moquegua-alerts.git
git branch -M main
git push -u origin main
```

## Paso 2: Configurar GitHub Actions

### 2.1 Habilitar Actions
1. Ve a tu repositorio en GitHub
2. Click en pestaña "Actions"
3. Click "I understand my workflows, go ahead and enable them"

### 2.2 Verificar Workflow
- El archivo `.github/workflows/update_alerts.yml` ya está incluido
- GitHub Actions ejecutará automáticamente 3x/día
- También puedes ejecutar manualmente desde la pestaña Actions

### 2.3 Primera Ejecución Manual
1. Ve a "Actions" → "Update Moquegua Alerts"
2. Click "Run workflow" → "Run workflow"
3. Espera ~5 minutos
4. Verifica que `data/alerts.csv` se actualizó

## Paso 3: Deploy en Streamlit Cloud

### 3.1 Crear Cuenta
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Sign in con GitHub

### 3.2 Crear Nueva App
1. Click "New app"
2. Selecciona tu repositorio: `TU_USUARIO/moquegua-alerts`
3. Branch: `main`
4. Main file path: `app/streamlit_app.py`
5. Click "Deploy"

### 3.3 Configuración Avanzada (Opcional)
- App URL: Personaliza la URL de tu app
- Python version: 3.11 (recomendado)
- Secrets: No necesarios para este proyecto

## Paso 4: Verificar Funcionamiento

### 4.1 Dashboard
- Abre la URL de tu app Streamlit
- Verifica que muestra las alertas
- Prueba las 3 páginas (Tiempo Real, Historial, Por Distrito)

### 4.2 Actualizaciones Automáticas
- Espera a la siguiente ejecución programada (08:00, 11:45, o 17:00 hora Perú)
- O ejecuta manualmente desde GitHub Actions
- El dashboard se actualizará automáticamente en ~1 minuto

## Paso 5: Mantenimiento

### Actualizar Horarios
Edita `.github/workflows/update_alerts.yml`:
```yaml
schedule:
  - cron: '0 13 * * *'  # Cambia estos valores
```

### Ver Logs
- GitHub Actions → Selecciona una ejecución → Ver logs
- Streamlit Cloud → App settings → Logs

### Troubleshooting

**GitHub Actions falla:**
- Verifica logs en Actions
- Común: Instalación de geoidep (puede tardar)

**Dashboard no actualiza:**
- Verifica que `data/alerts.csv` existe en GitHub
- Streamlit Cloud tarda ~1 min en detectar cambios

**No hay datos:**
- Normal si no hay alertas activas
- El CSV estará vacío pero el dashboard funcionará

## Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [geoidep Package](https://github.com/healthinnovation/geoidep)

## Costos

- GitHub Actions: 2000 minutos/mes gratis (suficiente para 3x/día)
- Streamlit Cloud: 1 app pública gratis
- **Total: $0/mes** 🎉
