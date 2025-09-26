# Sistema Automatizado de Scrapers de Noticias

## 📅 Configuración del Crontab

El sistema está configurado para ejecutarse automáticamente **todos los días a las 7:15 AM**.

### Comando del Crontab:
```
15 7 * * * cd /Users/danielegrasso/Dropbox/trabajo/EL_PAIS/2025/revista_prensa_cursos && ./run_all_scrapers.sh
```

### Explicación del formato:
- `15` = Minuto (15)
- `7` = Hora (7 AM)
- `*` = Día del mes (cualquiera)
- `*` = Mes (cualquiera)
- `*` = Día de la semana (cualquiera)

## 🔄 Proceso Automatizado

### 1. Ejecución de Scrapers (7:15 AM)
El script `run_all_scrapers.sh` ejecuta secuencialmente:
- ✅ **El Mundo** - 5 noticias principales
- ✅ **ElDiario.es** - 5 noticias principales
- ✅ **ABC.es** - 5 noticias principales
- ✅ **La Vanguardia** - 4 noticias principales + 1 aleatoria
- ✅ **El Confidencial** - 4 noticias específicas + 1 aleatoria

### 2. Actualización Automática
Después de ejecutar todos los scrapers:
- ✅ **Actualiza index.html** con los datos más recientes
- ✅ **Genera logs** en `scraper_logs.txt`
- ✅ **Mantiene timestamps** actualizados

## 📁 Archivos del Sistema

### Scripts Principales:
- `run_all_scrapers.sh` - Script principal que ejecuta todos los scrapers
- `update_index.py` - Script que actualiza el index.html automáticamente
- `test_cron.sh` - Script de prueba para verificar la configuración

### Scrapers Individuales:
- `scrapers_y_results/elmundo_scraper.py`
- `scrapers_y_results/eldiario_scraper.py`
- `scrapers_y_results/abc_scraper.py`
- `scrapers_y_results/lavanguardia_scraper.py`
- `scrapers_y_results/elconfidencial_scraper.py`

### Archivos de Datos:
- `scrapers_y_results/*_top5.json` - Datos de cada medio
- `index.html` - Página web actualizada
- `scraper_logs.txt` - Logs de ejecución

## 📊 Logs y Monitoreo

### Archivo de Logs: `scraper_logs.txt`
Contiene:
- Timestamp de cada ejecución
- Estado de cada scraper (✓ exitoso / ✗ error)
- Tiempo de ejecución de cada proceso

### Ejemplo de Log:
```
[2025-09-25 23:23:35] === Iniciando ejecución de scrapers ===
[2025-09-25 23:23:35] Ejecutando scraper de El Mundo...
[2025-09-25 23:23:38] ✓ El Mundo completado exitosamente
[2025-09-25 23:23:38] Ejecutando scraper de ElDiario.es...
[2025-09-25 23:23:44] ✓ ElDiario.es completado exitosamente
...
[2025-09-25 23:23:54] ✓ index.html actualizado exitosamente
[2025-09-25 23:23:54] === Proceso completo finalizado ===
```

## 🛠️ Comandos Útiles

### Ver el Crontab Actual:
```bash
crontab -l
```

### Ejecutar Manualmente:
```bash
./run_all_scrapers.sh
```

### Ver Logs:
```bash
cat scraper_logs.txt
```

### Probar la Configuración:
```bash
./test_cron.sh
```

## ⚠️ Notas Importantes

1. **macOS y Cron**: En macOS, el servicio cron puede necesitar permisos especiales. Si no funciona automáticamente, puedes:
   - Ir a "Preferencias del Sistema" > "Seguridad y Privacidad" > "Privacidad" > "Automatización"
   - Permitir que Terminal ejecute tareas programadas

2. **Rutas Absolutas**: El crontab usa rutas absolutas para asegurar que funcione desde cualquier directorio.

3. **Logs**: Los logs se acumulan en `scraper_logs.txt`. Puedes limpiarlos periódicamente si crecen mucho.

4. **Noticias Aleatorias**: La Vanguardia y El Confidencial incluyen noticias aleatorias que cambian en cada ejecución.

## 🎯 Resultado Final

Cada mañana a las 7:15 AM, tendrás:
- ✅ **25 noticias actuales** (5 por medio)
- ✅ **Página web actualizada** automáticamente
- ✅ **Logs detallados** de la ejecución
- ✅ **Noticias frescas** del día
