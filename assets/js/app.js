import { ChessGame, boardUtils } from "./core/chess-game.js";
import { PositionEvaluator, StockfishBridge } from "./core/position-evaluator.js";

const { FILES, colorOf, squareOf } = boardUtils;
const glyphs = { P: "♙", N: "♘", B: "♗", R: "♖", Q: "♕", K: "♔", p: "♟", n: "♞", b: "♝", r: "♜", q: "♛", k: "♚" };

const game = new ChessGame();
const evaluator = new PositionEvaluator();
let selectedSquare = null;
let flipped = false;
let localAnalysis = null;
let analysisVersion = 0;

const ui = {
  board: document.querySelector("#board"),
  turnOrb: document.querySelector("#turn-orb"), turnLabel: document.querySelector("#turn-label"), turnDetail: document.querySelector("#turn-detail"),
  newGame: document.querySelector("#new-game-button"), undo: document.querySelector("#undo-button"), flip: document.querySelector("#flip-button"),
  engineName: document.querySelector("#engine-name"), engineMessage: document.querySelector("#engine-message"), engineButton: document.querySelector("#engine-button"),
  moveCount: document.querySelector("#move-count"), movesLog: document.querySelector("#moves-log"), positionLabel: document.querySelector("#position-label"), positionBadge: document.querySelector("#position-badge"),
  openingEco: document.querySelector("#opening-eco"), openingName: document.querySelector("#opening-name"), openingDescription: document.querySelector("#opening-description"), openingLink: document.querySelector("#opening-link"),
  whiteProbability: document.querySelector("#white-probability"), drawProbability: document.querySelector("#draw-probability"), blackProbability: document.querySelector("#black-probability"),
  whiteBar: document.querySelector("#prob-white-bar"), drawBar: document.querySelector("#prob-draw-bar"), blackBar: document.querySelector("#prob-black-bar"),
  score: document.querySelector("#evaluation-score"), caption: document.querySelector("#evaluation-caption"), source: document.querySelector("#analysis-source"),
  route: document.querySelector("#route-tree"), routeCount: document.querySelector("#route-count"), nextCurrent: document.querySelector("#next-current"),
};

const engine = new StockfishBridge({ onStatus: updateEngineStatus });

function roundedPercentages(probabilities) {
  const entries = Object.entries(probabilities).map(([key, value]) => ({ key, value: Math.max(0, Number(value) || 0) }));
  const floors = Object.fromEntries(entries.map(({ key, value }) => [key, Math.floor(value)]));
  let remainder = 100 - Object.values(floors).reduce((sum, value) => sum + value, 0);
  entries.sort((a, b) => (b.value % 1) - (a.value % 1));
  for (let index = 0; remainder > 0; index = (index + 1) % entries.length, remainder -= 1) floors[entries[index].key] += 1;
  return floors;
}

function scoreText(score) {
  const display = Math.abs(score / 100).toFixed(2);
  return `${score > 0 ? "+" : score < 0 ? "−" : ""}${display}`;
}

function positionMood(score) {
  if (score > 95) return ["claras em fluxo", "corrente clara favorecida"];
  if (score < -95) return ["escuras em fluxo", "corrente escura favorecida"];
  if (score > 30) return ["leve maré clara", "claras com espaço"];
  if (score < -30) return ["leve maré escura", "escuras com espaço"];
  return ["equilibrada", "mar calmo"];
}

function renderBoard() {
  const ranks = flipped ? "12345678" : "87654321";
  const files = flipped ? [...FILES].reverse() : [...FILES];
  const legalTargets = selectedSquare ? new Set(game.legalMoves(selectedSquare).map((move) => squareOf(move.to))) : new Set();
  ui.board.innerHTML = "";
  ranks.split("").forEach((rank, rankIndex) => {
    files.forEach((file, fileIndex) => {
      const square = `${file}${rank}`;
      const piece = game.pieceAt(square);
      const isLight = (FILES.indexOf(file) + Number(rank)) % 2 === 0;
      const button = document.createElement("button");
      button.type = "button";
      button.className = `square ${isLight ? "light" : "dark"}${selectedSquare === square ? " selected" : ""}${game.lastMove && [game.lastMove.fromSquare, game.lastMove.toSquare].includes(square) ? " last-move" : ""}${legalTargets.has(square) ? " legal" : ""}${legalTargets.has(square) && piece ? " has-piece" : ""}`;
      button.dataset.square = square;
      button.setAttribute("role", "gridcell");
      button.setAttribute("aria-label", `${square}${piece ? `, ${pieceName(piece)}` : ", vazia"}`);
      if (piece) {
        const pawn = document.createElement("span");
        pawn.className = `piece ${colorOf(piece) === "w" ? "white" : "black"}`;
        pawn.textContent = glyphs[piece];
        button.append(pawn);
      }
      if (fileIndex === 0) {
        const label = document.createElement("span");
        label.className = "coord-rank";
        label.textContent = rank;
        button.append(label);
      }
      if (rankIndex === 7) {
        const label = document.createElement("span");
        label.className = "coord-file";
        label.textContent = file;
        button.append(label);
      }
      ui.board.append(button);
    });
  });
}

