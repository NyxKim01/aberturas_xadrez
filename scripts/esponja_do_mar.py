import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

PASTA_CSVS = "aberturas_csv"
LANCE_ALVO = 10
MIN_JOGOS_ABERTURA = 80

def preparar_dados_para_ia(diretorio):
    print("1. Carregando e unindo os arquivos CSV...")
    caminhos = Path(diretorio).glob("*.csv")
    lista_dfs = []

    # 1. Pegar cada partida só 1 vez    
    for cp in caminhos:
        temp_df = pd.read_csv(cp)
        lista_dfs.append(temp_df[temp_df['move_no'] == LANCE_ALVO])
        
    df = pd.concat(lista_dfs, ignore_index=True)
    print(f"Total de linhas extraídas no lance {LANCE_ALVO}: {len(df)}")

    # 2. Limpeza de nulos essenciais
    df = df.dropna(subset=['w_rating', 'b_rating', 'opening', 'result'])

    # 3. Remover aberturas com poucos dados
    print(f"2. Filtrando aberturas com menos de {MIN_JOGOS_ABERTURA} jogos...")
    contagem_aberturas = df['opening'].value_counts()
    aberturas_validas = contagem_aberturas[contagem_aberturas >= MIN_JOGOS_ABERTURA].index
    df_filtrado = df[df['opening'].isin(aberturas_validas)].copy()
    print(f"Linhas restantes após o filtro de abertura: {len(df_filtrado)}")

    # 4. Criando a diferença de rating
    df_filtrado['rating_diff'] = df_filtrado['w_rating'] - df_filtrado['b_rating']

    # 5. Label Encoding da abertura
    print("3. Codificando variáveis categóricas...")
    le = LabelEncoder()
    df_filtrado['opening_encoded'] = le.fit_transform(df_filtrado['opening'])

    # 6. Seleção de Recursos (Features) e Alvo (Target)
    # Remove o FEN por enquanto (pq árvores não lêem texto puro) e o opening antigo
    features = ['w_rating', 'b_rating', 'rating_diff', 'opening_encoded']
    target = 'result'

    X = df_filtrado[features]
    y = df_filtrado[target]

    # 7. Divisão em Treino e Teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Formato dos dados de treino: {X_train.shape}")
    
    return X_train, X_test, y_train, y_test, le

preparar_dados_para_ia(PASTA_CSVS)