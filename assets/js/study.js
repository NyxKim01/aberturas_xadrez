import { OPENINGS, OPENING_FAMILIES, findOpeningById } from "./data/openings.js";

const queryOpening = new URLSearchParams(window.location.search).get("opening");
let selectedOpening = findOpeningById(queryOpening);
let selectedVariation = null;
let activeFamily = "Todas";
let query = "";

const ui = {
  total: document.querySelector("#opening-total"), search: document.querySelector("#opening-search"), filters: document.querySelector("#family-filters"),
  count: document.querySelector("#result-count"), list: document.querySelector("#opening-list"),
  eco: document.querySelector("#detail-eco"), family: document.querySelector("#detail-family"), name: document.querySelector("#detail-name"), description: document.querySelector("#detail-description"), moves: document.querySelector("#detail-moves"),
  white: document.querySelector("#detail-white"), draw: document.querySelector("#detail-draw"), black: document.querySelector("#detail-black"), whiteBar: document.querySelector("#detail-white-bar"), drawBar: document.querySelector("#detail-draw-bar"), blackBar: document.querySelector("#detail-black-bar"),
  sample: document.querySelector("#sample-count"), chart: document.querySelector("#probability-chart"), variations: document.querySelector("#variation-list"), boardLink: document.querySelector("#detail-board-link"),
};

function percent(value) { return `${Math.round(value)}%`; }

function filteredOpenings() {
  const normalized = query.trim().toLocaleLowerCase("pt-BR");
  return OPENINGS.filter((opening) => activeFamily === "Todas" || opening.family === activeFamily)
    .filter((opening) => !normalized || `${opening.name} ${opening.eco} ${opening.family}`.toLocaleLowerCase("pt-BR").includes(normalized));
}

function renderFilters() {
  ui.filters.innerHTML = OPENING_FAMILIES.map((family) => `<button class="filter-pill ${family === activeFamily ? "is-active" : ""}" type="button" data-family="${family}">${family}</button>`).join("");
}

function renderList() {
  const openings = filteredOpenings();
  if(ui.count) ui.count.textContent = `${openings.length} ${openings.length === 1 ? "rota" : "rotas"}`;
  
  if(ui.list) {
    ui.list.innerHTML = openings.length ? openings.map((opening, index) => `
      <button class="opening-item ${opening.id === selectedOpening.id ? "is-selected" : ""}" type="button" data-opening="${opening.id}">
        <span class="opening-medallion">${String(index + 1).padStart(2, "0")}</span>
        <div class="item-info">
          <span class="item-eco">${opening.eco}</span>
          <span class="item-name">${opening.name}</span>
          <span class="item-family">${opening.family}</span>
        </div>
        <div class="item-stats">
          <span><strong>${opening.stats.white}%</strong> cl.</span>
          <span><strong>${opening.stats.draw}%</strong> em.</span>
          <span><strong>${opening.stats.black}%</strong> es.</span>
        </div>
      </button>`).join("") : '<div class="empty-atlas" style="padding: 24px; color: var(--text-muted);">Nenhuma corrente encontrada. Tente outro nome ou ECO.</div>';
  }
}

function selectedStats() {
  return selectedVariation ? selectedVariation.stats : selectedOpening.stats;
}

function selectedTrend() {
  if (!selectedVariation) return selectedOpening.trend;
  return selectedOpening.trend.map((value, index, all) => {
    const progress = index / (all.length - 1);
    return value + (selectedVariation.white - value) * progress;
  });
}

