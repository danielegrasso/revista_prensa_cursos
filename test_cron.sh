#!/bin/bash

# Script de prueba para verificar que el crontab funciona
echo "=== Prueba de ejecución automática ==="
echo "Fecha y hora actual: $(date)"
echo "Directorio actual: $(pwd)"
echo "Usuario: $(whoami)"
echo ""

# Verificar que los archivos existen
echo "Verificando archivos necesarios:"
if [ -f "run_all_scrapers.sh" ]; then
    echo "✓ run_all_scrapers.sh existe"
else
    echo "✗ run_all_scrapers.sh NO existe"
fi

if [ -f "update_index.py" ]; then
    echo "✓ update_index.py existe"
else
    echo "✗ update_index.py NO existe"
fi

if [ -d "scrapers_y_results" ]; then
    echo "✓ Directorio scrapers_y_results existe"
else
    echo "✗ Directorio scrapers_y_results NO existe"
fi

echo ""
echo "=== Fin de la prueba ==="
