import chess.pgn
import csv
import io
import multiprocessing as mp
import time
import os
from pathlib import Path
from datetime import timedelta

ARQUIVO_CSV = " - dataset_treinamento.csv"
NUM_CORES = mp.cpu_count()
FREQ_LOG = 1000 

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

def gera_CSV(folder, nome_abertura, pool, base_saida):
    start_time = time.time()
    total_partidas = 0
    pasta_abertura = Path(base_saida) / "aberturas_csv"
    pasta_abertura.mkdir(exist_ok=True)
    nome_arquivo_csv =  f"{nome_abertura}{ARQUIVO_CSV}"
    csv_path = pasta_abertura / nome_arquivo_csv
    with open(csv_path, 'w', encoding='utf-8', newline='') as csv_out:
        print(f"🐎 [Cavalo Marinho] Processando: {nome_abertura}...")
        escritor = csv.writer(csv_out)
        escritor.writerow(["fen", "move_no", "w_rating", "b_rating", "result", "opening"])
        for resultado_partida in pool.imap_unordered(processar_uma_partida, extrair_PGN(folder), chunksize=50):
            if resultado_partida:
                escritor.writerows(resultado_partida)
                total_partidas += 1
            if total_partidas % FREQ_LOG == 0 and total_partidas > 0:
                pass 
    elapsed = time.time() - start_time
    print(f"🐎 [Cavalo Marinho] Finalizado {nome_abertura} | Partidas: {total_partidas} | Tempo: {elapsed:.2f}s")
    return total_partidas

def processar_para_csv(pasta_pgns, base_saida):
    print(f"🐎 [Cavalo Marinho] Iniciando conversão para CSV com {NUM_CORES} núcleos...")
    start_time_main = time.time()
    root = Path(pasta_pgns)
    total_global = 0
    if not root.exists():
        print("❌ Diretório de aberturas não encontrado!")
        return
    with mp.Pool(processes=NUM_CORES) as pool:
        for pasta_abertura in root.iterdir():
            if not pasta_abertura.is_dir(): continue
            total_global += gera_CSV(pasta_abertura.iterdir(), pasta_abertura.name, pool, base_saida)   
    print(f"🐎 [Cavalo Marinho] TOTAL DE PARTIDAS EM CSV: {total_global}")
    print(f"🐎 [Cavalo Marinho] TEMPO TOTAL CSV: {timedelta(seconds=int(time.time() - start_time_main))}")

if __name__ == "__main__":
    processar_para_csv("aberturas_organizadas", ".")