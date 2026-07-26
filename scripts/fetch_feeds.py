#!/usr/bin/env python3
"""
Busca os feeds RSS/Atom de todos os veículos configurados em feeds_config.py,
classifica cada matéria em uma editoria (moda/beleza/lifestyle/cultura, ou
em-pauta quando é uma matéria em formato de debate) e grava o resultado em
data/articles.json — o arquivo que o site estático (index.html/script.js)
consome em tempo de execução. Também calcula "Em Alta" por consenso entre
fontes (sem depender de nenhuma API externa) e grava em data/em-alta.json.

Só usa a biblioteca padrão do Python (sem dependências) de propósito, para
manter o pipeline leve e fácil de rodar em qualquer runner do GitHub Actions.
"""

import hashlib
import html
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

from feeds_config import (
    ANCHOR_SOURCES,
    DEBATE_PATTERNS,
    EDITORIAL_ALIASES,
    EDITORIAL_KEYWORDS,
    EDITORIAL_ORDER,
    ENTITY_WATCHLIST,
    GOSSIP_EXCLUDE_PATTERNS,
    GOSSIP_EXCLUDE_PATTERNS_NACIONAL,
    POLITICS_EXCLUDE_PATTERNS,
    MAX_AGE_DAYS,
    MAX_ITEMS_PER_SOURCE,
    SOURCES,
)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "data" / "articles.json"
EM_ALTA_OUTPUT_PATH = ROOT / "data" / "em-alta.json"
EM_ALTA_WINDOW_HOURS = 60
EM_ALTA_MAX_ITEMS = 8

USER_AGENT = (
    "Mozilla/5.0 (compatible; TrendWireBot/1.0; "
    "+https://github.com/) TrendWire RSS aggregator"
)

TAG_RE = re.compile(r"<[^>]+>")
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\'>]+)["\']', re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")

# Frases fixas que alguns veículos colam em TODA matéria (ex: a Forbes repete
# "Forbes, a mais conceituada revista de negócios..." em toda descrição), o
# que contamina a classificação por editoria e o resumo. Removidas antes de
# qualquer outro processamento.
BOILERPLATE_PATTERNS = [
    re.compile(
        r"forbes,?\s+a\s+mais\s+conceituada\s+revista\s+de\s+neg[oó]cios\s+e\s+economia\s+do\s+mundo\.?",
        re.IGNORECASE,
    ),
    # Vogue Brasil (e possivelmente outras Globo) colam esse call-to-action
    # de WhatsApp em toda matéria — e ele sozinho cita moda/beleza/cultura/
    # lifestyle, o que fazia QUALQUER matéria (até fofoca pura) passar no
    # modo estrito só por causa do rodapé. Crítico remover antes de classificar.
    re.compile(
        r"quer saber as principais novidades sobre.*?siga o canal d[ao] .*?"
        r"whatsapp e receba tudo em primeira m[ãa]o!?",
        re.IGNORECASE | re.DOTALL,
    ),
]

# Hypebeast prefixa alguns resumos com a palavra literal "Summary" colada ao
# texto (ex: "SummarySKIMS debuted..."). Só aparece depois que as tags HTML
# (ex: a imagem que vem antes) já foram removidas, então é aplicado depois
# do strip_html, não junto com o BOILERPLATE_PATTERNS.
LEADING_SUMMARY_RE = re.compile(r"^summary(?=[A-Z])", re.IGNORECASE)

# Alguns feeds (Hypebeast) removem os espaços entre frases ao achatar listas
# em HTML, deixando "Beijing.Dior slated" grudado — insere o espaço de volta.
MISSING_SPACE_RE = re.compile(r"\.(?=[A-Z])")


def strip_boilerplate(text):
    if not text:
        return text
    for pattern in BOILERPLATE_PATTERNS:
        text = pattern.sub("", text)
    return text


_GOSSIP_RE = re.compile("|".join(GOSSIP_EXCLUDE_PATTERNS), re.IGNORECASE)
_GOSSIP_RE_NACIONAL = re.compile("|".join(GOSSIP_EXCLUDE_PATTERNS_NACIONAL), re.IGNORECASE)
_POLITICS_RE = re.compile("|".join(POLITICS_EXCLUDE_PATTERNS), re.IGNORECASE)
_STATS = {"gossip_excluded": 0, "politics_excluded": 0}


