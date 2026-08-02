(function () {
  // Monta as fileiras por tema (Moda/Beleza/Cultura/Em Pauta) ao vivo, lendo
  // o data-tag que cada .rail-card já carrega. Não duplica dado nenhum: os
  // cards aqui são clones dos mesmos cards das seções por editoria abaixo,
  // então continuam automaticamente em dia conforme a publicação automática
  // adiciona matérias novas — nada aqui precisa ser mantido à mão.
  const container = document.getElementById("theme-rails");
  if (!container) return;

  const THEMES = [
    { key: "moda", label: "Moda", desc: "Coleções, semana de moda, tendências e street style" },
    { key: "beleza", label: "Beleza", desc: "Skincare, maquiagem, cabelo e bem-estar" },
    { key: "cultura", label: "Cultura", desc: "Celebridades, cinema, música, arte, comportamento e lifestyle" },
    { key: "em-pauta", label: "Em Pauta", desc: "Os assuntos que estão movimentando a conversa" },
  ];

  const cards = Array.from(document.querySelectorAll(".rail-card[data-tag]"));
  const buckets = { moda: [], beleza: [], cultura: [], "em-pauta": [] };

  cards.forEach((card) => {
    let tag = card.dataset.tag;
    if (tag === "lifestyle") tag = "cultura";
    if (buckets[tag]) buckets[tag].push(card);
  });

  THEMES.forEach((theme) => {
    const items = buckets[theme.key].slice(0, 5);
    if (!items.length) return;

    const section = document.createElement("section");
    section.className = "edit-section theme-rail";
    section.id = "tema-" + theme.key;

    const head = document.createElement("div");
    head.className = "edit-section-head";
    const h2 = document.createElement("h2");
    h2.className = "edit-section-name";
    h2.textContent = theme.label;
    head.appendChild(h2);
    section.appendChild(head);

    const desc = document.createElement("p");
    desc.className = "edit-section-desc";
    desc.textContent = theme.desc;
    section.appendChild(desc);

    const grid = document.createElement("div");
    grid.className = "theme-grid";
    items.forEach((card) => grid.appendChild(card.cloneNode(true)));
    section.appendChild(grid);

    container.appendChild(section);
  });
})();
