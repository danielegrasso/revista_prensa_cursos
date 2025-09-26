# Revista de Prensa - Actualización Automática

Este proyecto automatiza la extracción de noticias de los principales medios de comunicación españoles y genera una página web actualizada diariamente.

## 📰 Medios Incluidos

- **El Mundo** (elmundo.es)
- **El Diario** (eldiario.es) 
- **ABC.es** (abc.es)
- **La Vanguardia** (lavanguardia.com)
- **El Confidencial** (elconfidencial.com)

## 🤖 Automatización

### GitHub Actions
- **Ejecución diaria**: Todos los días a las 7:15 AM (CET)
- **Actualización automática**: Extrae 5 noticias por medio
- **Commit automático**: Sube los cambios al repositorio
- **GitHub Pages**: Hosting gratuito de la página web

### Archivos Generados
- `scrapers_y_results/*_top5.json`: Datos de noticias por medio
- `index.html`: Página web actualizada
- `scraper_logs.txt`: Logs de ejecución

## 🚀 Uso Local

```bash
# Ejecutar todos los scrapers
./run_all_scrapers.sh

# Abrir la página web
open index.html
```

## 📁 Estructura del Proyecto

```
├── .github/workflows/scrapers.yml  # Automatización GitHub Actions
├── scrapers_y_results/             # Scrapers y resultados JSON
│   ├── elmundo_scraper.py
│   ├── eldiario_scraper.py
│   ├── abc_scraper.py
│   ├── lavanguardia_scraper.py
│   ├── elconfidencial_scraper.py
│   └── *_top5.json
├── run_all_scrapers.sh            # Script principal
├── update_index.py                # Actualizador de HTML
├── index.html                     # Página web
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

## 🔧 Dependencias

- Python 3.9+
- requests
- beautifulsoup4
- lxml

## 📅 Historial de Actualizaciones

Las noticias se actualizan automáticamente todos los días a las 7:15 AM. Puedes ver el historial de commits para verificar las actualizaciones.

## 🌐 Acceso Web

La página web está disponible en GitHub Pages una vez configurado el repositorio.