function renderChart() {
  if(!ui.chart) return;
  const trend = selectedTrend();
  const width = 520; const height = 170;
  const margin = { top: 18, right: 16, bottom: 27, left: 16 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const x = (index) => margin.left + (index / (trend.length - 1)) * plotWidth;
  const y = (value) => margin.top + (58 - value) / 18 * plotHeight;
  const points = trend.map((value, index) => `${x(index).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
  const area = `${margin.left},${margin.top + plotHeight} ${points} ${width - margin.right},${margin.top + plotHeight}`;
  const grid = [44, 50, 56].map((value) => `<line class="chart-grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(value)}" y2="${y(value)}"/><text class="chart-label" x="1" y="${y(value) + 3}">${value}%</text>`).join("");
  const dots = trend.map((value, index) => `<circle class="chart-dot" cx="${x(index)}" cy="${y(value)}" r="${index === trend.length - 1 ? 4 : 2.6}"/>`).join("");
  const labels = trend.map((_, index) => index % 2 === 0 || index === trend.length - 1 ? `<text class="chart-label" text-anchor="middle" x="${x(index)}" y="${height - 6}">${index + 1}</text>` : "").join("");
  
  // Updated SVG colors for Japandi theme (#C29580 for coral accent)
  ui.chart.innerHTML = `<defs><linearGradient id="chart-gradient" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#C29580"/><stop offset="100%" stop-color="#C29580" stop-opacity="0"/></linearGradient></defs>${grid}<polygon class="chart-area" points="${area}"/><polyline class="chart-line" points="${points}"/>${dots}${labels}`;
}

function renderDetail() {
  const stats = selectedStats();
  if(ui.eco) ui.eco.textContent = selectedOpening.eco;
  if(ui.family) ui.family.textContent = selectedOpening.family;
  if(ui.name) ui.name.textContent = selectedOpening.name;
  if(ui.description) ui.description.textContent = selectedVariation ? `${selectedOpening.description} Linha em foco: ${selectedVariation.name}.` : selectedOpening.description;
  if(ui.moves) ui.moves.innerHTML = selectedOpening.san.map((move) => `<span class="move-chip">${move}</span>`).join("");
  
  if(ui.white) ui.white.textContent = percent(stats.white); 
  if(ui.draw) ui.draw.textContent = percent(stats.draw); 
  if(ui.black) ui.black.textContent = percent(stats.black);
  
  if(ui.whiteBar) ui.whiteBar.style.width = `${stats.white}%`; 
  if(ui.drawBar) ui.drawBar.style.width = `${stats.draw}%`; 
  if(ui.blackBar) ui.blackBar.style.width = `${stats.black}%`;
  
  if(ui.sample) ui.sample.textContent = selectedVariation ? "linha em foco" : selectedOpening.sample;
  
  if(ui.variations) {
    ui.variations.innerHTML = selectedOpening.variations.map((variation, index) => `
      <button class="variation-row ${selectedVariation === variation ? "is-active" : ""}" type="button" data-variation="${index}">
        <div>
          <strong>${variation.name}</strong>
          <span>${variation.moves}</span>
        </div>
        <span class="variation-result">${variation.stats.white}% cl.</span>
      </button>`).join("");
  }
  
  if(ui.boardLink) {
    ui.boardLink.href = `index.html?line=${selectedOpening.moves.join(",")}`;
    ui.boardLink.innerHTML = `Experimentar ${selectedVariation ? selectedVariation.name : "no tabuleiro"} <span>→</span>`;
  }
  
  renderChart();
}

function render() {
  if (ui.total) ui.total.textContent = OPENINGS.length;
  renderFilters();
  renderList();
  renderDetail();
}

if(ui.search) {
  ui.search.addEventListener("input", (event) => { query = event.target.value; renderList(); });
}
if(ui.filters) {
  ui.filters.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-family]");
    if (!button) return;
    activeFamily = button.dataset.family;
    renderFilters(); renderList();
  });
}
if(ui.list) {
  ui.list.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-opening]");
    if (!button) return;
    selectedOpening = findOpeningById(button.dataset.opening);
    selectedVariation = null;
    window.history.replaceState({}, "", `?opening=${selectedOpening.id}`);
    renderList(); renderDetail();
  });
}
if(ui.variations) {
  ui.variations.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-variation]");
    if (!button) return;
    const variation = selectedOpening.variations[Number(button.dataset.variation)];
    selectedVariation = selectedVariation === variation ? null : variation;
    renderDetail();
  });
}

// Only render if we have the UI elements (so it doesn't crash on index.html if imported globally, though typically they are separate)
if(ui.list && ui.detailEco) {
    // Check bypassed to run in context of study page
}
render();
