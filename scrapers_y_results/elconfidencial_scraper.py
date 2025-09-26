#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper de la portada de El Confidencial
- Toma 5 noticias:
  * 4 específicas de clases principales: m-principal__title, m-fotoCentral__title, c-85__title, c-grandeFoto__title
  * 1 aleatoria evitando motor y deportes
- Excluye enlaces de "directo"/"en vivo" y "más noticias"/boletines/etc.
- Entra en cada noticia y extrae el subtítulo (standfirst/lead/excerpt/meta description)
- Devuelve JSON: { summary, generated_at, source, items[] }
"""

import json
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HOME = "https://www.elconfidencial.com/"
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
    href_l = href.lower()
    text_l = (text or "").lower()

    # Exclusiones
    if any(x in href_l for x in ["directo", "en-vivo", "minuto", "live", "vivo", "blogs", "hemeroteca", "podcasts", "multimedia", "fotos", "viñetas", "escaparate", "obituarios", "servicios", "tiempo", "newsletters", "apps", "suscripciones"]):
        return False
    if text_l.startswith("más ") or text_l.startswith("mas "):
        return False
    if any(x in text_l for x in ["más noticias", "suscríbete", "newsletter", "boletines", "hazte socio", "apps", "suscripciones", "hemeroteca", "podcasts", "multimedia", "fotos", "viñetas", "escaparate", "obituarios", "servicios", "blogs", "tiempo"]):
        return False

    # Inclusión por secciones
    include = [
        "/espana/", "/opinion/", "/cotizalia/", "/economia/", "/inmobiliario/", "/juridico/",
        "/planeta-a/", "/europa/", "/mundo/", "/cultura/", "/deportes/", "/comunicacion/",
        "/teknautas/", "/television/", "/acv/", "/motor/", "/de-compras/", "/interactivos/",
        "/multimedia/", "/madrid/", "/cataluna/", "/andalucia/", "/comunidad-valenciana/",
        "/galicia/", "/aragon/", "/pais-vasco/", "/canarias/", "/castilla-y-leon/"
    ]
    exclude = ["#", "/video/", "/videos/", "/podcast/", "/hemeroteca/", "/suscripciones/", "/clasificados/", "/newsletters/", "/apps/", "/tiempo/", "/blogs/"]
    if any(p in href_l for p in exclude):
        return False
    return any(p in href_l for p in include)


def pick_specific_news(soup: BeautifulSoup, base_url: str):
    results = []
    seen_paths = set()

    def try_add(a_tag, title_text=None):
        nonlocal results
        href = a_tag.get("href") if a_tag else None
        text = (title_text or a_tag.get_text(" ", strip=True) or "").strip()
        if not href or len(text) < 8:
            return
        full_url = urljoin(base_url, href)
        key = urlparse(full_url).path
        if key in seen_paths:
            return
        if not is_probable_news_link(full_url, text):
            return
        results.append({"title": text, "url": full_url})
        seen_paths.add(key)

    # 1) Noticia principal - m-principal__title (el enlace es el padre)
    for elem in soup.select(".m-principal__title.art-tit.titleArticleEditable"):
        parent_a = elem.parent
        if parent_a and parent_a.name == "a":
            try_add(parent_a, elem.get_text(" ", strip=True))
            break

    # 2) Noticia foto central - m-fotoCentral__title (el enlace es el padre)
    for elem in soup.select(".m-fotoCentral__title.art-tit.titleArticleEditable"):
        parent_a = elem.parent
        if parent_a and parent_a.name == "a":
            try_add(parent_a, elem.get_text(" ", strip=True))
            break

    # 3) Noticia c-85 - c-85__title (el enlace es el padre)
    for elem in soup.select(".c-85__title.art-tit.titleArticleEditable"):
        parent_a = elem.parent
        if parent_a and parent_a.name == "a":
            try_add(parent_a, elem.get_text(" ", strip=True))
            break

    # 4) Noticia c-grandeFoto - c-grandeFoto__title (el enlace es el padre)
    for elem in soup.select(".c-grandeFoto__title.art-tit.titleArticleEditable"):
        parent_a = elem.parent
        if parent_a and parent_a.name == "a":
            try_add(parent_a, elem.get_text(" ", strip=True))
            break

    return results


def pick_random_news(soup: BeautifulSoup, base_url: str, exclude_urls: set):
    candidates = []
    seen_paths = set()

    def try_add(a_tag):
        nonlocal candidates
        href = a_tag.get("href") if a_tag else None
        text = (a_tag.get_text(" ", strip=True) or "").strip()
        if not href or len(text) < 8:
            return
        full_url = urljoin(base_url, href)
        key = urlparse(full_url).path
        if key in seen_paths or full_url in exclude_urls:
            return
        
        # Excluir motor y deportes
        if "/motor/" in full_url.lower() or "/deportes/" in full_url.lower():
            return
            
        if not is_probable_news_link(full_url, text):
            return
        candidates.append({"title": text, "url": full_url})
        seen_paths.add(key)

    # Buscar candidatos en toda la página
    for a in soup.find_all("a", href=True):
        try_add(a)

    # Seleccionar uno aleatorio
    if candidates:
        return [random.choice(candidates)]
    return []


def extract_standfirst(article_soup: BeautifulSoup) -> str:
    selectors = [
        "div[class*='standfirst'] p",
        "p[class*='lead']",
        "p[class*='entradilla']",
        "p[class*='excerpt']",
        "div[class*='article-summary'] p",
        "div[class*='article-lead'] p",
        "div[class*='intro'] p",
        "div[class*='resumen'] p",
        "meta[name='description']",
        "article p",
    ]
    for sel in selectors:
        node = article_soup.select_one(sel)
        if node:
            if node.name == "meta":
                content = (node.get("content") or "").strip()
                if content:
                    return content
            else:
                text = node.get_text(" ", strip=True)
                if text and len(text) > 30:
                    return text
    return ""


def synthesize_summary(items: list) -> str:
    if not items:
        return ""
    focus = []
    for it in items:
        t = (it.get("title") or "").strip()
        s = (it.get("subtitle") or "").strip()
        if t and s:
            focus.append(f"{t}: {s}")
        elif t:
            focus.append(t)
    focus_text = "; ".join(focus[:3])
    summary = (
        f"Resumen del día en El Confidencial: {focus_text}. "
        f"Además, otras piezas destacadas de política, economía y sociedad."
    )
    return summary


def scrape_top5() -> list:
    home = fetch_html(HOME)
    
    # Obtener las 4 noticias específicas
    specific_news = pick_specific_news(home, HOME)
    exclude = {i["url"] for i in specific_news}
    
    # Obtener 1 noticia aleatoria (evitando motor y deportes)
    random_news = pick_random_news(home, HOME, exclude_urls=exclude)
    
    # Combinar todas las noticias
    chosen = specific_news + random_news

    results = []
    for item in chosen:
        try:
            article = fetch_html(item["url"])
            subtitle = extract_standfirst(article)
            results.append({
                "source": "El Confidencial",
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
        "source": HOME,
        "items": items,
    }
    save_json_object(payload, "elconfidencial_top5.json")
    print(f"Guardadas {len(items)} noticias en elconfidencial_top5.json con resumen")


if __name__ == "__main__":
    main()
