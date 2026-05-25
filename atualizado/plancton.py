import os
import pandas as pd
from pathlib import Path

def filtrar_partidas_por_rating(pasta_entrada, pasta_saida, max_diff=50):
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_entrada = Path(pasta_entrada)
    arquivos_csv = list(caminho_entrada.glob("*.csv"))
    if not arquivos_csv:
        print(f"Nenhum arquivo .csv encontrado na pasta '{pasta_entrada}'.")
        return
    print(f"Encontrados {len(arquivos_csv)} arquivos. Iniciando filtragem...\n")
    for caminho_arquivo in arquivos_csv:
        try:
            df = pd.read_csv(caminho_arquivo)
            if 'w_rating' not in df.columns or 'b_rating' not in df.columns:
                print(f"Aviso: Colunas 'w_rating' ou 'b_rating' não encontradas em '{caminho_arquivo.name}'. Pulando.")
                continue
            diferenca_rating = (df['w_rating'] - df['b_rating']).abs()
            df_filtrado = df[diferenca_rating < max_diff]
            caminho_arquivo_saida = os.path.join(pasta_saida, caminho_arquivo.name)
            df_filtrado.to_csv(caminho_arquivo_saida, index=False)
            print(f"Salvo: {caminho_arquivo.name} | Original: {len(df)} linhas | Filtrado: {len(df_filtrado)} linhas")
        except Exception as e:
            print(f"Erro ao processar '{caminho_arquivo.name}': {e}")
    print("\nProcesso de filtragem concluído com sucesso!")

if __name__ == "__main__":
    PASTA_ORIGEM = "./aberturas_csv" 
    PASTA_DESTINO = "./aberturas_csv_filtradas"
    filtrar_partidas_por_rating(PASTA_ORIGEM, PASTA_DESTINO)