def is_politics(title):
    matched = bool(_POLITICS_RE.search(title))
    if matched:
        _STATS["politics_excluded"] += 1
    return matched


def is_gossip(title, scope, link=""):
    # Sinal estrutural, não de texto: nos sites da rede Globo (Vogue/Glamour/
    # Marie Claire/Casa Vogue), a seção "/celebridades/" da URL é quase
    # inteiramente diário de vida pessoal (férias, aniversário de filho,
    # término de noivado...), mesmo quando o título não usa nenhuma frase de
    # fofoca reconhecível. Muito mais confiável que caçar frase por frase.
    if "/celebridades/" in link.lower():
        _STATS["gossip_excluded"] += 1
        return True

    matched = bool(_GOSSIP_RE.search(title)) or (
        scope == "nacional" and bool(_GOSSIP_RE_NACIONAL.search(title))
    )
    if matched:
        _STATS["gossip_excluded"] += 1
    return matched


def log(msg):
    print(msg, file=sys.stderr)


def fetch_bytes(url, timeout=15, max_redirects=5):
    # Alguns feeds (ex: Fashionista) usam 308 Permanent Redirect, que o
    # urllib padrão não segue de forma confiável em todas as versões —
    # seguimos manualmente para não depender disso.
    for _ in range(max_redirects):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308) and exc.headers.get("Location"):
                url = urllib.request.urljoin(url, exc.headers["Location"])
                continue
            raise
    raise RuntimeError(f"Excesso de redirecionamentos: {url}")


