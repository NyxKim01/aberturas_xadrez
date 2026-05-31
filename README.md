# 🌊🐚 Projeto Estrela do Mar — Explorando as Profundezas das Aberturas

Bem-vindo, mergulhador.  
Este projeto é como um oceano de partidas de xadrez — vasto, profundo e cheio de padrões escondidos. Sua missão é explorar esse mar de dados e organizar cada corrente (abertura) em seu próprio recife.

Ao final da jornada, você terá:

📂 Uma pasta principal  
└── 🌊 Várias subpastas (uma para cada abertura)  
  └── ♟️ Arquivos `.pgn` individuais de cada partida  

---

## 🐠 O Que Este Projeto Faz

A partir de um enorme banco de partidas do Lichess, o código:

- Converte arquivos compactados (`.pgn.zst`) em `.pgn`
- Filtra um número menor de partidas (para não afundar seu computador)
- Separa cada partida por abertura
- Organiza tudo em pastas automaticamente

---

## 🐳 Passo a Passo (A Jornada Submarina)

### 1️⃣ Preparar o Equipamento

Instale as dependências necessárias:

pip install -r requirements.txt

---

### 2️⃣ Baixar o Tesouro do Lichess

Escolha um banco de partidas no site do Lichess e baixe um arquivo:

arquivo.pgn.zst

Esses arquivos são enormes (tipo um oceano inteiro), então escolha com sabedoria.

---

### 3️⃣ Emergir com Dados Úteis (`nemo.py` 🐟)

Use o script `nemo.py` para:

- Converter `.zst` → `.pgn`
- Limitar a quantidade de partidas (ex: 100000)

python nemo.py arquivo.pgn.zst

Você obterá um novo arquivo `.pgn` menor e mais manejável.

---

### 4️⃣ Organizar o Oceano (`estrela_do_mar.py` ⭐)

Agora vem a mágica.

Execute:

python estrela_do_mar.py arquivo_reduzido.pgn

O script irá:

- Identificar a abertura de cada partida
- Criar uma pasta para cada abertura
- Salvar cada partida individualmente dentro da sua respectiva pasta

---

## 🐚 Estrutura Final

aberturas/
├── Sicilian Defense/
│   ├── partida_1.pgn
│   ├── partida_2.pgn
│   └── ...
├── French Defense/
│   ├── partida_1.pgn
│   └── ...
└── ...

---

## ⚠️ Avisos de Mergulho

- Arquivos `.zst` são **gigantescos** — não tente processar tudo de uma vez
- Use limites (ex: 100k partidas) para evitar travamentos
- O tempo de execução pode variar dependendo do tamanho do arquivo

---

## 🌊 Considerações Finais

Assim como o oceano, o xadrez guarda padrões profundos esperando para serem descobertos.  
Este projeto transforma caos em estrutura — um verdadeiro mapa do fundo do mar das aberturas.

Boa exploração, capitão. 🐙🐙
