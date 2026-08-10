const FILES = "abcdefgh";
const RANKS = "87654321";

const PIECE_LETTERS = { p: "", n: "C", b: "B", r: "T", q: "D", k: "R" };

function colorOf(piece) {
  if (!piece) return null;
  return piece === piece.toUpperCase() ? "w" : "b";
}

function typeOf(piece) {
  return piece?.toLowerCase() ?? null;
}

function opposite(color) {
  return color === "w" ? "b" : "w";
}

function inside(row, col) {
  return row >= 0 && row < 8 && col >= 0 && col < 8;
}

function indexOf(row, col) {
  return row * 8 + col;
}

function squareOf(index) {
  return `${FILES[index % 8]}${RANKS[Math.floor(index / 8)]}`;
}

function indexFromSquare(square) {
  const column = FILES.indexOf(square?.[0]);
  const row = RANKS.indexOf(square?.[1]);
  return column < 0 || row < 0 ? -1 : indexOf(row, column);
}

function initialBoard() {
  return [
    "r", "n", "b", "q", "k", "b", "n", "r",
    "p", "p", "p", "p", "p", "p", "p", "p",
    null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null,
    "P", "P", "P", "P", "P", "P", "P", "P",
    "R", "N", "B", "Q", "K", "B", "N", "R",
  ];
}

export class ChessGame {
  constructor() {
    this.reset();
  }

  reset() {
    this.board = initialBoard();
    this.turn = "w";
    this.castling = { K: true, Q: true, k: true, q: true };
    this.enPassant = null;
    this.moves = [];
    this.history = [];
    this.lastMove = null;
  }

  snapshot() {
    return {
      board: [...this.board],
      turn: this.turn,
      castling: { ...this.castling },
      enPassant: this.enPassant,
      moves: this.moves.map((move) => ({ ...move })),
      lastMove: this.lastMove ? { ...this.lastMove } : null,
    };
  }

  restore(snapshot) {
    this.board = [...snapshot.board];
    this.turn = snapshot.turn;
    this.castling = { ...snapshot.castling };
    this.enPassant = snapshot.enPassant;
    this.moves = snapshot.moves.map((move) => ({ ...move }));
    this.lastMove = snapshot.lastMove ? { ...snapshot.lastMove } : null;
  }

  undo() {
    const previous = this.history.pop();
    if (!previous) return false;
    this.restore(previous);
    return true;
  }

  cloneForMove() {
    const clone = Object.create(ChessGame.prototype);
    clone.restore(this.snapshot());
    clone.history = [];
    return clone;
  }

  pieceAt(square) {
    return this.board[indexFromSquare(square)];
  }

  legalMoves(square) {
    const from = indexFromSquare(square);
    if (from < 0 || colorOf(this.board[from]) !== this.turn) return [];
    return this.pseudoMoves(from).filter((move) => {
      if (move.castle && !this.castleIsSafe(move)) return false;
      const test = this.cloneForMove();
      test.applyMove(move, false);
      return !test.isInCheck(this.turn);
    });
  }

  allLegalMoves() {
    const moves = [];
    this.board.forEach((piece, index) => {
      if (piece && colorOf(piece) === this.turn) moves.push(...this.legalMoves(squareOf(index)));
    });
    return moves;
  }

  status() {
    const legalMoves = this.allLegalMoves();
    if (legalMoves.length) return { over: false, type: null, winner: null };
    if (this.isInCheck(this.turn)) return { over: true, type: "checkmate", winner: opposite(this.turn) };
    return { over: true, type: "stalemate", winner: null };
  }

  move(fromSquare, toSquare) {
    const move = this.legalMoves(fromSquare).find((candidate) => candidate.to === indexFromSquare(toSquare));
    if (!move) return null;
    this.history.push(this.snapshot());
    this.applyMove(move, true);
    return move;
  }

