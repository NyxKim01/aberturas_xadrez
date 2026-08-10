# 🐚 Maré de Aberturas

> Um laboratório de xadrez com cheiro de água salgada: mova no tabuleiro, veja a posição ser avaliada e descubra por quais aberturas sua partida está navegando.

![Licença do Stockfish compatível](https://img.shields.io/badge/Stockfish-opcional-64e2d3?style=flat-square)
![Sem etapa de build](https://img.shields.io/badge/build-n%C3%A3o%20necess%C3%A1rio-ff9d8d?style=flat-square)

## O que existe aqui

- Tabuleiro interativo com movimentos legais, captura en passant, roque, promoção automática para dama, xeque e desfazer lance.
- Identificação de abertura a partir da **sequência de lances**, não de uma posição visualmente parecida.
- Probabilidade de vitória/empate/derrota atualizada em cada posição — inclusive fora do livro de aberturas.
- Dois níveis de análise:
  - **Maré Neural**: estimativa local imediata, baseada em material, centro, desenvolvimento e segurança do rei.
  - **Stockfish 18 leve**: carregado sob demanda pelo botão da interface; a avaliação UCI substitui a estimativa local quando disponível.
- “Árvore de coral” com a sequência que o usuário criou e indicação de uma próxima corrente conhecida.
- Atlas de estudo com 16 aberturas, linhas clicáveis, comparativo de resultados e gráfico de mudança da expectativa ao longo dos lances.
- Visual inteiramente novo: oceano escuro, corais, bolhas, tipografia arredondada e componentes responsivos.

## Rodar localmente

O projeto é estático, não tem dependências instaláveis e não exige build. Basta ter Node.js.

```bash
npm run serve
```

No PowerShell com execução de scripts bloqueada, use o equivalente `npm.cmd run serve`.

Depois, abra [http://localhost:4173](http://localhost:4173). Use um servidor local em vez de abrir o HTML diretamente: isso permite que módulos JavaScript e o Worker do Stockfish funcionem corretamente.

## Rotas

| Página | Endereço | Para quê |
| --- | --- | --- |
| Explorar | `/index.html` | Jogar no tabuleiro e analisar qualquer posição. |
| Atlas | `/estudos.html` | Comparar aberturas, linhas e tendências de probabilidade. |

No atlas, o botão **“Experimentar no tabuleiro”** leva a linha-base da abertura para o tabuleiro. Por exemplo:

```text
/index.html?line=e2e4,e7e5,g1f3,b8c6,f1b5
```

## Como as previsões funcionam

### Posição livre

Todo lance legal pode ser analisado. Antes de ativar o Stockfish, a Maré Neural gera uma avaliação em centipeões e a transforma em três probabilidades. Ela é útil como resposta instantânea, mas não deve ser tratada como motor competitivo ou garantia de resultado.

Ao tocar em **“Ativar Stockfish profundo”**, o site inicia a cópia local, leve e single-threaded do Stockfish 18 e pede uma busca UCI de profundidade 13 para a posição atual. A busca roda em um Web Worker para não congelar o tabuleiro. O motor também fornece a própria tabela WDL, usada para atualizar as três probabilidades com dados da análise em vez de uma aproximação visual.

### Aberturas e estatísticas do atlas

`assets/js/data/openings.js` contém um pequeno atlas editorial, criado para demonstrar o produto. Os percentuais e amostras da página de estudo são **dados de referência de demonstração**: servem para comparação visual, e não são uma alegação de uma base estatística reproduzível.

Para produção, substitua esse arquivo por um pipeline que agregue PGNs (por ECO, rating, controle de tempo e data) e publique a mesma estrutura:

```js
{
  id: "ruy-lopez",
  eco: "C60",
  name: "Ruy Lopez",
  moves: ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
  stats: { white: 35, draw: 31, black: 34 },
  variations: [{ name: "Defesa Morphy", stats: { white: 35, draw: 32, black: 33 } }]
}
```

Assim, a resposta a “qual abertura tem mais chance?” passa a ser auditável e pode ser filtrada pela população que importa para você.

## Estrutura

```text
.
├── index.html                         # Laboratório do tabuleiro
├── estudos.html                       # Atlas de estudo
├── assets/
│   ├── css/
│   │   └── theme.css                  # Tema submarino e responsividade
│   └── js/
│       ├── app.js                     # Interface do tabuleiro
│       ├── study.js                   # Filtros, atlas e gráfico
│       ├── core/
│       │   ├── chess-game.js          # Regras e estado do tabuleiro
│       │   └── position-evaluator.js  # Avaliador local + ponte Stockfish
│       └── data/
│           └── openings.js            # Livro de aberturas e linhas
├── THIRD_PARTY_NOTICES.md
└── README.md
```

## Personalização rápida

- **Visual**: altere as variáveis no início de `assets/css/theme.css`.
- **Livro de aberturas**: edite ou substitua `assets/js/data/openings.js`.
- **Profundidade do motor**: em `assets/js/core/position-evaluator.js`, troque `go depth 13` por uma profundidade apropriada ao seu público e orçamento de CPU.
- **Motor local/produção**: os arquivos `.js` e `.wasm` do Stockfish já ficam em `assets/vendor/stockfish/`. Mantenha-os juntos, pois o Worker encontra o WASM pelo mesmo caminho.

## Notas de licença

O projeto inclui a versão leve, single-threaded, do [nmrugg/stockfish.js](https://github.com/nmrugg/stockfish.js), distribuída sob GPL-3.0. Ao redistribuir o projeto, preserve os avisos, disponibilize o código-fonte correspondente e cumpra as obrigações da licença. Veja também [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

Feito para explorar, não para decorar. ♟️🌊