function pieceName(piece) {
  const names = { P: "peão branco", N: "cavalo branco", B: "bispo branco", R: "torre branca", Q: "dama branca", K: "rei branco", p: "peão preto", n: "cavalo preto", b: "bispo preto", r: "torre preta", q: "dama preta", k: "rei preto" };
  return names[piece];
}

function renderMoves() {
  ui.moveCount.textContent = `${game.moves.length} ${game.moves.length === 1 ? "lance" : "lances"}`;
  const rows = [];
  for (let index = 0; index < game.moves.length; index += 2) {
    rows.push(`<li><span>${Math.floor(index / 2) + 1}.</span><span>${game.moves[index]?.notation ?? ""}</span><span>${game.moves[index + 1]?.notation ?? ""}</span></li>`);
  }
  ui.movesLog.innerHTML = rows.join("");
}

function renderTurn() {
  const terminal = game.status();
  if (terminal.type === "checkmate") {
    const winner = terminal.winner === "w" ? "claras" : "escuras";
    ui.turnOrb.textContent = "\u265A";
    ui.turnLabel.textContent = `Xeque-mate — ${winner} vencem`;
    ui.turnDetail.textContent = "Partida encerrada";
    return;
  }
  if (terminal.type === "stalemate") {
    ui.turnOrb.textContent = "½";
    ui.turnLabel.textContent = "Empate por afogamento";
    ui.turnDetail.textContent = "Partida encerrada";
    return;
  }
  const white = game.turn === "w";
  ui.turnOrb.textContent = white ? "♙" : "♟";
  ui.turnLabel.textContent = white ? "Vez das peças claras" : "Vez das peças escuras";
  ui.turnDetail.textContent = white ? "Brancas para jogar" : "Pretas para jogar";
}

function renderOpening(opening) {
  if (!opening) {
    ui.openingEco.textContent = game.moves.length ? "rota em formação" : "posição livre";
    ui.openingName.textContent = game.moves.length ? "Mar aberto" : "Mar aberto";
    ui.openingDescription.textContent = game.moves.length ? "Ainda não há uma abertura catalogada para esta sequência exata." : "Faça o primeiro lance para começar a identificar a corrente.";
    ui.openingLink.href = "estudos.html";
    return;
  }
  ui.openingEco.textContent = `${opening.eco} · ${opening.family}`;
  ui.openingName.textContent = opening.name;
  ui.openingDescription.textContent = opening.description;
  ui.openingLink.href = `estudos.html?opening=${opening.id}`;
}

function renderProbabilities(analysis) {
  const { white, draw, black } = analysis.probabilities;
  const rounded = roundedPercentages(analysis.probabilities);
  ui.whiteProbability.textContent = `${rounded.white}%`;
  ui.drawProbability.textContent = `${rounded.draw}%`;
  ui.blackProbability.textContent = `${rounded.black}%`;
  ui.whiteBar.style.width = `${white}%`;
  ui.drawBar.style.width = `${draw}%`;
  ui.blackBar.style.width = `${black}%`;
  ui.score.textContent = analysis.terminal?.type === "checkmate"
    ? `mate: ${analysis.terminal.winner === "w" ? "claras" : "escuras"}`
    : analysis.terminal?.type === "stalemate" ? "empate por afogamento" : scoreText(analysis.centipawns);
  const [badge, caption] = positionMood(analysis.centipawns);
  ui.positionBadge.textContent = badge;
  ui.caption.textContent = caption;
  if (!ui.source) {
    ui.source = document.createElement("small");
    ui.source.id = "analysis-source";
    ui.score.closest(".evaluation-line")?.append(ui.source);
  }
  ui.source.textContent = analysis.source === "Stockfish 18" ? "stockfish" : "estimativa";
}