  pseudoMoves(from) {
    const piece = this.board[from];
    const color = colorOf(piece);
    const type = typeOf(piece);
    const row = Math.floor(from / 8);
    const col = from % 8;
    const moves = [];
    const add = (to, options = {}) => {
      const target = this.board[to];
      if (target && colorOf(target) === color) return;
      moves.push({ from, to, piece, capture: target ?? null, ...options });
    };

    if (type === "p") {
      const direction = color === "w" ? -1 : 1;
      const startRow = color === "w" ? 6 : 1;
      const promotionRow = color === "w" ? 0 : 7;
      const one = row + direction;
      if (inside(one, col) && !this.board[indexOf(one, col)]) {
        add(indexOf(one, col), { promotion: one === promotionRow ? (color === "w" ? "Q" : "q") : null });
        const two = row + direction * 2;
        if (row === startRow && !this.board[indexOf(two, col)]) add(indexOf(two, col), { doublePawn: true });
      }
      for (const deltaCol of [-1, 1]) {
        const captureRow = row + direction;
        const captureCol = col + deltaCol;
        if (!inside(captureRow, captureCol)) continue;
        const target = indexOf(captureRow, captureCol);
        if (this.board[target] && colorOf(this.board[target]) !== color) {
          add(target, { promotion: captureRow === promotionRow ? (color === "w" ? "Q" : "q") : null });
        }
        if (this.enPassant === target) add(target, { enPassant: true, capture: color === "w" ? "p" : "P" });
      }
    }

    if (type === "n") {
      for (const [dr, dc] of [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]) {
        if (inside(row + dr, col + dc)) add(indexOf(row + dr, col + dc));
      }
    }

    if (type === "b" || type === "r" || type === "q") {
      const directions = [];
      if (type === "b" || type === "q") directions.push([-1, -1], [-1, 1], [1, -1], [1, 1]);
      if (type === "r" || type === "q") directions.push([-1, 0], [1, 0], [0, -1], [0, 1]);
      for (const [dr, dc] of directions) {
        let nextRow = row + dr;
        let nextCol = col + dc;
        while (inside(nextRow, nextCol)) {
          const target = indexOf(nextRow, nextCol);
          if (!this.board[target]) add(target);
          else {
            if (colorOf(this.board[target]) !== color) add(target);
            break;
          }
          nextRow += dr;
          nextCol += dc;
        }
      }
    }

    if (type === "k") {
      for (let dr = -1; dr <= 1; dr += 1) {
        for (let dc = -1; dc <= 1; dc += 1) {
          if ((dr || dc) && inside(row + dr, col + dc)) add(indexOf(row + dr, col + dc));
        }
      }
      if (color === "w" && from === indexFromSquare("e1")) {
        if (this.castling.K && !this.board[indexFromSquare("f1")] && !this.board[indexFromSquare("g1")] && this.board[indexFromSquare("h1")] === "R") add(indexFromSquare("g1"), { castle: "K" });
        if (this.castling.Q && !this.board[indexFromSquare("d1")] && !this.board[indexFromSquare("c1")] && !this.board[indexFromSquare("b1")] && this.board[indexFromSquare("a1")] === "R") add(indexFromSquare("c1"), { castle: "Q" });
      }
      if (color === "b" && from === indexFromSquare("e8")) {
        if (this.castling.k && !this.board[indexFromSquare("f8")] && !this.board[indexFromSquare("g8")] && this.board[indexFromSquare("h8")] === "r") add(indexFromSquare("g8"), { castle: "k" });
        if (this.castling.q && !this.board[indexFromSquare("d8")] && !this.board[indexFromSquare("c8")] && !this.board[indexFromSquare("b8")] && this.board[indexFromSquare("a8")] === "r") add(indexFromSquare("c8"), { castle: "q" });
      }
    }
    return moves;
  }

  castleIsSafe(move) {
    const color = colorOf(move.piece);
    if (this.isInCheck(color)) return false;
    const passThrough = move.castle === "K" || move.castle === "k" ? "f" : "d";
    const rank = color === "w" ? "1" : "8";
    return !this.isSquareAttacked(indexFromSquare(`${passThrough}${rank}`), opposite(color));
  }

  applyMove(move, annotate) {
    const color = colorOf(move.piece);
    const fromSquare = squareOf(move.from);
    const toSquare = squareOf(move.to);
    const capturedAt = move.enPassant ? move.to + (color === "w" ? 8 : -8) : move.to;
    this.board[move.from] = null;
    this.board[capturedAt] = null;
    this.board[move.to] = move.promotion ?? move.piece;

    if (move.castle === "K") { this.board[indexFromSquare("h1")] = null; this.board[indexFromSquare("f1")] = "R"; }
    if (move.castle === "Q") { this.board[indexFromSquare("a1")] = null; this.board[indexFromSquare("d1")] = "R"; }
    if (move.castle === "k") { this.board[indexFromSquare("h8")] = null; this.board[indexFromSquare("f8")] = "r"; }
    if (move.castle === "q") { this.board[indexFromSquare("a8")] = null; this.board[indexFromSquare("d8")] = "r"; }

    this.updateCastlingRights(move, fromSquare, toSquare);
    this.enPassant = move.doublePawn ? move.from + (color === "w" ? -8 : 8) : null;
    const notation = this.notationFor(move, toSquare);
    const record = { ...move, fromSquare, toSquare, uci: `${fromSquare}${toSquare}${move.promotion ? "q" : ""}`, notation, color };
    this.lastMove = record;
    if (annotate) this.moves.push(record);
    this.turn = opposite(this.turn);
  }

