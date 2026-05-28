import chess.pgn
import csv
import io
import multiprocessing as mp
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# CONFIGURAÇÃO VARIÁVEIS DE AMBIENTE, CONSTANTES E VARIÁVEIS GLOBAIS
load_dotenv()
DIRETORIO_SCRIPT = Path(__file__).resolve().parent

# O default é o nome gerado pelo "estrela_do_mar", considerando que a pasta e o script "PGNtoCSV" estejam na mesma pasta
env_pasta_PGNs = os.getenv("PASTA_PGNS", "")
PASTA_PGNS = env_pasta_PGNs if not env_pasta_PGNs == "" else DIRETORIO_SCRIPT / "aberturas_organizadas"

# O default considera que a pasta "aberturas_csv" deve ser criada no mesmo diretório do script
env_path_nova_pasta = os.getenv("LOCAL_NOVA_PASTA_CSV", "")
BASE_SAIDA = Path(env_path_nova_pasta) if not env_path_nova_pasta == "" else DIRETORIO_SCRIPT

ARQUIVO_CSV = " - dataset_treinamento.csv"

NUM_CORES = mp.cpu_count()
FREQ_LOG = 1000 

total_partidas_global = 0

# Método que recebe o PGN de uma partida e retorna array com os dados prontos para serem escritos em CSV
def processar_uma_partida(game_text):
    rows = []
    game = chess.pgn.read_game(io.StringIO(game_text))
    
    if game is None:
        return rows

    # Checa se existe informação de resultado (e se a notação está correta)
    res_str = game.headers.get("Result", "*")
    if res_str not in ["1-0", "0-1", "1/2-1/2"]:
        return rows

    # Checa se existe informação de rating
    w_rat = game.headers.get("WhiteElo")
    b_rat = game.headers.get("BlackElo")
    if not w_rat or not b_rat:
        return rows
    
    # Checa se existe informação de abertura
    opening = game.headers.get("Opening")
    if not opening:
        return rows

    # Converte string em valors numéricos
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
    
    del board
    del game
    return rows

# Função geradora que abre um arquivo .PGN e extrai todas as partidas nele contidas.    
def extrair_partidas_brutas(file_path):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        game_content = []
        for line in f:
            # Condição para caso hajam várias partidas em um único .PGN
            if line.startswith("[Event ") and game_content:
                yield "".join(game_content)
                game_content = []
            game_content.append(line)
        if game_content:
            yield "".join(game_content)

# Função geradora que abre uma pasta com N arquivos .PGN e extrai todas as partidas contidas na pasta inteira
def extrair_PGN(folder_iterable):
    for pgn in folder_iterable:
        if not pgn.is_file() or not pgn.suffix.lower() == ".pgn": continue
        yield from extrair_partidas_brutas(pgn)

# Função principal que gera os .CSVs a partir dos .PGNs
def gera_CSV(folder, nome_abertura, pool):
    start_time = time.time()
    total_partidas = 0

    pasta_abertura = BASE_SAIDA / "aberturas_csv"
    pasta_abertura.mkdir(exist_ok=True)
    nome_arquivo_csv =  f"{nome_abertura}{ARQUIVO_CSV}"
    csv_path = pasta_abertura / nome_arquivo_csv
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as csv_out:
        print(f"PROCESSO INICIADO - {nome_abertura}")
        print(f"arquivo de saída: {csv_path}")
        
        escritor = csv.writer(csv_out)
        escritor.writerow(["fen", "move_no", "w_rating", "b_rating", "result", "opening"])

        # Uso de pool de processamento para otimizar a velocidade do script com paralelismo
        for resultado_partida in pool.imap_unordered(processar_uma_partida, extrair_PGN(folder), chunksize=50):
            if resultado_partida:
                escritor.writerows(resultado_partida)
                total_partidas += 1
            
            # Feedback durante execução de quantas partidas foram processadas + velocidade de processamento
            if total_partidas % FREQ_LOG == 0 and total_partidas > 0:
                elapsed = time.time() - start_time
                velocidade_processamento = total_partidas / elapsed
                print(f"{total_partidas} partidas processadas... | Velocidade: {velocidade_processamento:.2f} partidas/seg")
    
    elapsed = time.time() - start_time
    print(f"PROCESSO FINALIZADO - {nome_abertura}")
    print(f"Tempo decorrido: {elapsed:.2f}")
    print(f"Partidas analisadas: {total_partidas}")
    print("="*16)

    global total_partidas_global
    total_partidas_global += total_partidas


def main():
    start_time_main = time.time()
    root = Path(PASTA_PGNS)
    
    # Cria pool de processos e itera pelas pastas com aberturas
    with mp.Pool(processes=NUM_CORES) as pool:
        for pasta_abertura in root.iterdir():
            if not pasta_abertura.is_dir(): continue
            gera_CSV(pasta_abertura.iterdir(), pasta_abertura.name, pool)
            

    print(f"TEMPO TOTAL DO PROGRAMA: {timedelta(seconds=int(time.time() - start_time_main))}")
            

if __name__ == "__main__":
    main()