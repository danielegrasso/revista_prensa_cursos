#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para actualizar automáticamente el index.html con los datos más recientes
de todos los JSONs de scrapers
"""

import json
import os
from datetime import datetime

def load_json_data(json_path):
    """Cargar datos de un archivo JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando {json_path}: {e}")
        return None

def format_time(timestamp):
    """Formatear timestamp a formato legible"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        # Convertir a zona horaria de Madrid (CET/CEST)
        import pytz
        madrid_tz = pytz.timezone('Europe/Madrid')
        dt_madrid = dt.astimezone(madrid_tz)
        return dt_madrid.strftime('%d/%m/%Y %H:%M')
    except:
        return timestamp

def generate_news_item_html(item, source_name):
    """Generar HTML para una noticia individual"""
    title = item.get('title', '').replace('"', '&quot;')
    subtitle = item.get('subtitle', '').replace('"', '&quot;')
    url = item.get('url', '#')
    scraped_at = item.get('scraped_at', '')
    date_formatted = format_time(scraped_at)
    
    return f'''                    <div class="news-item">
                        <div class="news-title">
                            <a href="{url}" target="_blank">
                                {title}
                            </a>
                        </div>
                        <div class="news-subtitle">
                            {subtitle}
                        </div>
                        <div class="news-meta">{source_name} • {date_formatted}</div>
                    </div>'''

def generate_media_section_html(media_data, media_id, media_name, has_portada=False, portada_url=""):
    """Generar HTML para una sección de medio"""
    generated_at = media_data.get('generated_at', '')
    update_time = format_time(generated_at)
    items = media_data.get('items', [])
    
    # Generar noticias
    news_items_html = '\n'.join([
        generate_news_item_html(item, media_name) 
        for item in items
    ])
    
    # Generar enlace a portada si existe
    portada_html = ""
    if has_portada and portada_url:
        portada_html = f'''
            <div class="portada-link">
                <a href="{portada_url}" target="_blank">Portada Papel</a>
            </div>'''
    
    return f'''        <!-- Sección {media_name} -->
        <div class="media-section">
            <div class="media-header" onclick="toggleSection('{media_id}')">
                <div class="media-title-container">
                    <div class="media-title">{media_name}</div>
                    <div class="update-time">{update_time}</div>
                </div>
                <div class="toggle-icon" id="{media_id}-icon">▼</div>
            </div>{portada_html}
            <div class="news-content" id="{media_id}-content">
                <div class="news-list">
{news_items_html}
                </div>
            </div>
        </div>'''

def main():
    # Rutas de los archivos JSON
    scrapers_dir = "scrapers_y_results"
    json_files = {
        'elmundo': {
            'file': f'{scrapers_dir}/elmundo_top5.json',
            'name': 'El Mundo',
            'has_portada': True,
            'portada_url': 'https://es.kiosko.net/es/np/elmundo.html'
        },
        'eldiario': {
            'file': f'{scrapers_dir}/eldiario_top5.json',
            'name': 'ElDiario.es',
            'has_portada': False,
            'portada_url': ''
        },
        'abc': {
            'file': f'{scrapers_dir}/abc_top5.json',
            'name': 'ABC.es',
            'has_portada': True,
            'portada_url': 'https://es.kiosko.net/es/np/abc.html'
        },
        'lavanguardia': {
            'file': f'{scrapers_dir}/lavanguardia_top5.json',
            'name': 'La Vanguardia',
            'has_portada': True,
            'portada_url': 'https://es.kiosko.net/es/np/lavanguardia.html'
        },
        'elconfidencial': {
            'file': f'{scrapers_dir}/elconfidencial_top5.json',
            'name': 'El Confidencial',
            'has_portada': False,
            'portada_url': ''
        }
    }
    
    # Cargar datos de todos los medios
    media_sections = []
    for media_id, config in json_files.items():
        data = load_json_data(config['file'])
        if data:
            section_html = generate_media_section_html(
                data, 
                media_id, 
                config['name'], 
                config['has_portada'], 
                config['portada_url']
            )
            media_sections.append(section_html)
    
    # Generar HTML completo
    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reseña de Prensa</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #ffffff;
            color: #000000;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        h1 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: #000000;
            font-weight: 300;
        }}

        .media-section {{
            margin-bottom: 2rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}

        .media-header {{
            background-color: #f8f9fa;
            padding: 1rem 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s ease;
        }}

        .media-header:hover {{
            background-color: #e9ecef;
        }}

        .media-title-container {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .media-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #000000;
        }}

        .update-time {{
            font-size: 0.85rem;
            color: #666666;
            font-weight: 400;
        }}

        .toggle-icon {{
            font-size: 1.2rem;
            transition: transform 0.3s ease;
        }}

        .toggle-icon.expanded {{
            transform: rotate(180deg);
        }}

        .portada-link {{
            padding: 1rem 1.5rem;
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
            text-align: left;
        }}

        .portada-link a {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
        }}

        .portada-link a:hover {{
            text-decoration: underline;
        }}

        .news-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}

        .news-content.expanded {{
            max-height: 2000px;
        }}

        .news-list {{
            padding: 1rem 1.5rem;
        }}

        .news-item {{
            margin-bottom: 1.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #f0f0f0;
        }}

        .news-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}

        .news-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #000000;
        }}

        .news-title a {{
            color: #000000;
            text-decoration: none;
        }}

        .news-title a:hover {{
            text-decoration: underline;
        }}

        .news-subtitle {{
            font-size: 0.9rem;
            color: #666666;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }}

        .news-meta {{
            font-size: 0.8rem;
            color: #999999;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            h1 {{
                font-size: 2rem;
            }}

            .media-header {{
                padding: 0.8rem 1rem;
            }}

            .media-title-container {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.3rem;
            }}

            .media-title {{
                font-size: 1.1rem;
            }}

            .update-time {{
                font-size: 0.8rem;
            }}

            .portada-link {{
                padding: 0.8rem 1rem;
            }}

            .news-list {{
                padding: 0.8rem 1rem;
            }}

            .news-title {{
                font-size: 1rem;
            }}

            .news-subtitle {{
                font-size: 0.85rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Reseña de Prensa</h1>
        
{chr(10).join(media_sections)}
    </div>

    <script>
        function toggleSection(sectionId) {{
            const content = document.getElementById(sectionId + '-content');
            const icon = document.getElementById(sectionId + '-icon');
            
            if (content.classList.contains('expanded')) {{
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            }} else {{
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }}
        }}
    </script>
</body>
</html>'''
    
    # Escribir el archivo HTML
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✓ index.html actualizado exitosamente")
        return True
    except Exception as e:
        print(f"✗ Error escribiendo index.html: {e}")
        return False

if __name__ == "__main__":
    main()
