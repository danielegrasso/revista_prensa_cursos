#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper de la portada de ABC.es
- Toma 5 noticias:
  * 4 primeras de titulares principales (parte alta): h2 en zonas de portada/hero/main
  * 1 adicional de bloques laterales/listas (evitando duplicados)
- Excluye enlaces de "directo"/"en vivo" y "más noticias"/boletines/etc.
- Entra en cada noticia y extrae el subtítulo (standfirst/lead/excerpt/meta description)
- Devuelve JSON: { summary, generated_at, source, items[] }
"""

import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HOME = "https://www.abc.es/"
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
    if any(x in href_l for x in ["directo", "en-vivo", "minuto", "live"]):
        return False
    if text_l.startswith("más ") or text_l.startswith("mas "):
        return False
    if any(x in text_l for x in ["más noticias", "suscríbete", "newsletter", "boletines", "hazte socio", "apps"]):
        return False

    # Inclusión por secciones
    include = [
        "/espana/", "/internacional/", "/economia/", "/deportes/", "/cultura/",
        "/opinion/", "/gente/", "/sevilla/", "/madrid/", "/sociedad/",
    ]
    exclude = ["#", "/video/", "/videos/", "/podcast/", "/hemeroteca/", "/suscripciones/"]
    if any(p in href_l for p in exclude):
        return False
    return any(p in href_l for p in include)


def pick_top4(soup: BeautifulSoup, base_url: str, limit: int = 4):
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

    # 1) Zonas de portada/hero/principal
    for sel in [
        "section[class*='hero'] h2 a",
        "section[class*='portada'] h2 a",
        "section[class*='principal'] h2 a",
        "div[class*='hero'] h2 a",
        "div[class*='portada'] h2 a",
        "div[class*='principal'] h2 a",
    ]:
        for a in soup.select(sel):
            try_add(a)
            if len(results) >= limit:
                return results

    # 2) H2 visibles en main
    for a in soup.select("main h2 a"):
        try_add(a)
        if len(results) >= limit:
            return results

    # 3) Fallback
    for a in soup.select("h2 a"):
        try_add(a)
        if len(results) >= limit:
            break

    return results[:limit]


def pick_extra1(soup: BeautifulSoup, base_url: str, exclude_urls: set, want: int = 1):
    picked = []

    def scan(selector: str):
        nonlocal picked
        for a in soup.select(selector):
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
                return

    # Listas/editoriales laterales o navegación
    for sel in [
        "aside a",
        "nav a",
        "section[class*='lista'] a",
        "div[class*='lista'] a",
    ]:
        scan(sel)
        if len(picked) >= want:
            return picked

    # Fallback global
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        text = (a.get_text(" ", strip=True) or "").strip()
        if not href or len(text) < 12:
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
    selectors = [
        "div[class*='standfirst'] p",
        "p[class*='lead']",
        "p[class*='entradilla']",
        "p[class*='excerpt']",
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
        f"Resumen del día en ABC.es: {focus_text}. "
        f"Además, otras piezas destacadas de política, economía y sociedad."
    )
    summary += " link a la portada: https://es.kiosko.net/es/np/abc.html"
    return summary


def scrape_top5() -> list:
    home = fetch_html(HOME)
    top4 = pick_top4(home, HOME, limit=4)
    exclude = {i["url"] for i in top4}
    extra = pick_extra1(home, HOME, exclude_urls=exclude, want=1)
    chosen = top4 + extra

    results = []
    for item in chosen:
        try:
            article = fetch_html(item["url"])
            subtitle = extract_standfirst(article)
            results.append({
                "source": "ABC.es",
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
    save_json_object(payload, "abc_top5.json")
    print(f"Guardadas {len(items)} noticias en abc_top5.json con resumen")


if __name__ == "__main__":
    main() 