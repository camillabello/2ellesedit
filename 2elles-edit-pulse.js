(function () {
  // Duas listas simples (sem foto): "Em Alta no Pick" (lê data/em-alta.json,
  // real e atualizado pela automação do PickYourFeed) e "Mais lidos da
  // semana" (lê data/mais-lidas.json — hoje vazio de propósito, só existe
  // ranking de verdade quando houver tráfego real; nada aqui é simulado).
  const container = document.getElementById("pulse-lists");
  if (!container) return;

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  function renderList(items, emptyMessage) {
    if (!items.length) {
      return `<p class="simple-list-empty">${emptyMessage}</p>`;
    }
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

  function buildColumn(title, desc, bodyHtml) {
    const col = document.createElement("div");
    const head = document.createElement("div");
    head.className = "edit-section-head";
    const h2 = document.createElement("h2");
    h2.className = "edit-section-name";
    h2.textContent = title;
    head.appendChild(h2);
    col.appendChild(head);
    const p = document.createElement("p");
    p.className = "edit-section-desc";
    p.textContent = desc;
    col.appendChild(p);
    const body = document.createElement("div");
    body.className = "pulse-col-body";
    body.innerHTML = bodyHtml;
    col.appendChild(body);
    return { col, body };
  }

  const section = document.createElement("section");
  section.className = "edit-section pulse-section";
  section.style.display = "grid";
  section.style.gridTemplateColumns = "1fr 1fr";
  section.style.gap = "3rem";

  const loadingHtml = "<p class=\"simple-list-empty\">Carregando…</p>";
  const emAlta = buildColumn("Em Alta no Pick", "Integrado com a home do PickYourFeed — atualizado automaticamente", loadingHtml);
  const maisLidos = buildColumn("Mais lidos da semana", "Atualizado automaticamente assim que houver tráfego real coletado", loadingHtml);

  section.appendChild(emAlta.col);
  section.appendChild(maisLidos.col);
  container.appendChild(section);

  fetch("data/em-alta.json")
    .then((r) => r.json())
    .then((data) => {
      const items = (data.items || []).map((it) => ({
        link: it.link,
        tag: it.source,
        title: it.title,
      }));
      emAlta.body.innerHTML = renderList(items, "Nada em alta no momento.");
    })
    .catch(() => {
      emAlta.body.innerHTML = renderList([], "Não foi possível carregar agora.");
    });

  fetch("data/mais-lidas.json")
    .then((r) => r.json())
    .then((data) => {
      const items = (data.items || []).map((it) => ({
        link: it.link,
        tag: it.tag || it.editorial || it.source || "",
        title: it.title,
      }));
      maisLidos.body.innerHTML = renderList(
        items,
        "Ainda sem dados reais de acesso — essa lista entra sozinha assim que o site tiver tráfego suficiente pra medir de verdade."
      );
    })
    .catch(() => {
      maisLidos.body.innerHTML = renderList(
        [],
        "Ainda sem dados reais de acesso — essa lista entra sozinha assim que o site tiver tráfego suficiente pra medir de verdade."
      );
    });

  const mql = window.matchMedia("(max-width: 720px)");
  function applyResponsive() {
    section.style.gridTemplateColumns = mql.matches ? "1fr" : "1fr 1fr";
  }
  mql.addEventListener("change", applyResponsive);
  applyResponsive();
})();
