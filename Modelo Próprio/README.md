# Projeto de análise de aberturas de xadrez

Este projeto prepara dados de partidas do Lichess, treina um modelo de previsão de resultado e avalia o modelo treinado.

O fluxo de trabalho é sempre:

1. **Sereia** cria automaticamente os dados de trabalho;
2. **Esponja do Mar** treina e salva o modelo;
3. **Plancton** testa o modelo salvo.

## Requisitos

Use Python 3 e instale as dependências:

```bash
pip install -r requirements.txt
```

Para executar a interface da Sereia, também é necessário o PyQt5:

```bash
pip install PyQt5
```

Para treinar e testar o modelo, instale também as bibliotecas de análise e aprendizado de máquina usadas pelos scripts:

```bash
pip install pandas numpy scikit-learn xgboost lightgbm optuna joblib
```

Também é necessário baixar um banco de partidas do Lichess no formato `.pgn.zst`.

## 1. Criar os dados com a Sereia

Execute:

```bash
python sereia.py
```

Na interface:

1. Selecione o arquivo `.pgn.zst` baixado do Lichess.
2. Defina a quantidade de partidas a processar e, se desejar, os filtros de rating.
3. Clique para iniciar o pipeline.

A Sereia executa automaticamente as etapas de extração, organização e conversão. Ao terminar, o projeto terá os principais arquivos e pastas abaixo:

```text
partidas_filtradas.pgn       # partidas extraídas do arquivo compactado
aberturas_organizadas/       # PGNs separados por abertura
aberturas_csv/               # dados prontos para treinamento
```

> Arquivos `.pgn.zst` podem ser muito grandes. Comece com uma quantidade menor de partidas para validar o fluxo.

## 2. Criar o modelo com a Esponja do Mar

Com a pasta `aberturas_csv/` criada pela Sereia, execute:

```bash
python esponja_do_mar.py
```

O script lê os CSVs, prepara as variáveis das partidas, treina e compara os modelos configurados e salva o melhor resultado em:

```text
modelo_arvore_campeao.pkl
```

Esse arquivo contém o modelo vencedor e os artefatos necessários para reutilizá-lo no teste.

## 3. Testar o modelo com o Plancton

Após gerar `modelo_arvore_campeao.pkl`, execute:

```bash
python plancton.py
```

O Plancton carrega o modelo salvo e os dados em `aberturas_csv/`, então exibe métricas como acurácia, relatório de classificação, matriz de confusão e log loss quando disponível.

## Resumo rápido

```bash
# 1. Gerar automaticamente os dados pela interface
python sereia.py

# 2. Treinar e salvar o modelo
python esponja_do_mar.py

# 3. Avaliar o modelo salvo
python plancton.py
```

## Arquivos principais

| Arquivo | Responsabilidade |
| --- | --- |
| `sereia.py` | Interface que orquestra a preparação automática dos dados. |
| `nemo.py` | Extrai e filtra partidas do arquivo `.pgn.zst`. |
| `estrela_do_mar.py` | Separa as partidas por abertura. |
| `cavalo_marinho.py` | Converte os PGNs organizados em arquivos CSV. |
| `esponja_do_mar.py` | Treina e salva o modelo. |
| `plancton.py` | Testa e apresenta as métricas do modelo salvo. |
