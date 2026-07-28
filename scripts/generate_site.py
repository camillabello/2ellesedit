#!/usr/bin/env python3
"""
Gera o HTML final do site a partir de data/articles.json, data/em-alta.json,
data/curated.json e data/mais-lidas.json — todo o conteúdo já vai pronto no
HTML (não depende de JavaScript rodar pra aparecer). Isso é essencial pra
SEO, pontuação de performance (PageSpeed/Core Web Vitals) e pra ferramentas
de IA que leem a página sem executar JS.

index.html é ao mesmo tempo o arquivo fonte (você pode editar o cabeçalho,
meta tags etc à mão) e o arquivo de saída: este script substitui só os
trechos marcados por comentários <!--...START/END--> e mantém o resto.

Só biblioteca padrão do Python — mesmo princípio do fetch_feeds.py.
"""

import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.html"
DATA_DIR = ROOT / "data"

EDITORIALS = [
    {
        "key": "moda",
        "label": "Moda",
        "desc": "Coleções, semana de moda, tendências e street style",
    },
    {
        "key": "beleza",
        "label": "Beleza",
        "desc": "Skincare, maquiagem, cabelo e bem-estar",
    },
    {
        "key": "cultura",
        "label": "Cultura",
        "desc": "Celebridades, cinema, música, arte e comportamento",
    },
    {
        "key": "lifestyle",
        "label": "Lifestyle",
        "desc": "Viagem, casa, gastronomia e bem-estar",
    },
    {
        "key": "em-pauta",
        "label": "Em Pauta",
        "desc": "Os assuntos que estão movimentando a conversa",
    },
]

CURATED_PILLARS = [
    {
        "key": "inspiracao",
        "label": "Inspiração",
        "desc": "Editoriais, campanhas, branding, vitrines e direção de arte — quase um moodboard vivo",
    },
    {
        "key": "descobertas",
        "label": "Descobertas",
        "desc": "O que a redação descobriu e não resistiu a compartilhar",
    },
]

CURATED_BADGE = "Curadoria da Redação"

EDIT_FEATURED = [
    {
        "title": "Comprar sem receber nada parece absurdo?",
        "section": "Contexto",
        "read_time": "5 min de leitura",
        "image": "images/2elles-edit/mulher-navegando-online-em-casa-com-mascara-facial.jpg",
        "link": "2elles-edit/dopamine-sites-comprar-sem-receber",
    },
    {
        "title": "A inteligência artificial democratizou a moda ou apenas tornou descartáveis as pessoas que construíram essa indústria?",
        "section": "Contexto",
        "read_time": "7 min de leitura",
        "image": "images/2elles-edit/editorial-de-moda-gerado-por-inteligencia-artificial.jpg",
        "link": "2elles-edit/inteligencia-artificial-na-moda",
    },
    {
        "title": "Qual será o futuro das publis nas redes sociais?",
        "section": "Contexto",
        "read_time": "6 min de leitura",
        "image": "images/2elles-edit/influenciadora-fazendo-publi-em-loja-de-beleza.jpg",
        "link": "2elles-edit/futuro-das-publis",
    },
    {
        "title": "O que é Quiet Luxury",
        "section": "Dossiê",
        "read_time": "6 min de leitura",
        "image": "images/2elles-edit/bastidores-desfile-alta-costura-quadro-de-casting.jpg",
        "link": "2elles-edit/o-que-e-quiet-luxury",
    },
    {
        "title": "Como funciona a Haute Couture de verdade",
        "section": "Dossiê",
        "read_time": "6 min de leitura",
        "image": "images/2elles-edit/vitrine-de-atelie-com-vestidos-brancos-de-alta-costura.jpg",
        "link": "2elles-edit/como-funciona-a-haute-couture",
    },
    {
        "title": "Old Money vs. Quiet Luxury: qual a diferença real",
        "section": "Dossiê",
        "read_time": "5 min de leitura",
        "image": "images/2elles-edit/acessorios-vintage-estilo-old-money-com-oculos-e-perolas.jpg",
        "link": "2elles-edit/old-money-vs-quiet-luxury",
    },
    {
        "title": "Clean Beauty: o que significa de verdade",
        "section": "Dossiê",
        "read_time": "5 min de leitura",
        "image": "images/2elles-edit/sombra-de-maos-aplicando-serum-com-conta-gotas.jpg",
        "link": "2elles-edit/o-que-e-clean-beauty",
    },
    {
        "title": "Cruelty-free e vegano não são a mesma coisa",
        "section": "Dossiê",
        "read_time": "4 min de leitura",
        "image": "images/2elles-edit/necessaire-com-produtos-de-beleza-e-skincare.jpg",
        "link": "2elles-edit/cruelty-free-vs-vegano",
    },
    {
        "title": "A história da Glossier",
        "section": "Dossiê",
        "read_time": "6 min de leitura",
        "image": "images/2elles-edit/produtos-glossier-organizados-em-prateleira-de-banheiro.jpg",
        "link": "2elles-edit/historia-da-glossier",
    },
]

