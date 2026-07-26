"""
Configuração das fontes (veículos) e das regras de classificação por editoria.
Único lugar que precisa ser editado para adicionar/remover um veículo ou
ajustar a que editoria ele cai por padrão quando o feed não dá pistas melhores.
"""

# nacional | internacional, URL do feed RSS/Atom, editoria padrão (fallback)
# quando nenhuma categoria/keyword bater com nada.
SOURCES = {
    "Vogue Brasil": {
        "scope": "nacional",
        # O feed de "celebridades" da Globo é, na prática, diário pessoal de
        # famosos (passeio em família, briga de casal, foto de bebê) — não
        # tem frase-padrão de fofoca pra bloquear, então exigimos que a
        # matéria toque em moda/beleza/lifestyle de verdade (strict=True),
        # senão vira ruído mesmo vindo de uma fonte "legítima".
        "feed_url": "https://vogue.globo.com/rss/vogue",
        "default_editorial": "moda",
        "strict": True,
    },
    "Elle Brasil": {
        "scope": "nacional",
        "feed_url": "https://elle.com.br/feed",
        "default_editorial": "moda",
        "strict": True,
    },
    "Glamour Brasil": {
        "scope": "nacional",
        "feed_url": "https://glamour.globo.com/rss/glamour",
        "default_editorial": "beleza",
        "strict": True,
    },
    "FFW": {
        "scope": "nacional",
        "feed_url": "https://ffw.uol.com.br/feed/",
        "default_editorial": "moda",
    },
    "Forbes": {
        "scope": "nacional",
        # Forbes cobre de tudo (política, esporte, tech); usamos o caderno
        # "Forbes Life" (mais próximo de lifestyle/moda/comportamento) e ainda
        # exigimos que a matéria bata com alguma keyword nossa (strict=True),
        # senão o feed vira uma fonte de ruído fora do escopo do site.
        "feed_url": "https://forbes.com.br/forbeslife/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Harper's Bazaar Brasil": {
        "scope": "nacional",
        "feed_url": "https://harpersbazaar.uol.com.br/feed/",
        "default_editorial": "moda",
    },
    "Steal the Look": {
        "scope": "nacional",
        "feed_url": "https://stealthelook.com.br/feed/",
        "default_editorial": "moda",
    },
    "Marie Claire Brasil": {
        "scope": "nacional",
        "feed_url": "https://revistamarieclaire.globo.com/rss/marieclaire",
        "default_editorial": "cultura",
        "strict": True,
    },
    "Follow The Colours": {
        "scope": "nacional",
        "feed_url": "https://followthecolours.com.br/feed/",
        "default_editorial": "cultura",
    },
    "Vogue US": {
        "scope": "internacional",
        "feed_url": "https://www.vogue.com/feed/rss",
        "default_editorial": "moda",
    },
    "Elle US": {
        "scope": "internacional",
        "feed_url": "https://www.elle.com/rss/all.xml/",
        "default_editorial": "moda",
    },
    "Harper's Bazaar US": {
        "scope": "internacional",
        "feed_url": "https://www.harpersbazaar.com/rss/all.xml/",
        "default_editorial": "moda",
    },
    "Vogue UK": {
        "scope": "internacional",
        "feed_url": "https://www.vogue.co.uk/feed/rss",
        "default_editorial": "moda",
    },
    "Vogue Paris": {
        "scope": "internacional",
        "feed_url": "https://www.vogue.fr/feed/rss",
        "default_editorial": "moda",
    },
    "Business of Fashion": {
        "scope": "internacional",
        # BoF é uma publicação de negócios por natureza; sem strict, quase
        # tudo caía em "moda" por padrão mesmo sendo pauta de M&A/varejo que
        # não tem mais casa nessa arquitetura — exige bater keyword de verdade.
        "feed_url": "https://www.businessoffashion.com/feed",
        "default_editorial": "moda",
        "strict": True,
    },
    "WWD": {
        "scope": "internacional",
        "feed_url": "https://wwd.com/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Refinery29": {
        "scope": "internacional",
        "feed_url": "https://www.refinery29.com/en-us/rss.xml",
        "default_editorial": "lifestyle",
    },
    "The Cut": {
        "scope": "internacional",
        "feed_url": "http://feeds.feedburner.com/nymag/fashion",
        "default_editorial": "cultura",
    },
    "Who What Wear": {
        "scope": "internacional",
        "feed_url": "https://www.whowhatwear.com/rss",
        "default_editorial": "moda",
    },
    "Fashionista": {
        "scope": "internacional",
        "feed_url": "https://fashionista.com/.rss/full/",
        "default_editorial": "moda",
        "strict": True,
    },
    "i-D": {
        "scope": "internacional",
        "feed_url": "https://i-d.co/feed/",
        "default_editorial": "cultura",
    },
    "Highsnobiety": {
        "scope": "internacional",
        "feed_url": "https://www.highsnobiety.com/feed/",
        "default_editorial": "moda",
    },
    "Nylon": {
        "scope": "internacional",
        "feed_url": "https://www.nylon.com/rss",
        "default_editorial": "beleza",
    },
    "Hypebeast": {
        "scope": "internacional",
        # Cobre também cinema/games/tech geral, não só streetwear — exige
        # keyword pra entrar, senão vira ruído (igual à Forbes).
        "feed_url": "https://hypebeast.com/feed",
        "default_editorial": "moda",
        "strict": True,
    },
    "Dazed": {
        "scope": "internacional",
        # Cobre política e cultura pop geral além de moda — mesmo motivo.
        "feed_url": "https://www.dazeddigital.com/rss",
        "default_editorial": "cultura",
        "strict": True,
    },
    "Wallpaper*": {
        "scope": "internacional",
        "feed_url": "https://www.wallpaper.com/feeds.xml",
        "default_editorial": "lifestyle",
    },
    "Casa Vogue": {
        "scope": "nacional",
        "feed_url": "https://casavogue.globo.com/rss/casavogue",
        "default_editorial": "lifestyle",
    },
    "GQ Brasil": {
        "scope": "nacional",
        # Moda masculina + comportamento geral; mesmo risco de "diário de
        # celebridade" que Vogue/Glamour/Capricho — strict.
        "feed_url": "https://gq.globo.com/rss/gq",
        "default_editorial": "moda",
        "strict": True,
    },
    "Capricho": {
        "scope": "nacional",
        "feed_url": "https://capricho.abril.com.br/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Casa e Jardim": {
        "scope": "nacional",
        "feed_url": "https://casaejardim.globo.com/rss/casaejardim",
        "default_editorial": "lifestyle",
    },
    "Garotas Estúpidas": {
        "scope": "nacional",
        # Blog pessoal de influencer — mesmo perfil de risco de diário de
        # vida pessoal que Vogue/Glamour Brasil.
        "feed_url": "https://garotasestupidas.com/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Sallve Blog": {
        "scope": "nacional",
        "feed_url": "https://www.sallve.com.br/blogs/sallve.atom",
        "default_editorial": "beleza",
    },
    "Monocle": {
        "scope": "internacional",
        # Cobre geopolítica, negócios e cultura geral além de design/
        # lifestyle — exige bater tema nosso.
        "feed_url": "https://monocle.com/feed/",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Dezeen": {
        "scope": "internacional",
        "feed_url": "https://www.dezeen.com/feed/",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Cool Hunting": {
        "scope": "internacional",
        "feed_url": "https://coolhunting.com/feed/",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "ArchDaily Brasil": {
        "scope": "nacional",
        "feed_url": "https://www.archdaily.com.br/br/feed",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Design Culture": {
        "scope": "nacional",
        "feed_url": "https://designculture.com.br/feed/",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Archtrends": {
        "scope": "nacional",
        "feed_url": "https://blog.archtrends.com/feed/",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Habitare": {
        "scope": "nacional",
        "feed_url": "https://www.revistahabitare.com.br/blog-feed.xml",
        "default_editorial": "lifestyle",
        "strict": True,
    },
    "Brazil Journal": {
        "scope": "nacional",
        # Jornalismo de negócios geral — na prática só sobrevive o que citar
        # moda/beleza/lifestyle/cultura explicitamente (esperado: pouco
        # volume no dia a dia, e tudo bem — é melhor 0 itens que ruído).
        "feed_url": "https://braziljournal.com/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Exame": {
        "scope": "nacional",
        "feed_url": "https://exame.com/feed/",
        "default_editorial": "moda",
        "strict": True,
    },
    "Meio & Mensagem": {
        "scope": "nacional",
        "feed_url": "https://www.meioemensagem.com.br/feed",
        "default_editorial": "moda",
        "strict": True,
    },
    "Clube de Criação": {
        "scope": "nacional",
        "feed_url": "https://www.clubedecriacao.com.br/feed/",
        "default_editorial": "cultura",
        "strict": True,
    },
    "Pipeline": {
        "scope": "nacional",
        "feed_url": "https://pipelinevalor.globo.com/rss/pipelinevalor",
        "default_editorial": "moda",
        "strict": True,
    },
}

# Ordem de prioridade ao escanear texto (categorias, título, resumo, URL).
# "moda" fica por último por ser o termo mais genérico/ruidoso.
# Não existe mais editoria "mercado" nem "comportamento": conteúdo de
# negócios/varejo/M&A não tem mais casa no site (não é o produto), e
# comportamento vira Cultura quando é factual, ou Em Pauta quando é uma
# matéria em formato de debate (ver DEBATE_PATTERNS mais abaixo).
EDITORIAL_KEYWORDS = {
    "cultura": [
        "cultura", "celebridade", "celebrity", "cinema", "filme", "movie",
        "música", "musica", "music", " arte", "art exhibit", "streaming",
        "série", "serie", "festival", "red carpet", "exposição", "exposicao",
        "documentário", "documentario", "livro", "surrealis", "muse",
        # ex-"comportamento": conteúdo factual sobre relações/carreira/
        # bem-estar emocional cai aqui.
        "comportamento", "relacionamento", "relationship", "carreira", "career",
        "saúde mental", "saude mental", "terapia", "therapy", "autoestima",
        "self-esteem", "namoro", "dating", "psicolog", "casamento", "divórcio",
        "divorcio", "soft life", "amizade",
    ],
    "beleza": [
        "beleza", "beauty", "skincare", "skin care", "maquiagem", "makeup",
        "make-up", "cabelo", "hair", "perfume", "fragrance", "cosmetic",
        "cosmético", "cosmetico", "unha", "nail", "dermato",
    ],
    "lifestyle": [
        # "viagem" sozinho é ambíguo demais ("viagem a trabalho", "viagem
        # diplomática" etc.) — fontes gerais de notícia (Exame, Brazil
        # Journal) usam a palavra o tempo todo fora de contexto de lifestyle.
        "lifestyle", "roteiro de viagem", "dicas de viagem", "destino de viagem",
        "guia de viagem", "travel", "decor", "decoração", "decoracao",
        "wellness", "bem-estar", "bem estar", "receita de", "gastronomia",
        "hotel", "wellness retreat", "apartment",
    ],
    "moda": [
        "moda", "fashion", "desfile", "passarela", "runway", "coleção",
        "colecao", "collection", "alfaiataria", "alfaiate", "tailoring",
        # "tênis" sozinho também significa o esporte (tênis de quadra) — só
        # conta quando vem claramente como calçado/sneaker.
        "streetwear", "sneaker", "tênis de sola", "tênis de cano",
        "tendência", "tendencia", "trend", "outfit", "look do dia",
        "semana de moda", "fashion week", "jeans", "collab",
        "campanha publicitária", "campanha publicitaria", "grife",
    ],
}

# Palavras de categoria do próprio feed que já batem 1:1 com nossas editorias
# (checadas antes de qualquer outra heurística — maior confiança).
EDITORIAL_ALIASES = {
    "moda": "moda",
    "fashion": "moda",
    "beleza": "beleza",
    "beauty": "beleza",
    "lifestyle": "lifestyle",
    "comportamento": "cultura",
    "cultura": "cultura",
    "culture": "cultura",
    "celebridades": "cultura",
    "celebrity": "cultura",
}

EDITORIAL_ORDER = ["cultura", "beleza", "lifestyle", "moda"]

# "Em Pauta": não é definido por assunto, é definido por FORMATO — a matéria
# discute/questiona um tema em vez de reportar um fato. Checado antes de
# qualquer editoria de assunto; se bater, a matéria vai pra Em Pauta e não
# pra Moda/Beleza/Cultura/Lifestyle mesmo que também tenha essas keywords.
DEBATE_PATTERNS = [
    r"\?\s*$",  # título termina em pergunta
    r"\bvoltou\b", r"\best[áa] de volta\b", r"\bacabou\b", r"\bmorreu\b",
    r"\bo fim d[eo]\b", r"\bchegou ao fim\b", r"\bainda faz sentido\b",
    r"\bainda existe\b", r"\bvale a pena\b", r"\bpor que\b",
    r"\bé tend[êe]ncia\b", r"\bestá matando\b",
    r"\bis dead\b", r"\bis back\b", r"\bthe end of\b", r"\bwhy is\b",
    r"\bshould you\b", r"\bis over\b", r"\bstill relevant\b",
]

# Matéria é descartada se o título bater com qualquer um desses padrões —
# política/geopolítica pura. Fica fora mesmo vindo de fonte "legítima"
# (ex: Exame, Brazil Journal cobrem política geral além de negócios/moda).
POLITICS_EXCLUDE_PATTERNS = [
    r"\bpresidente (lula|bolsonaro|trump|biden)\b",
    r"\b(lula|bolsonaro|trump|biden|netanyahu|putin|zelensky|zelenski)\b",
    r"\belei[çc][ãa]o\b", r"\belei[çc][õo]es\b", r"\bcongresso nacional\b",
    r"\bc[âa]mara dos deputados\b", r"\bsenado federal\b", r"\bstf\b",
    r"\bgoverno federal\b", r"\bministro da\b", r"\bministério d[eo]\b",
    r"\bgeopol[íi]tica\b", r"\bdiplomacia\b", r"\bembaixada\b",
    r"\bconflito armado\b", r"\bguerra (na|em|entre)\b", r"\bsan[çc][õo]es\b",
    r"\bonu\b", r"\botan\b", r"\bcorte de haia\b",
]

# Matéria é descartada (não entra no site) se o título bater com qualquer um
# desses padrões — fofoca de paparazzi/vida pessoal de influencer/celebridade
# (viagem, biquíni, aniversário, affair etc.), não é o conteúdo editorial que
# o site quer entregar, mesmo vindo de um veículo "legítimo" como Glamour ou
# Marie Claire.
GOSSIP_EXCLUDE_PATTERNS = [
    r"bi?qu[íi]ni", r"\bmaiô\b",
    r"posa (de|em|após|com)", r"curte (praia|f[ée]rias|passeio|barco|viagem)",
    r"compartilha (novas |suas |mais )?(registros|cliques|fotos)",
    r"exibe (cliques|registros|o corpo|a boa forma|a barriga)",
    r"em boa forma", r"corpo sarado", r"abre álbum de",
    r"comemora anivers[áa]rio de", r"anivers[áa]rio de \d+ anos de",
    r"declara-?se (para|pra)", r"\baffair\b", r"clim[aã]o", r"assume ciúme",
    r"mostra (a |o )?filh[ao]", r"recém-nascid",
    r"se derrete (por|com)",
    r"web (vibra|reage|se derrete|surta) com", r"internautas (reagem|comentam) (a|sobre)",
    r"ensaio sensual", r"reage à briga", r"fica(r|ndo)? com sua ex",
    # Fofoca de relacionamento em inglês (Elle US, The Cut etc.) — mesmo
    # padrão, escrito diferente.
    r"relationship timeline", r"\ball about\b.*\b(wife|husband|boyfriend|girlfriend)\b",
    r"\bis a married (lady|man|woman)\b", r"\bpacked on the pda\b",
    r"\bspotted (with|holding hands)\b", r"\bsparks? dating rumors\b",
    # "lingerie" sozinho fica de fora: é pauta de moda legítima em veículos
    # internacionais (ex: "lingerie trend"). Sem contexto de pose/selfie,
    # não é fofoca.
]

# Só aplicado a fontes nacionais — "Virginia" também é nome de estado
# americano e aparece em matérias legítimas de veículos internacionais.
GOSSIP_EXCLUDE_PATTERNS_NACIONAL = [
    r"\bvirginia\b",
]

MAX_ITEMS_PER_SOURCE = 10
MAX_AGE_DAYS = 6

# Usado só para o cálculo de "Em Alta" (consenso entre fontes) — não existe
# mais editoria própria de "Pessoas"/"Marcas". Se 2+ fontes diferentes citam
# o mesmo nome desta lista na mesma janela de tempo, isso conta como sinal
# de repercussão real. Ajuste livremente — é só edição de texto.
ENTITY_WATCHLIST = [
    # pessoas
    "Jonathan Anderson", "Miuccia Prada", "Phoebe Philo", "Anna Wintour",
    "Demna", "Grace Wales Bonner", "Pierpaolo Piccioli", "Sabato De Sarno",
    "Bella Hadid", "Zendaya", "Rihanna", "Alessandro Michele",
    "Virginie Viard", "Daniel Roseberry", "Simone Bellotti",
    # marcas / grupos
    "Prada", "Versace", "Gucci", "Chanel", "Dior", "LVMH", "Kering",
    "Louis Vuitton", "Hermès", "Hermes", "Balenciaga", "Miu Miu", "Loewe",
    "Valentino", "Saint Laurent", "Givenchy", "Fendi", "Burberry",
    "Zara", "Skims", "Rhode", "Fenty", "Sephora", "Natura", "Boticário",
    "Boticario", "Renner", "C&A", "Farm", "Animale",
]

# Fontes "âncora" — usadas só como critério de qualidade (desempate) no
# cálculo de Em Alta, versão simples (sem IA). Não afeta classificação nem
# filtro, só ajuda a decidir qual matéria representa um assunto em alta
# quando várias fontes cobrem a mesma coisa.
ANCHOR_SOURCES = {
    "Vogue Brasil", "Vogue US", "Vogue UK", "Vogue Paris",
    "Elle Brasil", "Elle US",
    "Harper's Bazaar Brasil", "Harper's Bazaar US",
    "Business of Fashion", "WWD", "Dazed",
}
