import { matchOpening, openingContinuation } from "../data/openings.js";
import { boardUtils } from "./chess-game.js";

const { colorOf, typeOf, squareOf } = boardUtils;
const PIECE_VALUE = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 0 };
const CENTER = new Set(["d4", "e4", "d5", "e5"]);

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function normalizeProbabilities(stats) {
  const white = Math.max(0, Number(stats.white) || 0);
  const draw = Math.max(0, Number(stats.draw) || 0);
  const black = Math.max(0, Number(stats.black) || 0);
  const sum = white + draw + black;
  if (!sum) return { white: 33.33, draw: 33.34, black: 33.33 };
  return { white: (white / sum) * 100, draw: (draw / sum) * 100, black: (black / sum) * 100 };
}

export function probabilitiesFromCentipawns(centipawns) {
  const score = clamp(Number(centipawns) || 0, -2000, 2000);
  // An estimate for the immediate local evaluator. The engine's own WDL table
  // takes precedence as soon as Stockfish is available.
  const expectedWhiteScore = 1 / (1 + 10 ** (-score / 520));
  const draw = 4 + 32 * Math.exp(-Math.abs(score) / 420);
  const white = expectedWhiteScore - draw / 200;
  const black = 1 - white - draw / 100;
  return normalizeProbabilities({ white, draw: draw / 100, black });
}

export function probabilitiesFromWdl(wdl, turn) {
  const [win, draw, loss] = wdl.map((value) => Math.max(0, Number(value) || 0));
  return normalizeProbabilities(turn === "w"
    ? { white: win, draw, black: loss }
    : { white: loss, draw, black: win });
}

function pieceValue(piece) {
  return PIECE_VALUE[typeOf(piece)] ?? 0;
}

// Looks one capture and one recapture ahead. This makes the instant estimate
// account for a piece left hanging while the deeper engine result is pending.
function immediateCaptureSwing(game) {
  let bestSwing = 0;
  const movingColor = game.turn;

  for (const move of game.allLegalMoves()) {
    if (!move.capture) continue;
    const afterCapture = game.cloneForMove();
    afterCapture.applyMove(move, false);
    let recaptureValue = 0;
    for (const reply of afterCapture.allLegalMoves()) {
      if (reply.to === move.to && reply.capture) recaptureValue = Math.max(recaptureValue, pieceValue(reply.capture));
    }
    bestSwing = Math.max(bestSwing, pieceValue(move.capture) - recaptureValue);
  }

  return movingColor === "w" ? bestSwing : -bestSwing;
}

export class PositionEvaluator {
  evaluate(game) {
    const terminal = game.status();
    const opening = matchOpening(game.moves.map((move) => move.uci));
    if (terminal.type === "checkmate") {
      const whiteWon = terminal.winner === "w";
      return {
        centipawns: whiteWon ? 10000 : -10000,
        probabilities: whiteWon ? { white: 100, draw: 0, black: 0 } : { white: 0, draw: 0, black: 100 },
        opening,
        continuation: null,
        material: { white: 0, black: 0 },
        terminal,
        source: "local",
      };
    }
    if (terminal.type === "stalemate") {
      return {
        centipawns: 0,
        probabilities: { white: 0, draw: 100, black: 0 },
        opening,
        continuation: null,
        material: { white: 0, black: 0 },
        terminal,
        source: "local",
      };
    }

    let score = 0;
    let whiteMaterial = 0;
    let blackMaterial = 0;
    let whiteDevelopment = 0;
    let blackDevelopment = 0;

    game.board.forEach((piece, index) => {
      if (!piece) return;
      const color = colorOf(piece);
      const type = typeOf(piece);
      const sign = color === "w" ? 1 : -1;
      const square = squareOf(index);
      const value = PIECE_VALUE[type];
      score += sign * value;
      if (color === "w") whiteMaterial += value; else blackMaterial += value;

      if (type === "p" && CENTER.has(square)) score += sign * 18;
      if ((type === "n" || type === "b") && !["b1", "g1", "b8", "g8", "c1", "f1", "c8", "f8"].includes(square)) {
        score += sign * 12;
        if (color === "w") whiteDevelopment += 1; else blackDevelopment += 1;
      }
      if (type === "p" && CENTER.has(square)) score += sign * 7;
      if (type === "k" && ["g1", "c1"].includes(square)) score += 24;
      if (type === "k" && ["g8", "c8"].includes(square)) score -= 24;
      if ((type === "n" || type === "b") && CENTER.has(square)) score += sign * 9;
    });

    const moveNumber = game.moves.length;
    if (moveNumber < 14) score += (whiteDevelopment - blackDevelopment) * 5;
    if (game.isInCheck("w")) score -= 36;
    if (game.isInCheck("b")) score += 36;
    score += immediateCaptureSwing(game);
    if (moveNumber === 0) score = 4;

    const base = probabilitiesFromCentipawns(score);
    let probabilities = base;
    if (opening && game.moves.length <= opening.moves.length + 6) {
      const historical = normalizeProbabilities(opening.stats);
      const historyWeight = Math.max(.14, .4 - game.moves.length * .022);
      probabilities = normalizeProbabilities({
        white: base.white * (1 - historyWeight) + historical.white * historyWeight,
        draw: base.draw * (1 - historyWeight) + historical.draw * historyWeight,
        black: base.black * (1 - historyWeight) + historical.black * historyWeight,
      });
    }

    return {
      centipawns: Math.round(score),
      probabilities,
      opening,
      continuation: openingContinuation(game.moves.map((move) => move.uci)),
      material: { white: whiteMaterial, black: blackMaterial },
      terminal,
      source: "Maré Neural",
    };
  }
}

