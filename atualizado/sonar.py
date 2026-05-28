import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def carregar_amostra(diretorio_csv, n_por_arquivo=10000):
    caminhos = Path(diretorio_csv).glob("*.csv")
    lista_amostras = []
    file = 0
    for f in caminhos:
        file += 1
        if (file % 10 == 0): print(f"Ta rodando! f = {file}")
        
        df_temp = pd.read_csv(f)
            
        lista_amostras.append(df_temp[df_temp['move_no']==5])

    return pd.concat(lista_amostras, ignore_index=True)


df = carregar_amostra("C:/Users/tiago/Desktop/Xadrez/aberturas_xadrez/novo/aberturas_csv")

# -> TRATAMENTO PARA VISUALIZAÇÃO

# Criar coluna de Diferença de Rating
df['rating_diff'] = df['w_rating'] - df['b_rating']

# Filtrar apenas as aberturas mais comuns
top_openings = df['opening'].value_counts().nlargest(20).index
df_top = df[df['opening'].isin(top_openings)]

# -> CÓDIGO DAS VISUALIZAÇÕES

plt.figure(figsize=(15, 10))

# Distribuição de Ratings
plt.subplot(2, 2, 1)
sns.histplot(df[['w_rating', 'b_rating']], kde=True, element="step")
plt.title("Distribuição de Ratings (Brancas vs Pretas)")
plt.xlabel("ELO")

# Win-Rate Médio por Abertura
# (1.0 = Brancas ganharam, 0.5 = Empate, 0.0 = Pretas ganharam)
plt.subplot(2, 2, 2)
sns.barplot(data=df_top, x='result', y='opening', palette="viridis", errorbar=None)
plt.axvline(0.5, color='red', linestyle='--') # Linha do empate
plt.title("Probabilidade de Vitória das Brancas por Abertura")
plt.xlabel("Resultado Médio (Próximo de 1 = Vantagem Branca)")

#Relação Diferença de Rating vs Resultado
plt.subplot(2, 2, 3)
sns.regplot(data=df.sample(2000), x='rating_diff', y='result', 
            scatter_kws={'alpha':0.1}, line_kws={'color':'red'})
plt.title("Correlação: Diferença de Rating vs Resultado")
plt.xlabel("Rating Brancas - Rating Pretas")

# Quantidade de lances processados por abertura
plt.subplot(2, 2, 4)
df_top['opening'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title("Distribuição do Volume de Dados (Top 10)")
plt.ylabel("")

plt.tight_layout()
plt.show()