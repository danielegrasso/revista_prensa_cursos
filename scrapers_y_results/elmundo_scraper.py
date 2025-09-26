#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper de la portada de elmundo.es
- Toma 5 noticias:
  * 4 primeras de h2.ue-c-cover-content__headline (parte alta de portada)
  * 1 de la zona cabecera SEO: div.ue-c-seo-links (primera no duplicada)
- Excluye enlaces de "directo" y "más noticias"
- Entra en cada noticia y extrae el subtítulo:
  <div class="ue-c-article__standfirst"><p class="ue-c-article__paragraph">
- Devuelve un JSON reutilizable con: { summary, items }
"""

import json
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

ELMUNDO_HOME = "https://www.elmundo.es/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def fetch_html(url: str, timeout: int = 15) -> BeautifulSoup:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "lxml")


def is_probable_news_link(href: str, text: str) -> bool:
    if not href:
        return False
    href_lower = href.lower()
    text_lower = (text or "").lower()

    # Exclusiones solicitadas
    if "directo" in href_lower or "live" in href_lower:
        return False
    if "intcmp=livefeed" in href_lower:
        return False
    if text_lower.startswith("más ") or text_lower.startswith("mas "):
        return False
    if "más noticias" in text_lower or "mas noticias" in text_lower:
        return False

    # Inclusión por secciones habituales
    include_patterns = [
        "/espana/", "/internacional/", "/economia/", "/deportes/",
        "/cultura/", "/opinion/", "/tecnologia/", "/ciencia/",
        "/sociedad/", "/television/", "/cronica/", "/andalucia/",
    ]
    # Excluir secciones no-noticia
    exclude_patterns = [
        "#", "/videos/", "/album/", "/pix/", "/bazar/",
        "/estaticos/", "/servicios/", "/suscriptor/", "/suscripcion/",
        "/newsletter/", "/horoscopo/", "/eltiempo/", "/programacion-tv/",
        "/guia-tv/", "/podcast/", "/juegos/", "/loteria/",
    ]
    if any(p in href_lower for p in exclude_patterns):
        return False
    return any(p in href_lower for p in include_patterns)


def extract_from_headlines_top(soup: BeautifulSoup, base_url: str, limit: int = 4):
    results = []
    seen_paths = set()

    # Caso 1: enlace dentro del h2
    for a in soup.select("h2.ue-c-cover-content__headline a"):
        href = a.get("href")
        title_text = a.get_text(" ", strip=True) or ""
        if not href or len(title_text.strip()) < 8:
            continue
        full_url = urljoin(base_url, href)
        key = urlparse(full_url).path
        if key in seen_paths:
            continue
        if not is_probable_news_link(full_url, title_text):
            continue
        results.append({"title": title_text.strip(), "url": full_url})
        seen_paths.add(key)
        if len(results) >= limit:
            return results

    # Caso 2: h2 con el texto y el enlace envolviendo por arriba (ancestor <a>)
    for h2 in soup.select("h2.ue-c-cover-content__headline"):
        if len(results) >= limit:
            break
        title_text = (h2.get_text(" ", strip=True) or "").strip()
        a_parent = h2.find_parent("a")
        href = a_parent.get("href") if a_parent else None
        if href and len(title_text) >= 8:
            full_url = urljoin(base_url, href)
            key = urlparse(full_url).path
            if key in seen_paths:
                continue
            if not is_probable_news_link(full_url, title_text):
                continue
            results.append({"title": title_text, "url": full_url})
            seen_paths.add(key)

    # Caso 3: enlace adyacente (hermanos cercanos)
    for h2 in soup.select("h2.ue-c-cover-content__headline"):
        if len(results) >= limit:
            break
        title_text = (h2.get_text(" ", strip=True) or "").strip()
        candidate_a = h2.find_previous("a") or h2.find_next("a")
        href = candidate_a.get("href") if candidate_a else None
        if href and len(title_text) >= 8:
            full_url = urljoin(base_url, href)
            key = urlparse(full_url).path
            if key in seen_paths:
                continue
            if not is_probable_news_link(full_url, title_text):
                continue
            results.append({"title": title_text, "url": full_url})
            seen_paths.add(key)

    return results[:limit]


def extract_from_seo_links(soup: BeautifulSoup, base_url: str, exclude_urls: set, want: int = 1):
    picked = []
    for a in soup.select("div.ue-c-seo-links a"):
        href = a.get("href")
        text = (a.get_text(" ", strip=True) or "").strip()
        if not href or len(text) < 8:
            continue
        full_url = urljoin(base_url, href)
        if full_url in exclude_urls:
            continue
        if not is_probable_news_link(full_url, text):
            continue
        picked.append({"title": text, "url": full_url})
        if len(picked) >= want:
            break
    return picked


def extract_standfirst(article_soup: BeautifulSoup) -> str:
    stand = article_soup.select_one(
        "div.ue-c-article__standfirst > p.ue-c-article__paragraph"
    )
    if stand:
        text = stand.get_text(" ", strip=True)
        if text:
            return text
    alternatives = [
        "div.ue-c-article__standfirst p",
        "div[class*='standfirst'] p",
        "p[class*='lead']",
        "meta[name='description']",
    ]
    for sel in alternatives:
        node = article_soup.select_one(sel)
        if node:
            if node.name == "meta":
                content = node.get("content", "").strip()
                if content:
                    return content
            else:
                text = node.get_text(" ", strip=True)
                if text:
                    return text
    return ""


def synthesize_summary(items: list) -> str:
    # Genera un párrafo neutral corto usando títulos y subtítulos
    if not items:
        return ""
    titles = [i.get("title", "").strip() for i in items if i.get("title")]
    focus = []
    for it in items:
        t = (it.get("title") or "").strip()
        s = (it.get("subtitle") or "").strip()
        if t and s:
            focus.append(f"{t}: {s}")
        elif t:
            focus.append(t)
    # Limitar longitud
    focus_text = "; ".join(focus[:3])
    summary = (
        f"Resumen del día en El Mundo: {focus_text}. "
        f"Además, se incluyen otras piezas destacadas de política, economía y sociedad."
    )
    summary += " link a la portada: https://es.kiosko.net/es/np/elmundo.html"
    return summary


def scrape_top5() -> list:
    home = fetch_html(ELMUNDO_HOME)

    # 1) Cuatro titulares principales desde h2.ue-c-cover-content__headline
    top4 = extract_from_headlines_top(home, ELMUNDO_HOME, limit=4)

    # 2) Quinta noticia desde div.ue-c-seo-links (evitando duplicados)
    exclude = {item["url"] for item in top4}
    seo_pick = extract_from_seo_links(home, ELMUNDO_HOME, exclude_urls=exclude, want=1)

    chosen = top4 + seo_pick

    results = []
    for item in chosen:
        try:
            article_soup = fetch_html(item["url"])
            subtitle = extract_standfirst(article_soup)
            results.append({
                "source": "El Mundo",
                "title": item["title"],
                "subtitle": subtitle,
                "url": item["url"],
                "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            })
        except Exception:
            continue
    return results


def save_json_object(payload: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    items = scrape_top5()
    summary = synthesize_summary(items)
    payload = {
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": ELMUNDO_HOME,
        "items": items,
    }
    save_json_object(payload, "elmundo_top5.json")
    print(f"Guardadas {len(items)} noticias en elmundo_top5.json con resumen")


if __name__ == "__main__":
    main() 