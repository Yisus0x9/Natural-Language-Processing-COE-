#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, quote
from datetime import datetime
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional
import feedparser

# Configuración ArXiv
ARXIV_CONFIG = {
    'base_url': 'http://export.arxiv.org/api/query',
    'categories': {
        'computation_language': 'cs.CL',
        'computer_vision': 'cs.CV',
        'cryptography_security': 'cs.CR'
    },
    'max_results_per_category': 10,
    'request_delay': 2,  # segundos entre requests
    'timeout': 30
}

# Configuración PubMed
PUBMED_CONFIG = {
    'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
    'max_results': 10,
    'batch_size': 10,
    'request_delay': 1,  # segundos entre requests
    'timeout': 30,
    'search_term': 'last_30_days[PDat]'  # últimos 30 días
}
# formato de fecha dd/mm/yy

# Configuración de archivos de salida
OUTPUT_CONFIG = {
    'arxiv_filename': 'arxiv_raw_corpus.csv',
    'pubmed_filename': 'pubmed_raw_corpus.csv',
    'encoding': 'utf-8',
    'delimiter': '\t'  # Tab como separador
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'scraper.log'
}

# Headers para requests
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArXivScraper:
    """Scraper para artículos de ArXiv"""
    
    def __init__(self):
        self.base_url = ARXIV_CONFIG['base_url']
        self.categories = ARXIV_CONFIG['categories']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_papers(self, category: str, max_results: int = 300) -> List[str]:
        """Busca papers en una categoría específica de ArXiv"""
        if category not in self.categories:
            raise ValueError(f"Categoría no válida: {category}")
        
        cat_code = self.categories[category]
        params = {
            'search_query': f'cat:{cat_code}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_arxiv_response(response.text)
        except Exception as e:
            logger.error(f"Error buscando papers en {category}: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parsea la respuesta XML de ArXiv y extrae información de los artículos"""
        papers = []
        
        try:
            # Parsear usando feedparser que maneja mejor los feeds de ArXiv
            feed = feedparser.parse(xml_content)
            
            for entry in feed.entries:
                try:
                    # Extraer ID de ArXiv del link
                    arxiv_id = entry.id.split('/')[-1]
                    
                    # Crear DOI
                    doi = f"10.48550/arXiv.{arxiv_id}"
                    
                    # Extraer autores
                    authors = []
                    if hasattr(entry, 'authors'):
                        authors = [author.name for author in entry.authors]
                    elif hasattr(entry, 'author'):
                        authors = [entry.author]
                    
                    # Extraer fecha de publicación
                    pub_date = ""
                    if hasattr(entry, 'published'):
                        pub_date = entry.published.split('T')[0]  # Solo la fecha, sin hora
                    
                    # Extraer categorías/secciones
                    sections = []
                    if hasattr(entry, 'tags'):
                        sections = [tag.term for tag in entry.tags if tag.scheme == 'http://arxiv.org/schemas/atom']
                    
                    paper = {
                        'doi': doi,
                        'title': entry.title.replace('\n', ' ').strip(),
                        'authors': '; '.join(authors),
                        'abstract': entry.summary.replace('\n', ' ').strip(),
                        'section': '; '.join(sections),
                        'date': pub_date,
                        'arxiv_id': arxiv_id
                    }
                    
                    papers.append(paper)
                    logger.info(f"Extraído paper: {paper['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error procesando entrada: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parseando respuesta XML: {e}")
        
        return papers
    
    def get_html_content(self, arxiv_id: str) -> Optional[str]:
        """Descarga el contenido HTML de un artículo de ArXiv (si está disponible)"""
        html_url = f"https://arxiv.org/html/{arxiv_id}"
        
        try:
            response = self.session.get(html_url, timeout=30)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"HTML no disponible para {arxiv_id}, código: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error descargando HTML para {arxiv_id}: {e}")
            return None



class PubMedScraper:
    """Scraper para artículos 'Trending' de PubMed"""

    def __init__(self, delay_seconds: float = 0.7, timeout: int = 25, max_retries: int = 3):
        self.base = "https://pubmed.ncbi.nlm.nih.gov"
        self.trending_url = f"{self.base}/trending/"
        self.delay = delay_seconds
        self.timeout = timeout
        self.max_retries = max_retries

        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        })

    # ---------- API pública ----------
    def get_trending_papers(self, max_results: int = 300) -> List[Dict]:
        """Obtiene artículos trending desde la UI (no E-utilities)."""
        hrefs = self._collect_trending_hrefs(max_results=max_results)
        if not hrefs:
            logger.warning("No se encontraron hrefs en Trending.")
            return []

        papers: List[Dict] = []
        for idx, href in enumerate(hrefs, 1):
            medline_text = self._fetch_pubmed_text(href)
            if not medline_text:
                continue
            batch = self._parse_medline_format(medline_text)
            # El formato `?format=pubmed` normalmente trae 1 registro por pmid
            papers.extend(batch)
            logger.info(f"[{idx}/{len(hrefs)}] Extraído PMID desde {href}")
            time.sleep(self.delay)

        return papers

    # ---------- Paso 1: extraer hrefs desde /trending/ con paginación ----------
    def _collect_trending_hrefs(self, max_results: int) -> List[str]:
        """Devuelve lista de hrefs como '/<PMID>/' desde /trending/ paginando."""
        collected: List[str] = []
        seen: set[str] = set()

        page = 1
        while len(collected) < max_results:
            url = f"{self.trending_url}?page={page}" if page > 1 else self.trending_url
            html = self._get(url)
            if not html:
                break

            hrefs = self._extract_hrefs_from_page(html)
            if not hrefs:
                # No hay más resultados o cambió el markup
                break

            for h in hrefs:
                if h not in seen:
                    seen.add(h)
                    collected.append(h)
                    if len(collected) >= max_results:
                        break

            # Heurística: si una página no trae nuevos, detenemos
            if page > 1 and not hrefs:
                break

            page += 1
            time.sleep(self.delay)

        logger.info(f"Trending hrefs recopilados: {len(collected)}")
        return collected

    def _extract_hrefs_from_page(self, html: str) -> List[str]:
        """Parses the HTML and returns relative hrefs like '/31916282/'."""
        soup = BeautifulSoup(html, "html.parser")

        # Cada resultado está en <article class="full-docsum">,
        # y el link del artículo en <a class="docsum-title" href="/<PMID>/">
        links = soup.select("article.full-docsum a.docsum-title[href]")
        hrefs: List[str] = []

        for a in links:
            href = a.get("href", "").strip()
            # Normaliza a la forma "/12345678/" y filtra basura
            if not href:
                continue
            # A veces vienen con querystring; nos quedamos con la parte /<pmid>/
            href = href.split("?")[0]
            if not href.startswith("/"):
                href = "/" + href
            # Validar que parezca PMID numérico
            m = re.search(r"/(\d+)/?$", href)
            if m:
                # Asegura trailing slash
                if not href.endswith("/"):
                    href = href + "/"
                hrefs.append(href)

        return hrefs

    # ---------- Paso 2: bajar texto MEDLINE del detalle ----------
    def _fetch_pubmed_text(self, href: str) -> Optional[str]:
        """Descarga `https://pubmed.ncbi.nlm.nih.gov{href}?format=pubmed`."""
        url = urljoin(self.base, href)
        url = f"{url}?format=pubmed"  # fuerza formato MEDLINE
        return self._get(url)

    # ---------- utilitario HTTP con reintentos/backoff ----------
    def _get(self, url: str) -> Optional[str]:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.s.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.text
                # 429/5xx -> backoff
                if resp.status_code in (429, 500, 502, 503, 504):
                    sleep = self.delay * attempt * 1.6
                    logger.warning(f"{resp.status_code} en {url} (intento {attempt}), reintentando en {sleep:.1f}s")
                    time.sleep(sleep)
                else:
                    logger.error(f"HTTP {resp.status_code} en {url}")
                    return None
            except Exception as e:
                last_exc = e
                sleep = self.delay * attempt * 1.6
                logger.warning(f"Excepción en GET {url}: {e} (intento {attempt}) -> sleep {sleep:.1f}s")
                time.sleep(sleep)
        if last_exc:
            logger.error(f"Fallo definitivo GET {url}: {last_exc}")
        return None

    # ---------- Paso 3: parser MEDLINE ----------
    def _parse_medline_format(self, medline_text: str) -> List[Dict]:
        """Parsea MEDLINE (líneas con claves 'PMID- ', 'TI  - ', etc.)."""
        papers: List[Dict] = []
        current: Dict[str, any] = {}
        last_key: Optional[str] = None

        for raw in medline_text.splitlines():
            line = raw.rstrip("\n")

            if not line.strip():
                if current:
                    papers.append(self._finalize_paper(current))
                    current = {}
                    last_key = None
                continue

            # Continuations: 6 spaces
            if line.startswith("      "):
                if last_key in ("title", "abstract"):
                    current[last_key] = (current.get(last_key, "") + " " + line.strip()).strip()
                continue

            # Campos principales
            if line.startswith("PMID- "):
                current["pmid"] = line[6:].strip()
                last_key = "pmid"
            elif line.startswith("TI  - "):
                current["title"] = line[6:].strip()
                last_key = "title"
            elif line.startswith("AB  - "):
                current["abstract"] = line[6:].strip()
                last_key = "abstract"
            elif line.startswith("AU  - "):
                current.setdefault("authors", []).append(line[6:].strip())
                last_key = "authors"
            elif line.startswith("TA  - "):
                current["journal"] = line[6:].strip()
                last_key = "journal"
            elif line.startswith("DP  - "):
                current["date"] = line[6:].strip()
                last_key = "date"
            elif line.startswith("AID - "):
                # Puede venir DOI u otros IDs; detecta DOI
                m = re.search(r"(10\.\d{4,9}/[^\s\]]+)", line)
                if m:
                    current["doi"] = m.group(1)
                last_key = "aid"
            else:
                last_key = None

        if current:
            papers.append(self._finalize_paper(current))

        return papers

    def _finalize_paper(self, d: Dict) -> Dict:
        return {
            "doi": d.get("doi", ""),
            "title": d.get("title", "").replace("\n", " ").strip(),
            "authors": "; ".join(d.get("authors", [])),
            "abstract": d.get("abstract", "").replace("\n", " ").strip(),
            "journal": d.get("journal", ""),
            "date": d.get("date", ""),
            "pmid": d.get("pmid", ""),
        }



