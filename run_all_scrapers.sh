#!/bin/bash

# Script para ejecutar todos los scrapers de noticias
# Se ejecuta automáticamente todos los días a las 7:15 AM

# Obtener el directorio del script (funciona tanto local como en GitHub Actions)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SCRAPERS_DIR="$PROJECT_DIR/scrapers_y_results"

# Cambiar al directorio de scrapers
cd "$SCRAPERS_DIR"

# Función para registrar logs
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$PROJECT_DIR/scraper_logs.txt"
}

log_message "=== Iniciando ejecución de scrapers ==="

# Ejecutar El Mundo
log_message "Ejecutando scraper de El Mundo..."
python3 elmundo_scraper.py
if [ $? -eq 0 ]; then
    log_message "✓ El Mundo completado exitosamente"
else
    log_message "✗ Error en El Mundo"
fi

# Ejecutar ElDiario.es
log_message "Ejecutando scraper de ElDiario.es..."
python3 eldiario_scraper.py
if [ $? -eq 0 ]; then
    log_message "✓ ElDiario.es completado exitosamente"
else
    log_message "✗ Error en ElDiario.es"
fi

# Ejecutar ABC.es
log_message "Ejecutando scraper de ABC.es..."
python3 abc_scraper.py
if [ $? -eq 0 ]; then
    log_message "✓ ABC.es completado exitosamente"
else
    log_message "✗ Error en ABC.es"
fi

# Ejecutar La Vanguardia
log_message "Ejecutando scraper de La Vanguardia..."
python3 lavanguardia_scraper.py
if [ $? -eq 0 ]; then
    log_message "✓ La Vanguardia completado exitosamente"
else
    log_message "✗ Error en La Vanguardia"
fi

# Ejecutar El Confidencial
log_message "Ejecutando scraper de El Confidencial..."
python3 elconfidencial_scraper.py
if [ $? -eq 0 ]; then
    log_message "✓ El Confidencial completado exitosamente"
else
    log_message "✗ Error en El Confidencial"
fi

log_message "=== Ejecución de scrapers completada ==="
log_message ""

# Volver al directorio del proyecto
cd "$PROJECT_DIR"

# Actualizar el index.html con los nuevos datos
log_message "Actualizando index.html..."
python3 update_index.py
if [ $? -eq 0 ]; then
    log_message "✓ index.html actualizado exitosamente"
else
    log_message "✗ Error actualizando index.html"
fi

log_message "=== Proceso completo finalizado ==="
