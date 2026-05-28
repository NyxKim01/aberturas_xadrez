import chess.pgn
import os
import re

def limpar_nome_pasta(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome).strip()

def separar_pgn_por_abertura(caminho_pgn_entrada, diretorio_saida="aberturas_organizadas"):
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
    try:
        with open(caminho_pgn_entrada, "r", encoding="utf-8") as arquivo_pgn:
            contador_jogos = 0
            while True:
                jogo = chess.pgn.read_game(arquivo_pgn)
                if jogo is None:
                    break 
                contador_jogos += 1
                abertura_completa = jogo.headers.get("Opening", "Desconhecida")
                abertura_base = abertura_completa.split(':')[0].split(',')[0].split('#')[0].strip()
                nome_pasta_seguro = limpar_nome_pasta(abertura_base)
                pasta_abertura = os.path.join(diretorio_saida, nome_pasta_seguro)
                if not os.path.exists(pasta_abertura):
                    os.makedirs(pasta_abertura)
                nome_arquivo_jogo = f"jogo_{contador_jogos}.pgn"
                caminho_arquivo_jogo = os.path.join(pasta_abertura, nome_arquivo_jogo)
                with open(caminho_arquivo_jogo, "w", encoding="utf-8") as arquivo_saida:
                    exportador = chess.pgn.FileExporter(arquivo_saida)
                    jogo.accept(exportador)
        print(f"⭐ [Estrela do Mar] Concluído! {contador_jogos} jogos organizados.")
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo '{caminho_pgn_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    arquivo_alvo = "primeiras_10000_partidas.pgn" 
    separar_pgn_por_abertura(arquivo_alvo)