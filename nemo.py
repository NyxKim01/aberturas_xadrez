import zstandard as zstd
import io

def extrair_partidas_zst(caminho_entrada, caminho_saida, limite_partidas=10000):
    print(f"Iniciando a extração de {limite_partidas} partidas...")
    print(f"Lendo de: {caminho_entrada}")
    dctx = zstd.ZstdDecompressor()
    with open(caminho_entrada, 'rb') as arquivo_comprimido:
        with dctx.stream_reader(arquivo_comprimido) as leitor_stream:
            stream_texto = io.TextIOWrapper(leitor_stream, encoding='utf-8')
            with open(caminho_saida, 'w', encoding='utf-8') as arquivo_saida:
                contador_partidas = 0
                for linha in stream_texto:
                    if linha.startswith("[Event "):
                        if contador_partidas == limite_partidas:
                            break
                        contador_partidas += 1
                        if contador_partidas % 10000 == 0:
                            print(f"{contador_partidas} partidas processadas...")
                    arquivo_saida.write(linha)
    print(f"Sucesso! {contador_partidas} partidas foram salvas em '{caminho_saida}'.")

if __name__ == "__main__":
    ARQUIVO_ENTRADA = "arquivo.pgn.zst" 
    ARQUIVO_SAIDA = "primeiras_10000_partidas.pgn"
    extrair_partidas_zst(ARQUIVO_ENTRADA, ARQUIVO_SAIDA, 100000)
