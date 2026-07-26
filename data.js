/*
 * Configuração estática do site (não muda com frequência).
 * As matérias em si NÃO ficam aqui — o HTML já vem pronto do servidor,
 * gerado por scripts/generate_site.py a partir de data/*.json (que por sua
 * vez vêm de scripts/fetch_feeds.py). Este arquivo só existe pra dar ao
 * script.js a lista de editorias, usada quando o filtro Brasil/Mundo muda
 * e o carrossel de cada editoria precisa ser refeito no navegador.
 * Ver scripts/feeds_config.py para a lista de veículos e regras de editoria,
 * e scripts/generate_site.py para as mesmas editorias do lado do build.
 */

// Ordem e metadados das editorias "de assunto" — agregadas via RSS.
// "Em Pauta" não é assunto, é FORMATO (matérias em tom de debate/pergunta),
// classificada assim no pipeline independente do tema.
const EDITORIALS = [
  {
    key: "moda",
    label: "Moda",
    desc: "Coleções, semana de moda, tendências e street style",
  },
  {
    key: "beleza",
    label: "Beleza",
    desc: "Skincare, maquiagem, cabelo e bem-estar",
  },
  {
    key: "cultura",
    label: "Cultura",
    desc: "Celebridades, cinema, música, arte e comportamento",
  },
  {
    key: "lifestyle",
    label: "Lifestyle",
    desc: "Viagem, casa, gastronomia e bem-estar",
  },
  {
    key: "em-pauta",
    label: "Em Pauta",
    desc: "Os assuntos que estão movimentando a conversa — não é notícia, é debate",
  },
];