const STOCKFISH_WORKER = new URL("../../vendor/stockfish/stockfish-18-lite-single.js", import.meta.url);

/**
 * Starts the locally served Stockfish Worker only when requested. Keeping the
 * Worker and its WASM side-by-side avoids the fragile remote Blob/CORS setup.
 */
export class StockfishBridge {
  constructor({ onStatus = () => {} } = {}) {
    this.onStatus = onStatus;
    this.worker = null;
    this.ready = false;
    this.loading = false;
    this.pending = null;
    this.queued = null;
    this.startPromise = null;
    this.startTimeout = null;
    this.readyResolver = null;
  }

  async start() {
    if (this.ready) return true;
    if (this.loading) return this.startPromise;
    this.loading = true;
    this.onStatus("loading");
    try {
      this.worker = new Worker(STOCKFISH_WORKER);
      this.worker.addEventListener("message", (event) => this.handleMessage(String(event.data)));
      this.worker.addEventListener("error", () => this.fail());
      this.worker.addEventListener("messageerror", () => this.fail());
      this.startPromise = new Promise((resolve) => {
        this.readyResolver = resolve;
        this.startTimeout = window.setTimeout(() => this.fail(), 15000);
      });
      this.worker.postMessage("uci");
      return await this.startPromise;
    } catch {
      this.fail();
      return false;
    }
  }

  handleMessage(line) {
    if (line === "uciok") {
      this.worker?.postMessage("setoption name UCI_ShowWDL value true");
      this.worker?.postMessage("isready");
      return;
    }
    if (line === "readyok") {
      this.ready = true;
      this.loading = false;
      window.clearTimeout(this.startTimeout);
      this.startTimeout = null;
      this.onStatus("ready");
      this.readyResolver?.(true);
      this.readyResolver = null;
      return;
    }
    if (!this.pending) return;

    const score = line.match(/\bscore (cp|mate) (-?\d+)/);
    if (score) {
      const numeric = Number(score[2]);
      this.pending.score = score[1] === "mate" ? Math.sign(numeric || 1) * 10000 : numeric;
      this.pending.mate = score[1] === "mate" ? numeric : null;
    }
    const wdl = line.match(/\bwdl\s+(\d+)\s+(\d+)\s+(\d+)/);
    if (wdl) this.pending.wdl = [Number(wdl[1]), Number(wdl[2]), Number(wdl[3])];

    if (line.startsWith("bestmove")) {
      const completed = this.pending;
      this.pending = null;
      const centipawns = completed.turn === "w" ? completed.score : -completed.score;
      completed.callback({
        centipawns,
        probabilities: completed.mate
          ? (centipawns > 0 ? { white: 100, draw: 0, black: 0 } : { white: 0, draw: 0, black: 100 })
          : completed.wdl
          ? probabilitiesFromWdl(completed.wdl, completed.turn)
          : probabilitiesFromCentipawns(centipawns),
        bestMove: line.split(" ")[1],
      });
      if (this.queued) {
        const next = this.queued;
        this.queued = null;
        this.beginEvaluation(next);
      }
    }
  }

  evaluate(fen, turn, callback) {
    if (!this.ready || !this.worker) return false;
    const request = { fen, turn, callback, score: 0, mate: null, wdl: null };
    if (this.pending) {
      this.queued = request;
      this.worker.postMessage("stop");
      return true;
    }
    this.beginEvaluation(request);
    return true;
  }

  beginEvaluation(request) {
    this.pending = request;
    this.worker?.postMessage(`position fen ${request.fen}`);
    this.worker?.postMessage("go depth 13");
  }

  fail() {
    window.clearTimeout(this.startTimeout);
    this.startTimeout = null;
    this.ready = false;
    this.loading = false;
    this.pending = null;
    this.queued = null;
    this.onStatus("unavailable");
    this.readyResolver?.(false);
    this.readyResolver = null;
    this.startPromise = null;
    this.worker?.terminate();
    this.worker = null;
  }
}
