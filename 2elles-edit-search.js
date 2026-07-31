(function () {
  // Busca e filtro por tag do 2 Élles Edit — roda inteiro no navegador, sobre
  // os cards que já vêm prontos no HTML. Sem fetch, sem backend: só lê o
  // data-tag e o título que cada .rail-card já carrega.
  const searchInput = document.getElementById("edit-search");
  const tagFilterEl = document.querySelector(".edit-tag-filter");
  const emptyMsgEl = document.querySelector(".edit-empty-msg");

  if (!searchInput && !tagFilterEl) return;

  const sections = Array.from(document.querySelectorAll("[data-searchable]"));
  const cards = sections.flatMap((section) =>
    Array.from(section.querySelectorAll(".rail-card"))
  );

  if (!cards.length) return;

  let activeTag = "all";

  const normalize = (str) =>
    (str || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();

  const applyFilter = () => {
    const query = normalize(searchInput ? searchInput.value : "");
    let visibleTotal = 0;

    sections.forEach((section) => {
      const sectionCards = Array.from(section.querySelectorAll(".rail-card"));
      let visibleInSection = 0;

      sectionCards.forEach((card) => {
        const matchesTag = activeTag === "all" || card.dataset.tag === activeTag;
        const title = card.querySelector(".rail-card-title");
        const matchesQuery = !query || normalize(title ? title.textContent : "").includes(query);
        const visible = matchesTag && matchesQuery;

        card.style.display = visible ? "" : "none";
        if (visible) visibleInSection++;
      });

      visibleTotal += visibleInSection;

      if (section.dataset.searchable === "section") {
        section.style.display = visibleInSection === 0 ? "none" : "";
      }
    });

    if (emptyMsgEl) {
      emptyMsgEl.style.display = visibleTotal === 0 ? "block" : "none";
    }
  };

  if (searchInput) {
    searchInput.addEventListener("input", applyFilter);
  }

  if (tagFilterEl) {
    tagFilterEl.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        activeTag = chip.dataset.tag;
        tagFilterEl.querySelectorAll(".chip").forEach((c) => {
          c.classList.toggle("is-active", c === chip);
        });
        applyFilter();
      });
    });
  }

  applyFilter();
})();