class DataProcessor:
    """Procesador de datos para generar archivos CSV"""
    
    @staticmethod
    def save_arxiv_data(papers: List[Dict], filename: str = 'arxiv_raw_corpus.csv'):
        """Guarda los datos de ArXiv en formato CSV con tabs como separador"""
        if not papers:
            logger.warning("No hay datos para guardar")
            return
        
        fieldnames = ['DOI', 'Title', 'Authors', 'Abstract', 'Section', 'Date']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for paper in papers:
                    writer.writerow({
                        'DOI': paper.get('doi', ''),
                        'Title': paper.get('title', ''),
                        'Authors': paper.get('authors', ''),
                        'Abstract': paper.get('abstract', ''),
                        'Section': paper.get('section', ''),
                        'Date': paper.get('date', '')
                    })
            
            logger.info(f"Datos de ArXiv guardados en {filename} ({len(papers)} registros)")
            
        except Exception as e:
            logger.error(f"Error guardando datos de ArXiv: {e}")
    
    @staticmethod
    def save_pubmed_data(papers: List[Dict], filename: str = 'pubmed_raw_corpus.csv'):
        """Guarda los datos de PubMed en formato CSV con tabs como separador"""
        if not papers:
            logger.warning("No hay datos para guardar")
            return
        
        fieldnames = ['DOI', 'Title', 'Authors', 'Abstract', 'Journal', 'Date', 'PMID']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for paper in papers:
                    writer.writerow({
                        'DOI': paper.get('doi', ''),
                        'Title': paper.get('title', ''),
                        'Authors': paper.get('authors', ''),
                        'Abstract': paper.get('abstract', ''),
                        'Journal': paper.get('journal', ''),
                        'Date': paper.get('date', ''),
                        'PMID': paper.get('pmid', '')
                    })
            
            logger.info(f"Datos de PubMed guardados en {filename} ({len(papers)} registros)")
            
        except Exception as e:
            logger.error(f"Error guardando datos de PubMed: {e}")