def local_tag(tag):
    """Remove o namespace de uma tag ElementTree, ex: '{atom}subtitle' -> 'subtitle'."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def strip_html(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = TAG_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def truncate(text, max_len=200):
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:") + "…"


def extract_image(*html_fragments):
    for fragment in html_fragments:
        if not fragment:
            continue
        m = IMG_SRC_RE.search(fragment)
        if m:
            return m.group(1)
    return None


def parse_pubdate(raw):
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _compile_keyword_patterns():
    patterns = {}
    for editorial, keywords in EDITORIAL_KEYWORDS.items():
        alternation = "|".join(re.escape(kw.strip()) for kw in keywords)
        patterns[editorial] = re.compile(rf"\b(?:{alternation})\b", re.IGNORECASE)
    return patterns


_KEYWORD_PATTERNS = _compile_keyword_patterns()
_DEBATE_RE = re.compile("|".join(DEBATE_PATTERNS), re.IGNORECASE)
_ENTITY_PATTERNS = {
    name: re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE) for name in ENTITY_WATCHLIST
}


def is_debate_framed(title):
    return bool(_DEBATE_RE.search(title))


def find_entity_mentions(title):
    return [name for name, pattern in _ENTITY_PATTERNS.items() if pattern.search(title)]


def classify(editorial_default, categories, title, description, link, strict=False):
    haystack_categories = [c.lower() for c in categories if c]
    combined_for_topic_check = " ".join([title or "", description or ""])
    is_on_topic = any(
        pattern.search(combined_for_topic_check) for pattern in _KEYWORD_PATTERNS.values()
    )

    # "Em Pauta" é definido pelo FORMATO do título (pergunta/debate), não
    # pelo assunto — tem prioridade sobre qualquer editoria de assunto (ex:
    # "Quiet luxury morreu?" tem "luxo" mas o que importa é o formato de
    # debate). Em fontes "strict" (Forbes, BoF...) só vale se também bater
    # algum tema nosso — senão qualquer pergunta genérica de negócios entraria.
    if is_debate_framed(title) and (not strict or is_on_topic):
        return "em-pauta"

    # Fontes "strict" (ex: Forbes) têm taxonomias de categoria muito ruidosas
    # (tags de SEO genéricas em todo texto), então ignoramos as categorias e
    # confiamos só no texto visível (título/resumo/link) para essas.
    if not strict:
        for cat in haystack_categories:
            for alias, editorial in EDITORIAL_ALIASES.items():
                if alias in cat:
                    return editorial

    combined = " ".join(
        [title or "", description or "", link or ""]
        + ([] if strict else haystack_categories)
    )

    for editorial in EDITORIAL_ORDER:
        if _KEYWORD_PATTERNS[editorial].search(combined):
            return editorial

    return None if strict else editorial_default


def parse_item(item, source_name):
    fields = {}
    categories = []

    for child in item:
        tag = local_tag(child.tag)
        text = (child.text or "").strip()

        if tag == "title":
            fields["title"] = text
        elif tag == "link":
            fields["link"] = text or (child.attrib.get("href") if child.attrib else "")
        elif tag == "pubDate" or tag == "published" or tag == "updated":
            fields.setdefault("pubDate_raw", text)
        elif tag == "description" or tag == "summary":
            # Alguns itens (visto na Vogue Brasil) trazem DUAS tags de
            # descrição — uma real e uma curta/desconexa (parece artefato do
            # gerador de RSS da Globo). Fica sempre a mais longa, não a
            # última: assim a matéria de verdade nunca é descartada por uma
            # duplicata vazia.
            candidate = child.text or ""
            if len(candidate) > len(fields.get("description", "")):
                fields["description"] = candidate
        elif tag == "encoded":  # content:encoded
            candidate = child.text or ""
            if len(candidate) > len(fields.get("content_encoded", "")):
                fields["content_encoded"] = candidate
        elif tag == "subtitle":  # atom:subtitle (usado pela Globo como dek)
            fields["subtitle"] = text
        elif tag == "category":
            categories.append(text or child.attrib.get("term", ""))
        elif tag == "thumbnail" and child.attrib.get("url"):  # media:thumbnail
            fields.setdefault("image", child.attrib["url"])
        elif tag == "content" and child.attrib.get("url"):  # media:content
            if "image" in child.attrib.get("medium", "image") or child.attrib.get(
                "url", ""
            ).lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                fields.setdefault("image", child.attrib["url"])
        elif tag == "enclosure":
            if "image" in child.attrib.get("type", ""):
                fields.setdefault("image", child.attrib.get("url"))
        elif tag == "guid":
            fields.setdefault("guid", text)

    title = strip_html(fields.get("title", ""))
    link = fields.get("link", "").strip()
    if not title or not link:
        return None

    if is_gossip(title, SOURCES[source_name]["scope"], link):
        return None  # fofoca de paparazzi/vida pessoal — fora do escopo do site

    if is_politics(title):
        return None  # política/geopolítica — fora do escopo do site

    pub_date = parse_pubdate(fields.get("pubDate_raw"))

    description_raw = strip_boilerplate(fields.get("description", ""))
    content_raw = strip_boilerplate(fields.get("content_encoded", ""))
    subtitle = strip_html(fields.get("subtitle", ""))

    excerpt = subtitle or strip_html(description_raw) or strip_html(content_raw)
    if excerpt:
        excerpt = MISSING_SPACE_RE.sub(". ", excerpt)
        excerpt = LEADING_SUMMARY_RE.sub("", excerpt)
    excerpt = truncate(excerpt) if excerpt else ""

    image = fields.get("image") or extract_image(description_raw, content_raw)

    source_config = SOURCES[source_name]
    editorial = classify(
        source_config["default_editorial"],
        categories,
        title,
        # Corta em ~400 caracteres, sempre — não dá pra confiar que
        # "description" é um resumo curto: o Pipeline (Valor), por exemplo,
        # põe o ARTIGO INTEIRO (milhares de caracteres) nessa tag. Textos
        # longos praticamente sempre contêm alguma palavra genérica por
        # acaso, o que gerava classificações falsas. Título + início do
        # texto é concentrado o bastante pra classificar bem.
        strip_html(description_raw)[:400],
        link,
        strict=source_config.get("strict", False),
    )
    if editorial is None:
        return None  # fonte "strict" (ex: Forbes) e nenhuma keyword bateu -> fora de escopo

    article_id = hashlib.md5(link.encode("utf-8")).hexdigest()[:12]

    return {
        "id": article_id,
        "editorial": editorial,
        "scope": SOURCES[source_name]["scope"],
        "source": source_name,
        "title": title,
        "excerpt": excerpt,
        "image": image,
        "link": link,
        "mentions": find_entity_mentions(title),
        "pubDate": (pub_date or datetime.now(timezone.utc)).isoformat(),
    }


def parse_feed(raw_bytes, source_name):
    # Alguns feeds (ex: FFW) mandam bytes em branco antes do <?xml ...?>,
    # o que o parser considera inválido (a declaração precisa ser a 1ª coisa).
    raw_bytes = raw_bytes.lstrip()
    try:
        root = ElementTree.fromstring(raw_bytes)
    except ElementTree.ParseError as exc:
        log(f"  [!] XML inválido para {source_name}: {exc}")
        return []

    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    articles = []
    for item in items:
        parsed = parse_item(item, source_name)
        if parsed:
            articles.append(parsed)
    return articles


def fetch_source(name, config):
    try:
        raw = fetch_bytes(config["feed_url"])
    except Exception as exc:  # noqa: BLE001 - queremos resiliência por fonte
        log(f"  [!] Falha ao buscar {name} ({config['feed_url']}): {exc}")
        return []

    articles = parse_feed(raw, name)
    articles.sort(key=lambda a: a["pubDate"], reverse=True)
    return articles[:MAX_ITEMS_PER_SOURCE]


def compute_em_alta(all_articles):
    """
    Versão simples de "Em Alta": sem IA, sem API externa. Curadoria é
    aproximada por CONSENSO ENTRE FONTES — se 2+ veículos diferentes
    publicam sobre a mesma entidade (marca/pessoa da ENTITY_WATCHLIST) numa
    janela recente, isso é repercussão real. Empate é resolvido priorizando
    fonte "âncora" + matéria com foto. Se nenhuma entidade tiver consenso
    (dia mais parado), completa com as mais recentes com foto de qualquer
    editoria, pra "Em Alta" nunca ficar vazio.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=EM_ALTA_WINDOW_HOURS)
    recent = [a for a in all_articles if datetime.fromisoformat(a["pubDate"]) >= cutoff]

    entity_sources = defaultdict(set)
    entity_articles = defaultdict(list)
    for article in recent:
        for entity in article.get("mentions", []):
            entity_sources[entity].add(article["source"])
            entity_articles[entity].append(article)

    def article_quality_key(article):
        return (
            article["source"] in ANCHOR_SOURCES,
            bool(article.get("image")),
            article["pubDate"],
        )

    trending_entities = sorted(
        (e for e, srcs in entity_sources.items() if len(srcs) >= 2),
        key=lambda e: len(entity_sources[e]),
        reverse=True,
    )

    em_alta = []
    seen_ids = set()
    for entity in trending_entities:
        best = max(entity_articles[entity], key=article_quality_key)
        if best["id"] in seen_ids:
            continue
        em_alta.append({**best, "trendingReason": f"Repercutindo em {len(entity_sources[entity])} veículos"})
        seen_ids.add(best["id"])
        if len(em_alta) >= EM_ALTA_MAX_ITEMS:
            break

    if len(em_alta) < EM_ALTA_MAX_ITEMS:
        fallback_pool = sorted(
            (a for a in recent if a.get("image") and a["id"] not in seen_ids),
            key=lambda a: a["pubDate"],
            reverse=True,
        )
        for article in fallback_pool:
            em_alta.append({**article, "trendingReason": None})
            seen_ids.add(article["id"])
            if len(em_alta) >= EM_ALTA_MAX_ITEMS:
                break

    return em_alta


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    all_articles = []
    editorial_counts = {}

    for name, config in SOURCES.items():
        log(f"Buscando {name}...")
        articles = fetch_source(name, config)
        fresh = [a for a in articles if datetime.fromisoformat(a["pubDate"]) >= cutoff]
        log(f"  -> {len(articles)} itens ({len(fresh)} dentro dos últimos {MAX_AGE_DAYS} dias)")
        all_articles.extend(fresh)
        for a in fresh:
            editorial_counts[a["editorial"]] = editorial_counts.get(a["editorial"], 0) + 1

    all_articles.sort(key=lambda a: a["pubDate"], reverse=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "articles": all_articles,
    }
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    em_alta = compute_em_alta(all_articles)
    EM_ALTA_OUTPUT_PATH.write_text(
        json.dumps(
            {"generatedAt": datetime.now(timezone.utc).isoformat(), "items": em_alta},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    log(f"\nTotal: {len(all_articles)} matérias gravadas em {OUTPUT_PATH}")
    for editorial in [*EDITORIAL_ORDER, "em-pauta"]:
        log(f"  {editorial}: {editorial_counts.get(editorial, 0)}")
    log(f"\nDescartadas por filtro anti-fofoca: {_STATS['gossip_excluded']}")
    log(f"Descartadas por filtro anti-política: {_STATS['politics_excluded']}")
    log(f"Em Alta: {len(em_alta)} itens gravados em {EM_ALTA_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
