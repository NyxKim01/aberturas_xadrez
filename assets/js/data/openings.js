const stat = (white, draw, black) => ({ white, draw, black });

export const OPENINGS = [
  {
    id: "ruy-lopez",
    eco: "C60",
    name: "Ruy Lopez",
    family: "Jogo aberto",
    description: "Pressiona o cavalo que sustenta e5 e transforma desenvolvimento em pressão de longo prazo.",
    moves: ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
    san: ["1. e4", "e5", "2. Cf3", "Cc6", "3. Bb5"],
    stats: stat(35, 31, 34), sample: "referência: 2,1 mi partidas", trend: [50, 50, 50, 51, 51, 50, 51, 52, 51],
    variations: [
      { name: "Defesa Morphy", moves: "a6 4. Ba4 Cf6 5. O-O Be7", stats: stat(35, 32, 33), white: 52 },
      { name: "Ataque Worrall", moves: "a6 4. Ba4 Cf6 5. De2", stats: stat(38, 29, 33), white: 54 },
      { name: "Defesa Berlim", moves: "3... Cf6 4. O-O Cxe4", stats: stat(33, 38, 29), white: 52 },
    ],
  },
  {
    id: "italian-game",
    eco: "C50",
    name: "Jogo Italiano",
    family: "Jogo aberto",
    description: "Uma rota direta para desenvolvimento, centro e ataques rápidos contra f7.",
    moves: ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"],
    san: ["1. e4", "e5", "2. Cf3", "Cc6", "3. Bc4", "Bc5"],
    stats: stat(37, 29, 34), sample: "referência: 1,8 mi partidas", trend: [50, 50, 51, 51, 53, 51, 52, 52, 51],
    variations: [
      { name: "Giuoco Piano", moves: "4. c3 Cf6 5. d3", stats: stat(36, 31, 33), white: 52 },
      { name: "Ataque Fígado Frito", moves: "4. Cg5 d5 5. exd5", stats: stat(43, 18, 39), white: 53 },
      { name: "Evans Gambit", moves: "4. b4 Bxb4 5. c3", stats: stat(41, 20, 39), white: 51 },
    ],
  },
  {
    id: "scotch-game",
    eco: "C45",
    name: "Jogo Escocês",
    family: "Jogo aberto",
    description: "Troca cedo no centro para abrir linhas e reduzir a pressão lenta da Ruy Lopez.",
    moves: ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4", "e5d4"],
    san: ["1. e4", "e5", "2. Cf3", "Cc6", "3. d4", "exd4"],
    stats: stat(38, 27, 35), sample: "referência: 760 mil partidas", trend: [50, 50, 50, 51, 54, 52, 53, 52, 52],
    variations: [
      { name: "Scotch clássico", moves: "4. Cxd4 Bc5 5. Be3", stats: stat(38, 29, 33), white: 53 },
      { name: "Gambito Escocês", moves: "4. Bc4 Bc5 5. c3", stats: stat(41, 22, 37), white: 52 },
      { name: "Defesa Steinitz", moves: "4. Cxd4 Dh4", stats: stat(42, 21, 37), white: 55 },
    ],
  },
  {
    id: "sicilian-defense",
    eco: "B20",
    name: "Defesa Siciliana",
    family: "Semiaberta",
    description: "As pretas recusam a simetria e criam um desequilíbrio imediato com pressão na coluna c.",
    moves: ["e2e4", "c7c5"],
    san: ["1. e4", "c5"],
    stats: stat(35, 28, 37), sample: "referência: 3,4 mi partidas", trend: [50, 49, 48, 49, 50, 49, 48, 49, 48],
    variations: [
      { name: "Najdorf", moves: "2. Cf3 d6 3. d4 cxd4 4. Cxd4 Cf6 5. Cc3 a6", stats: stat(34, 26, 40), white: 47 },
      { name: "Dragão", moves: "2. Cf3 Cc6 3. d4 cxd4 4. Cxd4 g6", stats: stat(36, 25, 39), white: 49 },
      { name: "Alapin", moves: "2. c3 d5 3. exd5 Dxd5", stats: stat(38, 29, 33), white: 52 },
    ],
  },
  {
    id: "french-defense",
    eco: "C00",
    name: "Defesa Francesa",
    family: "Semifechada",
    description: "Uma estrutura sólida em e6 que questiona o centro branco no momento certo.",
    moves: ["e2e4", "e7e6"],
    san: ["1. e4", "e6"],
    stats: stat(36, 30, 34), sample: "referência: 1,3 mi partidas", trend: [50, 50, 49, 50, 51, 50, 51, 50, 50],
    variations: [
      { name: "Avanço", moves: "2. d4 d5 3. e5", stats: stat(37, 28, 35), white: 51 },
      { name: "Tarrasch", moves: "2. d4 d5 3. Cd2", stats: stat(38, 30, 32), white: 53 },
      { name: "Winawer", moves: "2. d4 d5 3. Cc3 Bb4", stats: stat(37, 27, 36), white: 50 },
    ],
  },
  {
    id: "caro-kann",
    eco: "B10",
    name: "Defesa Caro-Kann",
    family: "Semifechada",
    description: "As pretas apoiam d5 sem bloquear o bispo de casas claras — uma maré paciente e resistente.",
    moves: ["e2e4", "c7c6"],
    san: ["1. e4", "c6"],
    stats: stat(37, 31, 32), sample: "referência: 1,1 mi partidas", trend: [50, 50, 51, 52, 51, 52, 52, 53, 52],
    variations: [
      { name: "Avanço", moves: "2. d4 d5 3. e5", stats: stat(39, 27, 34), white: 53 },
      { name: "Clássica", moves: "2. d4 d5 3. Cc3 dxe4 4. Cxe4 Bf5", stats: stat(36, 32, 32), white: 52 },
      { name: "Panov", moves: "2. exd5 cxd5 3. d4", stats: stat(38, 29, 33), white: 53 },
    ],
  },
  {
    id: "pirc-defense",
    eco: "B07",
    name: "Defesa Pirc",
    family: "Hipermoderna",
    description: "As pretas deixam o centro avançar para atacá-lo depois com peças fianchetadas.",
    moves: ["e2e4", "d7d6", "d2d4", "g8f6"],
    san: ["1. e4", "d6", "2. d4", "Cf6"],
    stats: stat(39, 27, 34), sample: "referência: 430 mil partidas", trend: [50, 50, 52, 52, 54, 53, 52, 53, 52],
    variations: [
      { name: "Ataque Austríaco", moves: "3. Cc3 g6 4. f4", stats: stat(42, 22, 36), white: 54 },
      { name: "Clássica", moves: "3. Cc3 g6 4. Cf3", stats: stat(39, 29, 32), white: 54 },
      { name: "Sistema 150", moves: "3. Cc3 g6 4. Be3", stats: stat(41, 24, 35), white: 53 },
    ],
  },
  {
    id: "queens-gambit",
    eco: "D06",
    name: "Gambito da Dama",
    family: "Jogo de dama",
    description: "Um peão oferecido para construir um centro durável e conquistar espaço nas alas.",
    moves: ["d2d4", "d7d5", "c2c4"],
    san: ["1. d4", "d5", "2. c4"],
    stats: stat(39, 34, 27), sample: "referência: 2,5 mi partidas", trend: [50, 51, 51, 53, 53, 54, 53, 54, 54],
    variations: [
      { name: "Gambito Recusado", moves: "e6 3. Cc3 Cf6 4. Bg5", stats: stat(38, 36, 26), white: 56 },
      { name: "Eslava", moves: "c6 3. Cf3 Cf6 4. Cc3", stats: stat(37, 35, 28), white: 55 },
      { name: "Aceito", moves: "dxc4 3. Cf3 Cf6 4. e3", stats: stat(42, 31, 27), white: 57 },
    ],
  },
  {
    id: "london-system",
    eco: "D02",
    name: "Sistema Londres",
    family: "Jogo de dama",
    description: "Uma configuração previsível e prática, focada em desenvolvimento estável e planos claros.",
    moves: ["d2d4", "d7d5", "c1f4"],
    san: ["1. d4", "d5", "2. Bf4"],
    stats: stat(40, 32, 28), sample: "referência: 970 mil partidas", trend: [50, 51, 52, 54, 54, 55, 55, 54, 55],
    variations: [
      { name: "Londres clássico", moves: "Cf6 3. e3 e6 4. Bd3", stats: stat(39, 33, 28), white: 55 },
      { name: "Ataque Jobava", moves: "Cf6 3. Cc3", stats: stat(43, 25, 32), white: 55 },
      { name: "Londres com c3", moves: "Cf6 3. c3", stats: stat(40, 30, 30), white: 55 },
    ],
  },
  {
    id: "kings-indian",
    eco: "E60",
    name: "Defesa Índia do Rei",
    family: "Hipermoderna",
    description: "As pretas aceitam menos espaço para lançar um contra-ataque intenso contra o rei branco.",
    moves: ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"],
    san: ["1. d4", "Cf6", "2. c4", "g6", "3. Cc3", "Bg7"],
    stats: stat(38, 25, 37), sample: "referência: 1,2 mi partidas", trend: [50, 50, 51, 50, 52, 50, 49, 50, 49],
    variations: [
      { name: "Clássica", moves: "4. e4 d6 5. Cf3 O-O", stats: stat(39, 25, 36), white: 51 },
      { name: "Sämisch", moves: "4. e4 d6 5. f3", stats: stat(42, 23, 35), white: 53 },
      { name: "Fianchetto", moves: "4. Cf3 O-O 5. g3", stats: stat(37, 30, 33), white: 52 },
    ],
  },
  {
    id: "nimzo-indian",
    eco: "E20",
    name: "Defesa Nimzo-Índia",
    family: "Hipermoderna",
    description: "O bispo em b4 pressiona a estrutura branca e cria decisões estratégicas desde cedo.",
    moves: ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"],
    san: ["1. d4", "Cf6", "2. c4", "e6", "3. Cc3", "Bb4"],
    stats: stat(36, 35, 29), sample: "referência: 880 mil partidas", trend: [50, 50, 51, 52, 51, 53, 54, 53, 54],
    variations: [
      { name: "Rubinstein", moves: "4. e3 O-O 5. Bd3", stats: stat(36, 36, 28), white: 54 },
      { name: "Sämisch", moves: "4. a3 Bxc3+ 5. bxc3", stats: stat(40, 29, 31), white: 55 },
      { name: "Clássica", moves: "4. Dc2 O-O 5. a3", stats: stat(38, 32, 30), white: 55 },
    ],
  },
  {
    id: "grunfeld-defense",
    eco: "D70",
    name: "Defesa Grünfeld",
    family: "Hipermoderna",
    description: "Uma escolha dinâmica: as pretas atacam o centro de peões com máxima atividade.",
    moves: ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5"],
    san: ["1. d4", "Cf6", "2. c4", "g6", "3. Cc3", "d5"],
    stats: stat(37, 27, 36), sample: "referência: 590 mil partidas", trend: [50, 50, 51, 50, 50, 48, 49, 48, 49],
    variations: [
      { name: "Sistema Russo", moves: "4. cxd5 Cxd5 5. e4", stats: stat(39, 26, 35), white: 51 },
      { name: "Fianchetto", moves: "4. Cf3 Bg7 5. g3", stats: stat(36, 32, 32), white: 52 },
      { name: "Variante das trocas", moves: "4. cxd5 Cxd5 5. Bd2", stats: stat(38, 28, 34), white: 51 },
    ],
  },
  {
    id: "english-opening",
    eco: "A20",
    name: "Abertura Inglesa",
    family: "Flanco",
    description: "O peão c controla d5 e prepara uma luta flexível pelo centro à distância.",
    moves: ["c2c4"],
    san: ["1. c4"],
    stats: stat(39, 34, 27), sample: "referência: 1,5 mi partidas", trend: [50, 52, 52, 53, 54, 54, 55, 54, 55],
    variations: [
      { name: "Siciliana Reversa", moves: "e5 2. Cc3 Cf6 3. g3", stats: stat(40, 31, 29), white: 55 },
      { name: "Simétrica", moves: "c5 2. Cc3 Cc6 3. g3", stats: stat(38, 35, 27), white: 55 },
      { name: "Anglo-Índia", moves: "Cf6 2. Cc3 e6 3. Cf3", stats: stat(39, 34, 27), white: 55 },
    ],
  },
  {
    id: "reti-opening",
    eco: "A04",
    name: "Abertura Réti",
    family: "Flanco",
    description: "Um convite flexível: as brancas desenvolvem antes de revelar a estrutura central.",
    moves: ["g1f3"],
    san: ["1. Cf3"],
    stats: stat(40, 35, 25), sample: "referência: 640 mil partidas", trend: [50, 52, 53, 54, 54, 55, 55, 56, 55],
    variations: [
      { name: "Réti clássica", moves: "d5 2. c4", stats: stat(40, 34, 26), white: 56 },
      { name: "Índia do Rei Reversa", moves: "Cf6 2. g3 g6 3. Bg2", stats: stat(39, 36, 25), white: 56 },
      { name: "Transposição Catalã", moves: "d5 2. d4", stats: stat(40, 35, 25), white: 56 },
    ],
  },
  {
    id: "vienna-game",
    eco: "C25",
    name: "Jogo Vienense",
    family: "Jogo aberto",
    description: "Desenvolvimento ativo do cavalo c e a possibilidade de avançar f4 para um ataque imediato.",
    moves: ["e2e4", "e7e5", "b1c3"],
    san: ["1. e4", "e5", "2. Cc3"],
    stats: stat(41, 26, 33), sample: "referência: 350 mil partidas", trend: [50, 50, 52, 53, 54, 55, 54, 55, 54],
    variations: [
      { name: "Gambito Vienense", moves: "Cf6 3. f4", stats: stat(44, 18, 38), white: 53 },
      { name: "Jogo lento", moves: "Cc6 3. Cf3", stats: stat(40, 29, 31), white: 55 },
      { name: "Frankenstein–Drácula", moves: "Cc6 3. Bc4 Cf6 4. d3", stats: stat(42, 21, 37), white: 53 },
    ],
  },
  {
    id: "scandinavian-defense",
    eco: "B01",
    name: "Defesa Escandinava",
    family: "Semiaberta",
    description: "As pretas desafiam e4 já no primeiro gesto, aceitando expor a dama por atividade.",
    moves: ["e2e4", "d7d5"],
    san: ["1. e4", "d5"],
    stats: stat(40, 25, 35), sample: "referência: 420 mil partidas", trend: [50, 50, 53, 52, 53, 54, 53, 54, 53],
    variations: [
      { name: "Principal", moves: "2. exd5 Dxd5 3. Cc3", stats: stat(42, 24, 34), white: 54 },
      { name: "Moderna", moves: "2. exd5 Cf6 3. d4", stats: stat(40, 27, 33), white: 54 },
      { name: "Gambito Islandês", moves: "2. exd5 Cf6 3. c4 e6", stats: stat(43, 19, 38), white: 53 },
    ],
  },
];

export const OPENING_FAMILIES = ["Todas", ...new Set(OPENINGS.map((opening) => opening.family))];

export function findOpeningById(id) {
  return OPENINGS.find((opening) => opening.id === id) ?? OPENINGS[0];
}

export function matchOpening(moveList) {
  if (!moveList.length) return null;
  return OPENINGS
    .filter((opening) => opening.moves.length <= moveList.length)
    .filter((opening) => opening.moves.every((move, index) => moveList[index] === move))
    .sort((a, b) => b.moves.length - a.moves.length)[0] ?? null;
}

export function openingContinuation(moveList) {
  const candidates = OPENINGS
    .filter((opening) => moveList.length < opening.moves.length)
    .filter((opening) => moveList.every((move, index) => opening.moves[index] === move))
    .sort((a, b) => a.moves.length - b.moves.length);
  return candidates[0] ?? null;
}