def main():
    """Función principal para ejecutar ambos scrapers"""
    logger.info("Iniciando scraping de ArXiv y PubMed...")
    
      # Scraping de ArXiv
    logger.info("=== SCRAPING ARXIV ===")
    arxiv_scraper = ArXivScraper()
    all_arxiv_papers = []
    
    categories = ARXIV_CONFIG['categories'].keys()
    for category in categories:
        logger.info(f"Procesando categoría: {category}")
        papers = arxiv_scraper.search_papers(category, max_results=ARXIV_CONFIG['max_results_per_category'])
        all_arxiv_papers.extend(papers)
        time.sleep(2)  # Pausa entre categorías
    
    # Guardar datos de ArXiv
    DataProcessor.save_arxiv_data(all_arxiv_papers)

 
    # Scraping de PubMed
    logger.info("\n=== SCRAPING PUBMED ===")
    pubmed_scraper = PubMedScraper()
    pubmed_papers = pubmed_scraper.get_trending_papers(max_results=PUBMED_CONFIG['max_results'])
    
    # Guardar datos de PubMed
    DataProcessor.save_pubmed_data(pubmed_papers)
    
    logger.info(f"\n=== RESUMEN ===")
    logger.info(f"ArXiv papers extraídos: {len(all_arxiv_papers)}")
    logger.info(f"PubMed papers extraídos: {len(pubmed_papers)}")
    logger.info("Proceso completado!")


if __name__ == "__main__":
    main()