EDIT_BADGE = "2 Élles Edit"


def esc(text):
    return html.escape(text or "", quote=True)


def load_json(name, default):
    path = DATA_DIR / name
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def time_ago(iso_date):
    try:
        dt = datetime.fromisoformat(iso_date)
    except (TypeError, ValueError):
        return ""
    now = datetime.now(timezone.utc)
    diff_h = round((now - dt).total_seconds() / 3600)
    if diff_h < 1:
        return "há poucos minutos"
    if diff_h == 1:
        return "há 1 hora"
    if diff_h < 24:
        return f"há {diff_h} horas"
    diff_d = round(diff_h / 24)
    return "há 1 dia" if diff_d == 1 else f"há {diff_d} dias"


def filter_by_max_age(items_sorted_desc, max_age_hours, min_count):
    """Prefere itens dentro de max_age_hours, mas nunca deixa a lista mais
    curta que min_count - se faltar item novo, completa com os mais recentes
    disponíveis mesmo que passem da idade máxima (dia fraco de notícia não
    pode esvaziar o carrossel)."""
    if not items_sorted_desc:
        return items_sorted_desc
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    fresh = [a for a in items_sorted_desc if datetime.fromisoformat(a["pubDate"]) >= cutoff]
    if len(fresh) >= min_count:
        return fresh
    return items_sorted_desc[:min_count]


def diversify(articles):
    """Alterna Brasil/Mundo turno a turno e circula pelas fontes dentro de
    cada turno, pra nunca empilhar matérias seguidas do mesmo veículo."""
    by_source = {}
    for a in articles:
        by_source.setdefault(a["source"], []).append(a)

    sources_by_scope = {"nacional": [], "internacional": []}
    for source, items in by_source.items():
        sources_by_scope[items[0]["scope"]].append(source)

    pointer = {"nacional": 0, "internacional": 0}
    result = []
    turn = "nacional"
    misses_in_a_row = 0

    while len(result) < len(articles) and misses_in_a_row < 2:
        sources = sources_by_scope[turn]
        picked = False
        for _ in range(len(sources)):
            source = sources[pointer[turn] % len(sources)] if sources else None
            pointer[turn] += 1
            if source and by_source[source]:
                result.append(by_source[source].pop(0))
                picked = True
                break
        misses_in_a_row = 0 if picked else misses_in_a_row + 1
        turn = "internacional" if turn == "nacional" else "nacional"

    return result


def render_card(article):
    source = esc(article["source"])
    title = esc(article["title"])
    time_txt = time_ago(article["pubDate"])
    link = esc(article["link"])

    if article.get("image"):
        img = esc(article["image"])
        return f"""<div class="rail-card"><a class="rail-card-photo" href="{link}" target="_blank" rel="noopener noreferrer"><img src="{img}" alt="{title}" loading="lazy" width="250" height="313" /><div class="rail-card-overlay"></div><div class="rail-card-content"><span class="rail-card-tag">{source}</span><h3 class="rail-card-title">{title}</h3><span class="rail-card-time">{time_txt}</span></div></a></div>"""
    return f"""<div class="rail-card"><a class="rail-card-text" href="{link}" target="_blank" rel="noopener noreferrer"><div><span class="rail-card-tag">{source}</span><h3 class="rail-card-title">{title}</h3></div><span class="rail-card-time">{time_txt}</span></a></div>"""


def render_hero(article):
    if not article:
        return ""
    source = esc(article["source"])
    title = esc(article["title"])
    excerpt = esc(article.get("excerpt", ""))
    img = esc(article["image"])
    link = esc(article["link"])
    kicker = (
        f'{source}<span class="dot-brand"></span>Em Alta'
        if article.get("trendingReason")
        else f'{source}<span class="dot-brand"></span>Manchete do dia'
    )
    return f"""<section class="hero"><a class="hero-link" href="{link}" target="_blank" rel="noopener noreferrer"><img src="{img}" alt="{title}" loading="eager" fetchpriority="high" width="1200" height="620" /><div class="hero-overlay"></div><div class="hero-content"><span class="hero-kicker">{kicker}</span><h2 class="hero-title">{title}</h2><p class="hero-excerpt">{excerpt}</p></div></a></section>"""


