(function () {
  // O HTML já vem pronto do servidor (gerado por scripts/generate_site.py) —
  // isso é o que garante que crawlers de busca e de IA, e o Lighthouse,
  // vejam o conteúdo real sem precisar rodar JS. Este arquivo só ADICIONA
  // interatividade por cima do que já está na página: as setas do
  // carrossel e o filtro Brasil/Mundo/Todas. Ele nunca busca dados via
  // fetch() — lê o mesmo JSON que o Python já embutiu na página.
  const mainEl = document.getElementById("main");
  const scopeFilterEl = document.getElementById("scope-filter");

  let activeScope = "all";
  let allArticles = [];
  let allEmAlta = [];

  const dataScript = document.getElementById("site-data");
  try {
    const embedded = JSON.parse((dataScript && dataScript.textContent) || "{}");
    allArticles = embedded.articles || [];
    allEmAlta = embedded.emAlta || [];
  } catch (err) {
    console.error("Não foi possível ler os dados embutidos da página", err);
  }

  const timeAgo = (isoDate) => {
    const diffMs = Date.now() - new Date(isoDate).getTime();
    const diffH = Math.round(diffMs / 3600000);
    if (diffH < 1) return "há poucos minutos";
    if (diffH === 1) return "há 1 hora";
    if (diffH < 24) return `há ${diffH} horas`;
    const diffD = Math.round(diffH / 24);
    return diffD === 1 ? "há 1 dia" : `há ${diffD} dias`;
  };

  const escapeHtml = (str) =>
    str.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const filterByScope = (articles) =>
    activeScope === "all" ? articles : articles.filter((a) => a.scope === activeScope);

  // Alterna Brasil/Mundo turno a turno e circula pelas fontes dentro de cada
  // turno, pra nunca empilhar matérias seguidas do mesmo veículo.
  const diversify = (articles) => {
    const bySource = new Map();
    articles.forEach((a) => {
      if (!bySource.has(a.source)) bySource.set(a.source, []);
      bySource.get(a.source).push(a);
    });

    const sourcesByScope = { nacional: [], internacional: [] };
    bySource.forEach((items, source) => {
      sourcesByScope[items[0].scope]?.push(source);
    });

    const pointer = { nacional: 0, internacional: 0 };
    const result = [];
    let turn = "nacional";
    let missesInARow = 0;

    while (result.length < articles.length && missesInARow < 2) {
      const sources = sourcesByScope[turn];
      let picked = false;
      for (let i = 0; i < sources.length; i++) {
        const source = sources[pointer[turn] % sources.length];
        pointer[turn]++;
        const bucket = bySource.get(source);
        if (bucket.length) {
          result.push(bucket.shift());
          picked = true;
          break;
        }
      }
      missesInARow = picked ? 0 : missesInARow + 1;
      turn = turn === "nacional" ? "internacional" : "nacional";
    }

    return result;
  };

  // ---------- Construção de DOM (só usada ao re-renderizar por filtro) ----------

  const railCard = (article) => {
    const wrapper = document.createElement("div");
    wrapper.className = "rail-card";

    const link = document.createElement("a");
    link.href = article.link;
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    if (article.image) {
      link.className = "rail-card-photo";
      link.innerHTML = `
        <img src="${article.image}" alt="${escapeHtml(article.title)}" loading="lazy" width="250" height="313" />
        <div class="rail-card-overlay"></div>
        <div class="rail-card-content">
          <span class="rail-card-tag">${escapeHtml(article.source)}</span>
          <h3 class="rail-card-title">${escapeHtml(article.title)}</h3>
          <span class="rail-card-time">${timeAgo(article.pubDate)}</span>
        </div>
      `;
    } else {
      link.className = "rail-card-text";
      link.innerHTML = `
        <div>
          <span class="rail-card-tag">${escapeHtml(article.source)}</span>
          <h3 class="rail-card-title">${escapeHtml(article.title)}</h3>
        </div>
        <span class="rail-card-time">${timeAgo(article.pubDate)}</span>
      `;
    }

    wrapper.appendChild(link);
    return wrapper;
  };

  const renderHero = (heroArticle) => {
    const section = document.createElement("section");
    section.className = "hero";
    if (!heroArticle) return section;

    const link = document.createElement("a");
    link.href = heroArticle.link;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.className = "hero-link";

    const kicker = heroArticle.trendingReason
      ? `${escapeHtml(heroArticle.source)} · Em Alta`
      : `${escapeHtml(heroArticle.source)} · Manchete do dia`;

    link.innerHTML = `
      <img src="${heroArticle.image}" alt="${escapeHtml(heroArticle.title)}" loading="eager" width="1200" height="620" />
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <span class="hero-kicker">${kicker}</span>
        <h2 class="hero-title">${escapeHtml(heroArticle.title)}</h2>
        <p class="hero-excerpt">${escapeHtml(heroArticle.excerpt || "")}</p>
      </div>
    `;

    section.appendChild(link);
    return section;
  };

  const renderRailSection = ({ key, title, desc, articles, variant }) => {
    if (!articles || articles.length === 0) return null;

    const section = document.createElement("section");
    section.className = "rail-section" + (variant ? ` is-${variant}` : "");
    section.id = key;
    section.dataset.editorial = key;

    const head = document.createElement("div");
    head.className = "rail-head";
    head.innerHTML = `
      <div>
        <h2 class="rail-title">${escapeHtml(title)}</h2>
        <p class="rail-desc">${escapeHtml(desc)}</p>
      </div>
      <div class="rail-controls">
        <button type="button" class="rail-arrow" data-dir="-1" aria-label="Ver manchetes anteriores">‹</button>
        <button type="button" class="rail-arrow" data-dir="1" aria-label="Ver mais manchetes">›</button>
      </div>
    `;
    section.appendChild(head);

    const track = document.createElement("div");
    track.className = "rail-track";
    articles.forEach((a) => track.appendChild(railCard(a)));
    section.appendChild(track);

    wireUpRail(section);
    return section;
  };

  // ---------- Interatividade sobre uma seção já existente no DOM ----------
  // Funciona igual para seções que vieram prontas do servidor e pras que o
  // JS acabou de montar — é só isso que faz as setas do carrossel andarem.

  const wireUpRail = (section) => {
    const track = section.querySelector(".rail-track");
    const [prevBtn, nextBtn] = section.querySelectorAll(".rail-arrow");
    if (!track || !prevBtn || !nextBtn) return;

    const updateArrows = () => {
      prevBtn.disabled = track.scrollLeft <= 4;
      nextBtn.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 4;
    };
    const scrollByCards = (dir) => {
      const firstCard = track.firstElementChild;
      const cardWidth = firstCard ? firstCard.getBoundingClientRect().width + 16 : 260;
      track.scrollBy({ left: dir * cardWidth * 2, behavior: "smooth" });
    };
    prevBtn.addEventListener("click", () => scrollByCards(-1));
    nextBtn.addEventListener("click", () => scrollByCards(1));
    track.addEventListener("scroll", updateArrows, { passive: true });
    requestAnimationFrame(updateArrows);
  };

  // ---------- Re-render do que depende do filtro Brasil/Mundo/Todas ----------
  // Curadoria (Inspiração/Descobertas) e Mais Lidas NÃO dependem de escopo,
  // então ficam do jeito que vieram do servidor — só isto aqui é refeito.

  const updateScopeDependentSections = () => {
    const visibleArticles = filterByScope(allArticles);
    const visibleEmAlta = filterByScope(allEmAlta);

    const heroArticle =
      visibleEmAlta[0] ||
      visibleArticles.filter((a) => a.image).sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate))[0];

    const currentHero = document.querySelector(".hero");
    if (currentHero) currentHero.replaceWith(renderHero(heroArticle));

    const emAltaRest = diversify(
      visibleEmAlta.filter((a) => !heroArticle || a.id !== heroArticle.id)
    );
    const newEmAlta = renderRailSection({
      key: "em-alta",
      title: "Em Alta",
      desc: "O que vale a pena conhecer hoje — curadoria, não só o que mais bombou",
      articles: emAltaRest,
      variant: "em-alta",
    });
    const currentEmAlta = document.getElementById("em-alta");
    if (currentEmAlta) {
      if (newEmAlta) currentEmAlta.replaceWith(newEmAlta);
      else currentEmAlta.remove();
    } else if (newEmAlta) {
      document.querySelector(".hero")?.after(newEmAlta);
    }

    EDITORIALS.forEach((editorial) => {
      const items = diversify(
        visibleArticles
          .filter((a) => a.editorial === editorial.key)
          .sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate))
      );
      const newSection = renderRailSection({
        key: editorial.key,
        title: editorial.label,
        desc: editorial.desc,
        articles: items,
      });
      const current = document.getElementById(editorial.key);
      if (current) {
        if (newSection) current.replaceWith(newSection);
        else current.remove();
      } else if (newSection) {
        mainEl.appendChild(newSection);
      }
    });
  };

  // ---------- Boot: só interatividade, o conteúdo já está na página ----------

  const boot = () => {
    document.querySelectorAll(".rail-section").forEach(wireUpRail);

    scopeFilterEl.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        activeScope = chip.dataset.scope;
        scopeFilterEl.querySelectorAll(".chip").forEach((c) => {
          c.classList.toggle("is-active", c === chip);
        });
        updateScopeDependentSections();
      });
    });
  };

  boot();
})();
