import chess.pgn
import csv
import io
import multiprocessing as mp
import time
import os
import json 
from pathlib import Path
from datetime import timedelta

ARQUIVO_CSV = " - dataset_treinamento.csv"
ARQUIVO_CONTROLE = "controle_aberturas.json"
NUM_CORES = mp.cpu_count()
FREQ_LOG = 1000 
TETO_PARTIDAS_ABERTURA = 500

def processar_uma_partida(game_text):
    rows = []
    game = chess.pgn.read_game(io.StringIO(game_text))
    if game is None: return rows
    res_str = game.headers.get("Result", "*")
    if res_str not in ["1-0", "0-1", "1/2-1/2"]: return rows
    w_rat = game.headers.get("WhiteElo")
    b_rat = game.headers.get("BlackElo")
    if not w_rat or not b_rat: return rows
    opening = game.headers.get("Opening")
    if not opening: return rows
    try:
        res_val = 1.0 if res_str == "1-0" else (0.0 if res_str == "0-1" else 0.5)
        w_rat = int(w_rat)
        b_rat = int(b_rat)
    except ValueError:
        return rows
    board = game.board()
    move_count = 0
    for move in game.mainline_moves():
        rows.append([board.fen(), move_count, w_rat, b_rat, res_val, opening])
        board.push(move)
        move_count += 1
    return rows

def extrair_partidas_brutas(file_path):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        game_content = []
        for line in f:
            if line.startswith("[Event ") and game_content:
                yield "".join(game_content)
                game_content = []
            game_content.append(line)
        if game_content:
            yield "".join(game_content)

def extrair_PGN(folder_iterable):
    for pgn in folder_iterable:
        if not pgn.is_file() or not pgn.suffix.lower() == ".pgn": continue
        yield from extrair_partidas_brutas(pgn)

def carregar_controle(base_saida):
    caminho_json = Path(base_saida) / ARQUIVO_CONTROLE
    if caminho_json.exists():
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_controle(base_saida, dados):
    caminho_json = Path(base_saida) / ARQUIVO_CONTROLE
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def gera_CSV(folder, nome_abertura, pool, base_saida, historico_contagem):
    start_time = time.time()
    
    partidas_anteriores = historico_contagem.get(nome_abertura, 0)
    partidas_novas = 0

    if partidas_anteriores >= TETO_PARTIDAS_ABERTURA:
        print(f"🛑 [Teto Histórico Já Atingido] {nome_abertura} já possui {partidas_anteriores} partidas. Pulando...")
        return 0

    pasta_abertura = Path(base_saida) / "aberturas_csv"
    pasta_abertura.mkdir(exist_ok=True)
    nome_arquivo_csv = f"{nome_abertura}{ARQUIVO_CSV}"
    csv_path = pasta_abertura / nome_arquivo_csv
    
    modo_abertura = 'a' if csv_path.exists() else 'w'
    
    with open(csv_path, modo_abertura, encoding='utf-8', newline='') as csv_out:
        escritor = csv.writer(csv_out)
        
        if modo_abertura == 'w':
            print(f"🐎 [Cavalo Marinho] Criando novo CSV para: {nome_abertura}...")
            escritor.writerow(["fen", "move_no", "w_rating", "b_rating", "result", "opening"])
        else:
            print(f"🔄 [Cavalo Marinho] Atualizando CSV existente para: {nome_abertura} (Já tinha {partidas_anteriores} partidas)...")

        for resultado_partida in pool.imap_unordered(processar_uma_partida, extrair_PGN(folder), chunksize=50):
            # Teto dinâmico: soma o que já tinha com o que foi extraído agora
            if (partidas_anteriores + partidas_novas) >= TETO_PARTIDAS_ABERTURA:
                print(f"🛑 [Teto Atingido Agora] {nome_abertura} alcançou o limite de {TETO_PARTIDAS_ABERTURA} no total. Interrompendo...")
                break
                
            if resultado_partida:
                escritor.writerows(resultado_partida)
                partidas_novas += 1
                
    historico_contagem[nome_abertura] = partidas_anteriores + partidas_novas
    
    elapsed = time.time() - start_time
    print(f"   -> {nome_abertura} | Novas: {partidas_novas} | Total Atual: {historico_contagem[nome_abertura]} | Tempo: {elapsed:.2f}s")
    return partidas_novas

def processar_para_csv(pasta_pgns, base_saida):
    print(f"🐎 [Cavalo Marinho] Iniciando conversão para CSV com {NUM_CORES} núcleos...")
    start_time_main = time.time()
    root = Path(pasta_pgns)
    total_novas_global = 0
    
    if not root.exists():
        print("❌ Diretório de aberturas não encontrado!")
        return

    historico_contagem = carregar_controle(base_saida)

    with mp.Pool(processes=NUM_CORES) as pool:
        for pasta_abertura in root.iterdir():
            if not pasta_abertura.is_dir(): continue
            
            total_novas_global += gera_CSV(
                pasta_abertura.iterdir(), 
                pasta_abertura.name, 
                pool, 
                base_saida, 
                historico_contagem
            )
            
            salvar_controle(base_saida, historico_contagem)
            
    print(f"🐎 [Cavalo Marinho] TOTAL DE NOVAS PARTIDAS ADICIONADAS: {total_novas_global}")
    print(f"🐎 [Cavalo Marinho] TEMPO TOTAL CSV: {timedelta(seconds=int(time.time() - start_time_main))}")

if __name__ == "__main__":
    processar_para_csv("aberturas_organizadas", ".")