def render_rail_section(key, title, desc, articles, variant=None):
    if not articles:
        return ""
    variant_class = f" is-{variant}" if variant else ""
    badge = (
        f'<span class="byline-badge">{esc(CURATED_BADGE)}</span>'
        if variant == "curadoria"
        else ""
    )
    cards = "".join(render_card(a) for a in articles)
    return f"""<section class="rail-section{variant_class}" id="{key}" data-editorial="{key}"><div class="rail-head"><div>{badge}<h2 class="rail-title">{esc(title)}</h2><p class="rail-desc">{esc(desc)}</p></div><div class="rail-controls"><button type="button" class="rail-arrow" data-dir="-1" aria-label="Ver manchetes anteriores">‹</button><button type="button" class="rail-arrow" data-dir="1" aria-label="Ver mais manchetes">›</button></div></div><div class="rail-track">{cards}</div></section>"""


def render_edit_card(post):
    title = esc(post["title"])
    img = esc(post["image"])
    link = esc(post["link"])
    section = esc(post["section"])
    read_time = esc(post["read_time"])
    return f"""<div class="rail-card"><a class="rail-card-photo" href="{link}"><img src="{img}" alt="{title}" loading="lazy" width="250" height="313" /><div class="rail-card-overlay"></div><div class="rail-card-content"><span class="rail-card-tag">{section}</span><h3 class="rail-card-title">{title}</h3><span class="rail-card-time">{read_time}</span></div></a></div>"""


def render_edit_rail():
    cards = "".join(render_edit_card(p) for p in EDIT_FEATURED)
    badge = f'<span class="byline-badge">{esc(EDIT_BADGE)}</span>'
    return f"""<section class="rail-section is-edit-feature" id="2elles-edit" data-editorial="2elles-edit"><div class="rail-head"><div>{badge}<p class="rail-desc">Conteúdo autoral pra quem quer ir além. <a class="rail-see-all" href="2elles-edit">Ver tudo →</a></p></div></div><div class="rail-track">{cards}</div></section>"""


def render_mais_lidas(items):
    if not items:
        return ""
    rows = "".join(
        f"""<li><a href="{esc(item['link'])}" target="_blank" rel="noopener noreferrer"><span class="mais-lidas-source">{esc(item['source'])}</span><span class="mais-lidas-title">{esc(item['title'])}</span></a></li>"""
        for item in items
    )
    return f"""<section class="mais-lidas" id="mais-lidas"><div class="rail-head"><div><h2 class="rail-title">Mais Lidas</h2><p class="rail-desc">O que as leitoras mais acessaram nas últimas 24 horas</p></div></div><ol class="mais-lidas-list">{rows}</ol></section>"""


def render_section_nav():
    links = [f'<a href="#em-alta">Em Alta</a>']
    links += [f'<a href="#{ed["key"]}">{esc(ed["label"])}</a>' for ed in EDITORIALS]
    links.append('<a href="2elles-edit" class="nav-2elles">2 Élles Edit</a>')
    return "".join(links)


def render_scope_filter():
    options = [("all", "Todas as fontes"), ("nacional", "Brasil"), ("internacional", "Mundo")]
    chips = []
    for key, label in options:
        active = " is-active" if key == "all" else ""
        chips.append(
            f'<button type="button" class="chip{active}" data-scope="{key}">{esc(label)}</button>'
        )
    return "".join(chips)