  updateCastlingRights(move, fromSquare, toSquare) {
    if (move.piece === "K") { this.castling.K = false; this.castling.Q = false; }
    if (move.piece === "k") { this.castling.k = false; this.castling.q = false; }
    if (fromSquare === "a1" || toSquare === "a1") this.castling.Q = false;
    if (fromSquare === "h1" || toSquare === "h1") this.castling.K = false;
    if (fromSquare === "a8" || toSquare === "a8") this.castling.q = false;
    if (fromSquare === "h8" || toSquare === "h8") this.castling.k = false;
  }

  notationFor(move, toSquare) {
    if (move.castle === "K" || move.castle === "k") return "O-O";
    if (move.castle === "Q" || move.castle === "q") return "O-O-O";
    const type = typeOf(move.piece);
    const capture = move.capture ? "x" : "";
    const pawnFile = type === "p" && capture ? squareOf(move.from)[0] : "";
    const promotion = move.promotion ? `=${PIECE_LETTERS[typeOf(move.promotion)]}` : "";
    return `${PIECE_LETTERS[type]}${pawnFile}${capture}${toSquare}${promotion}`;
  }

  isInCheck(color) {
    const king = color === "w" ? "K" : "k";
    const kingSquare = this.board.indexOf(king);
    return kingSquare >= 0 && this.isSquareAttacked(kingSquare, opposite(color));
  }

  isSquareAttacked(target, byColor) {
    const targetRow = Math.floor(target / 8);
    const targetCol = target % 8;
    const pawnRow = targetRow + (byColor === "w" ? 1 : -1);
    for (const pawnCol of [targetCol - 1, targetCol + 1]) {
      if (inside(pawnRow, pawnCol) && this.board[indexOf(pawnRow, pawnCol)] === (byColor === "w" ? "P" : "p")) return true;
    }
    for (const [dr, dc] of [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]) {
      if (inside(targetRow + dr, targetCol + dc) && this.board[indexOf(targetRow + dr, targetCol + dc)] === (byColor === "w" ? "N" : "n")) return true;
    }
    for (const [dr, dc, hunters] of [
      [-1, -1, ["b", "q"]], [-1, 1, ["b", "q"]], [1, -1, ["b", "q"]], [1, 1, ["b", "q"]],
      [-1, 0, ["r", "q"]], [1, 0, ["r", "q"]], [0, -1, ["r", "q"]], [0, 1, ["r", "q"]],
    ]) {
      let row = targetRow + dr; let col = targetCol + dc;
      while (inside(row, col)) {
        const piece = this.board[indexOf(row, col)];
        if (piece) {
          if (colorOf(piece) === byColor && hunters.includes(typeOf(piece))) return true;
          break;
        }
        row += dr; col += dc;
      }
    }
    for (let dr = -1; dr <= 1; dr += 1) {
      for (let dc = -1; dc <= 1; dc += 1) {
        if ((dr || dc) && inside(targetRow + dr, targetCol + dc) && this.board[indexOf(targetRow + dr, targetCol + dc)] === (byColor === "w" ? "K" : "k")) return true;
      }
    }
    return false;
  }

  fen() {
    const ranks = [];
    for (let row = 0; row < 8; row += 1) {
      let empty = 0; let rank = "";
      for (let col = 0; col < 8; col += 1) {
        const piece = this.board[indexOf(row, col)];
        if (piece) { if (empty) { rank += empty; empty = 0; } rank += piece; } else empty += 1;
      }
      if (empty) rank += empty;
      ranks.push(rank);
    }
    const rights = Object.entries(this.castling).filter(([, value]) => value).map(([key]) => key).join("") || "-";
    return `${ranks.join("/")} ${this.turn} ${rights} ${this.enPassant === null ? "-" : squareOf(this.enPassant)} 0 ${Math.floor(this.moves.length / 2) + 1}`;
  }
}

export const boardUtils = { FILES, RANKS, colorOf, typeOf, squareOf, indexFromSquare, opposite };
