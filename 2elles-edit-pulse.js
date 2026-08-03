(function () {
  // Duas listas simples (sem foto): "Em Alta no Pick" (lê data/em-alta.json,
  // real e atualizado pela automação do PickYourFeed) e "Mais lidos da
  // semana" (lê data/mais-lidas.json — hoje vazio de propósito, só existe
  // ranking de verdade quando houver tráfego real; nada aqui é simulado).
  // "Mais lidos" só é inserida no DOM quando existir dado real: enquanto
  // estiver vazia, nem aparece (evita o widget morto/estranho na home).
  const container = document.getElementById("pulse-lists");
  if (!container) return;

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  function renderList(items) {
    const rows = items
      .slice(0, 8)
      .map((item, i) => {
        const num = String(i + 1).padStart(2, "0");
        return `<li>
          <span class="simple-list-num">${num}</span>
          <a href="${escapeHtml(item.link)}" target="_blank" rel="noopener noreferrer">
            <span class="simple-list-tag">${escapeHtml(item.tag)}</span>
            <h3 class="simple-list-title">${escapeHtml(item.title)}</h3>
          </a>
        </li>`;
      })
      .join("");
    return `<ol class="simple-list">${rows}</ol>`;
  }

  function buildColumn(title, desc) {
    const col = document.createElement("div");
    const h2 = document.createElement("p");
    h2.className = "pulse-title";
    h2.textContent = title;
    col.appendChild(h2);
    const p = document.createElement("p");
    p.className = "pulse-desc";
    p.textContent = desc;
    col.appendChild(p);
    const body = document.createElement("div");
    body.className = "pulse-col-body";
    body.innerHTML = '<p class="simple-list-empty">Carregando…</p>';
    col.appendChild(body);
    return { col, body };
  }

  function fetchItems(url, mapFn) {
    return fetch(url)
      .then((r) => r.json())
      .then((data) => (data.items || []).map(mapFn))
      .catch(() => []);
  }

  Promise.all([
    fetchItems("data/em-alta.json", (it) => ({ link: it.link, tag: it.source, title: it.title })),
    fetchItems("data/mais-lidas.json", (it) => ({
      link: it.link,
      tag: it.tag || it.editorial || it.source || "",
      title: it.title,
    })),
  ]).then(([emAltaItems, maisLidosItems]) => {
    const section = document.createElement("section");
    section.className = "edit-section pulse-section";

    const emAlta = buildColumn("Em Alta no Pick", "Integrado com a home do PickYourFeed");
    emAlta.body.innerHTML = emAltaItems.length
      ? renderList(emAltaItems)
      : '<p class="simple-list-empty">Nada em alta no momento.</p>';

    if (maisLidosItems.length) {
      section.style.display = "grid";
      section.style.gridTemplateColumns = "1fr 1fr";
      section.style.gap = "3rem";
      const maisLidos = buildColumn("Mais lidos da semana", "Atualizado automaticamente");
      maisLidos.body.innerHTML = renderList(maisLidosItems);
      section.appendChild(emAlta.col);
      section.appendChild(maisLidos.col);

      const mql = window.matchMedia("(max-width: 720px)");
      const applyResponsive = () => {
        section.style.gridTemplateColumns = mql.matches ? "1fr" : "1fr 1fr";
      };
      mql.addEventListener("change", applyResponsive);
      applyResponsive();
    } else {
      // Sem dado real ainda: só "Em Alta", largura contida (não é pra
      // parecer uma seção editorial cheia, é um widget discreto).
      emAlta.col.style.maxWidth = "420px";
      section.appendChild(emAlta.col);
    }

    container.appendChild(section);
  });
})();
