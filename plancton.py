import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
)
import joblib
import sys

PASTA_CSVS = "aberturas_csv"           
MODELO_PKL = "modelo_arvore_campeao.pkl"
LANCE_ALVO = 10
MIN_JOGOS_ABERTURA = 80              

# ------------------------------------------------------------
# Carregar artefatos salvos
# ------------------------------------------------------------
print("📦 Carregando modelo e artefatos...")
pacote = joblib.load(MODELO_PKL)
modelo = pacote["modelo"]
nome_modelo = pacote["nome_modelo"]
encoder_aberturas = pacote["encoder_aberturas"]
features = pacote["features"]
artefatos = pacote["artefatos_preproc"]
aberturas_validas = artefatos["aberturas_validas"]
smoothed_probs = artefatos["smoothed_probs"]
global_mean = artefatos["global_mean"]
opening_count_map = artefatos["opening_count_map"]
bins_rating_avg = artefatos["bins_rating_avg"]
print(f"   Modelo carregado: {nome_modelo}")
print(f"   Features esperadas: {features}")

# ------------------------------------------------------------
# Leitura e preparação dos dados de teste
# ------------------------------------------------------------
print("🧹 Lendo dados de teste...")
caminhos = list(Path(PASTA_CSVS).glob("*.csv"))
if not caminhos:
    print(f"❌ Nenhum CSV encontrado em '{PASTA_CSVS}'.", file=sys.stderr)
    sys.exit(1)
df = pd.concat([pd.read_csv(p) for p in caminhos], ignore_index=True)
df = df[df["move_no"] == LANCE_ALVO].copy()
df = df.dropna(subset=["w_rating", "b_rating", "opening", "result"])
df["target_class"] = df["result"].map({0.0: 0, 0.5: 1, 1.0: 2})
df = df.dropna(subset=["target_class"])
y_true = df["target_class"].astype(int)
df["rating_diff"] = df["w_rating"] - df["b_rating"]
df["rating_avg"] = (df["w_rating"] + df["b_rating"]) / 2.0
for c in [0, 1, 2]:
    prob_col = f"op_prob_{c}"
    df[prob_col] = df["opening"].apply(
        lambda op: smoothed_probs.get(op, {}).get(prob_col, global_mean.get(c, 0.0))
    )
df["opening_count"] = df["opening"].map(opening_count_map).fillna(0).astype(int)
df["rating_avg_bin"] = pd.cut(
    df["rating_avg"], bins=bins_rating_avg, labels=False, duplicates="drop"
)
df["rating_avg_bin"] = df["rating_avg_bin"].fillna(-1).astype(int)
df["opening_encoded"] = df["opening"].apply(
    lambda s: encoder_aberturas.transform([s])[0]
    if s in encoder_aberturas.classes_
    else -1
)
X_test = df[features].copy()
print(f"   Dados preparados: {X_test.shape[0]} linhas, {X_test.shape[1]} colunas.")

# ------------------------------------------------------------
# Avaliação do modelo
# ------------------------------------------------------------
print("\n📊 Avaliando o modelo campeão...")
y_pred = modelo.predict(X_test)
y_proba = modelo.predict_proba(X_test) if hasattr(modelo, "predict_proba") else None
acc = accuracy_score(y_true, y_pred)
print(f"\n✅ Acurácia: {acc:.4f}")
target_names = ["Derrota (0)", "Empate (1)", "Vitória (2)"]
print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred, target_names=target_names))
print("📋 Matriz de Confusão:")
print(confusion_matrix(y_true, y_pred))
if y_proba is not None:
    try:
        ll = log_loss(y_true, y_proba)
        print(f"\n📉 Log Loss: {ll:.4f}")
    except ValueError as e:
        print(f"   Não foi possível calcular log loss: {e}")
print("\n🏁 Teste concluído.")