def build_main_html(articles, em_alta_items, curated_posts, mais_lidas_items):
    hero_article = em_alta_items[0] if em_alta_items else None
    if not hero_article:
        with_image = [a for a in articles if a.get("image")]
        with_image.sort(key=lambda a: a["pubDate"], reverse=True)
        hero_article = with_image[0] if with_image else None

    parts = [render_hero(hero_article)]

    em_alta_rest = diversify(
        [a for a in em_alta_items if not hero_article or a["id"] != hero_article["id"]]
    )
    parts.append(
        render_rail_section(
            "em-alta",
            "Em Alta",
            "O que você não deveria deixar de ver hoje",
            em_alta_rest,
            variant="em-alta",
        )
    )

    parts.append(render_edit_rail())

    for pillar in CURATED_PILLARS:
        posts = sorted(
            (p for p in curated_posts if p.get("pillar") == pillar["key"]),
            key=lambda p: p["pubDate"],
            reverse=True,
        )
        # Melhores itens seguem no ar por até 3 dias se não tiver nada mais novo,
        # mas nunca deixa o pilar com menos de 5 itens no ar
        posts = filter_by_max_age(posts, max_age_hours=72, min_count=5)
        parts.append(
            render_rail_section(pillar["key"], pillar["label"], pillar["desc"], posts, variant="curadoria")
        )

    for editorial in EDITORIALS:
        items = sorted(
            (a for a in articles if a["editorial"] == editorial["key"]),
            key=lambda a: a["pubDate"],
            reverse=True,
        )
        # Home sempre com matéria quente: prioriza últimas 12h, só passa
        # disso se não tiver itens novos suficientes pra preencher o rail
        items = filter_by_max_age(items, max_age_hours=12, min_count=8)
        items = diversify(items)
        parts.append(render_rail_section(editorial["key"], editorial["label"], editorial["desc"], items))

    parts.append(render_mais_lidas(mais_lidas_items))

    return "".join(p for p in parts if p)


def replace_block(html_text, marker, new_inner):
    pattern = re.compile(
        rf"(<!--{marker}_START-->)(.*?)(<!--{marker}_END-->)", re.DOTALL
    )
    if not pattern.search(html_text):
        raise RuntimeError(
            f"Marcador <!--{marker}_START-->...<!--{marker}_END--> não encontrado em index.html"
        )
    return pattern.sub(lambda m: m.group(1) + new_inner + m.group(3), html_text)


def build_item_list_jsonld(articles):
    """ItemList com as manchetes atuais — ajuda buscadores e ferramentas de
    IA a saber o que está na página agora, além do texto visível."""
    top = sorted(articles, key=lambda a: a["pubDate"], reverse=True)[:24]
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": a["link"],
                "name": a["title"],
            }
            for i, a in enumerate(top)
        ],
    }
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{payload_json}</script>'


def main():
    articles = load_json("articles.json", {"articles": []})["articles"]
    em_alta_items = load_json("em-alta.json", {"items": []})["items"]
    curated_posts = load_json("curated.json", {"posts": []})["posts"]
    mais_lidas_items = load_json("mais-lidas.json", {"items": []})["items"]

    main_html = build_main_html(articles, em_alta_items, curated_posts, mais_lidas_items)

    # O JSON embutido só existe pra re-montar os carrosséis quando o filtro
    # Brasil/Mundo/Todas muda — nenhum card mostra resumo (só tag+título+
    # hora), então "excerpt" só importa pra quem pode virar a manchete
    # principal (precisa ter foto). Cortar isso dos demais evita ~15-20% de
    # peso no payload sem perder nada visível — importa pro PageSpeed.
    def trim_for_client(article):
        trimmed = {k: v for k, v in article.items() if k not in ("excerpt", "mentions")}
        if article.get("image"):
            trimmed["excerpt"] = article.get("excerpt", "")
        return trimmed

    site_data_json = json.dumps(
        {
            "articles": [trim_for_client(a) for a in articles],
            "emAlta": [trim_for_client(a) for a in em_alta_items],
        },
        ensure_ascii=False,
    )
    # Defesa contra qualquer matéria cujo título/link contenha literalmente
    # "</" seguido de algo que pareça fechar a tag <script> — quebraria o
    # parsing HTML da página inteira. "<\/" é JSON válido (barra escapada).
    site_data_json = site_data_json.replace("</", "<\\/")
    data_script_tag = f'<script type="application/json" id="site-data">{site_data_json}</script>'

    text = INDEX_PATH.read_text(encoding="utf-8")
    text = replace_block(text, "NAV", render_section_nav())
    text = replace_block(text, "SCOPE", render_scope_filter())
    text = replace_block(text, "MAIN", main_html)
    text = replace_block(text, "DATA", data_script_tag)
    text = replace_block(text, "JSONLD_ITEMLIST", build_item_list_jsonld(articles))
    INDEX_PATH.write_text(text, encoding="utf-8")

    print(
        f"index.html gerado: {len(articles)} matérias, {len(em_alta_items)} em alta, "
        f"{len(curated_posts)} posts de curadoria, {len(mais_lidas_items)} mais lidas.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