function renderRoute() {
  ui.routeCount.textContent = game.moves.length ? `${game.moves.length} nós` : "raiz";
  if (!game.moves.length) {
    ui.route.innerHTML = '<div class="route-root"><span>✦</span> início</div><p>Escolha o primeiro lance para o coral crescer.</p>';
    return;
  }
  const visible = game.moves.slice(-8);
  ui.route.innerHTML = `<div class="route-root"><span>✦</span> início</div>${visible.map((move) => `<div class="route-node">${move.notation}</div>`).join("")}`;
}

function renderNextCurrent(analysis) {
  const next = analysis.continuation;
  const opening = analysis.opening;
  if (next) {
    const nextMove = next.san[game.moves.length] ?? "continue a linha";
    ui.nextCurrent.innerHTML = `<span aria-hidden="true">🐠</span><p><strong>Corrente possível</strong><span>${nextMove} leva em direção a ${next.name}.</span></p>`;
    return;
  }
  if (opening) {
    const variation = opening.variations[0];
    ui.nextCurrent.innerHTML = `<span aria-hidden="true">🐠</span><p><strong>Próxima corrente</strong><span>Estude ${variation.name} no atlas para ver uma ramificação conhecida.</span></p>`;
    return;
  }
  ui.nextCurrent.innerHTML = '<span aria-hidden="true">🐠</span><p><strong>Próxima corrente</strong><span>O motor segue avaliando mesmo fora das rotas catalogadas.</span></p>';
}

function renderAnalysis(analysis) {
  localAnalysis = analysis;
  ui.positionLabel.textContent = game.moves.length ? `Após ${game.moves.length} ${game.moves.length === 1 ? "lance" : "lances"}` : "Posição inicial";
  renderOpening(analysis.opening);
  renderProbabilities(analysis);
  renderRoute();
  renderNextCurrent(analysis);
}

function refresh({ requestEngine = true } = {}) {
  const version = ++analysisVersion;
  renderBoard();
  renderMoves();
  renderTurn();
  const analysis = evaluator.evaluate(game);
  renderAnalysis(analysis);
  if (requestEngine && engine.ready && !analysis.terminal?.over) {
    const fen = game.fen();
    const currentTurn = game.turn;
    engine.evaluate(fen, currentTurn, (engineAnalysis) => {
      if (version !== analysisVersion || fen !== game.fen()) return;
      renderAnalysis({ ...evaluator.evaluate(game), ...engineAnalysis, source: "Stockfish 18" });
    });
  }
}

function updateEngineStatus(status) {
  if (status === "loading") {
    ui.engineName.textContent = "Mergulhando no Stockfish…";
    ui.engineMessage.textContent = "Carregando o motor leve em segundo plano.";
    ui.engineButton.textContent = "Carregando análise profunda…";
    ui.engineButton.disabled = true;
  }
  if (status === "ready") {
    ui.engineName.textContent = "Stockfish 18 · pronto";
    ui.engineMessage.textContent = "Avaliação UCI aprofundada para a posição no tabuleiro.";
    ui.engineButton.textContent = "Stockfish ativo ✦";
    ui.engineButton.disabled = true;
    refresh({ requestEngine: true });
  }
  if (status === "unavailable") {
    ui.engineName.textContent = "Maré Neural";
    ui.engineMessage.textContent = "O Stockfish não ficou acessível; a estimativa local continua ativa.";
    ui.engineButton.textContent = "Tentar Stockfish novamente →";
    ui.engineButton.disabled = false;
  }
}

ui.board.addEventListener("click", (event) => {
  const target = event.target.closest("button[data-square]");
  if (!target) return;
  const square = target.dataset.square;
  const piece = game.pieceAt(square);
  if (selectedSquare) {
    const moved = game.move(selectedSquare, square);
    if (moved) {
      selectedSquare = null;
      refresh();
      return;
    }
  }
  selectedSquare = piece && colorOf(piece) === game.turn ? square : null;
  renderBoard();
});

ui.newGame.addEventListener("click", () => { game.reset(); selectedSquare = null; refresh(); });
ui.undo.addEventListener("click", () => { if (game.undo()) { selectedSquare = null; refresh(); } });
ui.flip.addEventListener("click", () => { flipped = !flipped; renderBoard(); });
ui.engineButton.addEventListener("click", () => engine.start());

function loadLineFromAtlas() {
  const line = new URLSearchParams(window.location.search).get("line");
  if (!line) return;
  line.split(",").forEach((uci) => {
    if (!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci)) return;
    game.move(uci.slice(0, 2), uci.slice(2, 4));
  });
}

loadLineFromAtlas();
refresh({ requestEngine: false });
