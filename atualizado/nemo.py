import zstandard as zstd
import io
import re
import random
from collections import defaultdict

def processar_jogo(buffer_jogo, w_elo, b_elo, eco, max_dif, usar_prob, cont_elo, cont_eco):
    if w_elo is None or b_elo is None:
        return False 
    if abs(w_elo - b_elo) > max_dif:
        return False 
    if usar_prob:
        if not eco: 
            return False 
        faixa_elo = ((w_elo + b_elo) // 2) // 100
        freq_elo = cont_elo[faixa_elo]
        freq_eco = cont_eco[eco]
        probabilidade = 1.0 / (1.0 + (0.01 * freq_elo) + (0.05 * freq_eco))
        if random.random() > probabilidade:
            return False 
        cont_elo[faixa_elo] += 1
        cont_eco[eco] += 1
    return True

def extrair_partidas_zst(caminho_entrada, caminho_saida, limite_partidas=10000, max_dif_rating=200, usar_probabilidade=False):
    print(f"🐠 [Nemo] Extraindo até {limite_partidas} partidas...")
    print(f"   ↳ Max Dif. Rating: {max_dif_rating} | Modelo Uniforme: {'Ativo' if usar_probabilidade else 'Inativo'}")
    elo_regex = re.compile(r'\[(White|Black)Elo "(\d+)"\]')
    eco_regex = re.compile(r'\[ECO "([^"]+)"\]')
    contagem_elo = defaultdict(int)
    contagem_eco = defaultdict(int)
    dctx = zstd.ZstdDecompressor()
    with open(caminho_entrada, 'rb') as arquivo_comprimido:
        with dctx.stream_reader(arquivo_comprimido) as leitor_stream:
            stream_texto = io.TextIOWrapper(leitor_stream, encoding='utf-8')
            with open(caminho_saida, 'w', encoding='utf-8') as arquivo_saida:
                contador_partidas = 0
                jogo_buffer = []
                w_elo = b_elo = eco = None
                for linha in stream_texto:
                    if linha.startswith("[Event "):
                        if jogo_buffer:
                            aceito = processar_jogo(jogo_buffer, w_elo, b_elo, eco, max_dif_rating, usar_probabilidade, contagem_elo, contagem_eco)
                            if aceito:
                                arquivo_saida.writelines(jogo_buffer)
                                contador_partidas += 1
                                if contador_partidas % 1000 == 0:
                                    print(f"🐠 [Nemo] {contador_partidas} partidas filtradas e escritas...")
                                if contador_partidas >= limite_partidas:
                                    break
                        jogo_buffer = [linha]
                        w_elo = b_elo = eco = None
                    else:
                        jogo_buffer.append(linha)
                        if linha.startswith("[WhiteElo"):
                            m = elo_regex.search(linha)
                            if m: w_elo = int(m.group(2))
                        elif linha.startswith("[BlackElo"):
                            m = elo_regex.search(linha)
                            if m: b_elo = int(m.group(2))
                        elif linha.startswith("[ECO"):
                            m = eco_regex.search(linha)
                            if m: eco = m.group(1)
                if jogo_buffer and contador_partidas < limite_partidas:
                    if processar_jogo(jogo_buffer, w_elo, b_elo, eco, max_dif_rating, usar_probabilidade, contagem_elo, contagem_eco):
                        arquivo_saida.writelines(jogo_buffer)
                        contador_partidas += 1
    print(f"🐠 [Nemo] Sucesso! {contador_partidas} partidas empacotadas de acordo com os filtros de qualidade.")

if __name__ == "__main__":
    extrair_partidas_zst("arquivo.pgn.zst", "teste.pgn", 1000, 150, True)