import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    VotingClassifier,
    StackingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
import optuna
import joblib
import warnings
warnings.filterwarnings("ignore")

# ------------------------------------------------------------
# Configurações Globais
# ------------------------------------------------------------
SEED = 42
PASTA_CSVS = "aberturas_csv"
LANCE_ALVO = 10
MIN_JOGOS_ABERTURA = 80
N_TRIALS_OPTUNA = 2

# ------------------------------------------------------------
# 1) Preparação dos Dados – Retorna também artefatos para reuso
# ------------------------------------------------------------
def preparar_dados_para_ia(diretorio):
    print("🧹 Lendo CSVs ...")
    caminhos = list(Path(diretorio).glob("*.csv"))
    if not caminhos:
        raise FileNotFoundError(f"Nenhum CSV em '{diretorio}'.")
    df = pd.concat([pd.read_csv(p) for p in caminhos], ignore_index=True)
    df = df[df["move_no"] == LANCE_ALVO].copy()
    df = df.dropna(subset=["w_rating", "b_rating", "opening", "result"])
    df["target_class"] = df["result"].map({0.0: 0, 0.5: 1, 1.0: 2})
    df = df.dropna(subset=["target_class"])
    contagem = df["opening"].value_counts()
    aberturas_validas = contagem[contagem >= MIN_JOGOS_ABERTURA].index.tolist()
    df = df[df["opening"].isin(aberturas_validas)].copy()
    df["rating_diff"] = df["w_rating"] - df["b_rating"]
    df["rating_avg"] = (df["w_rating"] + df["b_rating"]) / 2.0
    X = df[["w_rating", "b_rating", "rating_diff", "rating_avg", "opening"]]
    y = df["target_class"].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y
    )
    global_mean = y_train.value_counts(normalize=True)
    train_df = X_train.copy()
    train_df["target"] = y_train
    op_stats = (
        train_df.groupby("opening")["target"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )
    for c in [0, 1, 2]:
        if c not in op_stats.columns:
            op_stats[c] = 0.0
    op_counts = train_df["opening"].value_counts()
    m = 15  
    smoothed = {}
    for op in op_counts.index:
        cnt = op_counts[op]
        smoothed[op] = {
            "op_prob_0": (op_stats.loc[op, 0] * cnt + global_mean.get(0, 0) * m) / (cnt + m),
            "op_prob_1": (op_stats.loc[op, 1] * cnt + global_mean.get(1, 0) * m) / (cnt + m),
            "op_prob_2": (op_stats.loc[op, 2] * cnt + global_mean.get(2, 0) * m) / (cnt + m),
        }
    df_smoothed = pd.DataFrame.from_dict(smoothed, orient="index")
    X_train = X_train.join(df_smoothed, on="opening")
    X_test = X_test.join(df_smoothed, on="opening")
    for c in [0, 1, 2]:
        X_train[f"op_prob_{c}"] = X_train[f"op_prob_{c}"].fillna(global_mean.get(c, 0.0))
        X_test[f"op_prob_{c}"] = X_test[f"op_prob_{c}"].fillna(global_mean.get(c, 0.0))
    pop_map = op_counts.to_dict()
    X_train["opening_count"] = X_train["opening"].map(pop_map).fillna(0).astype(int)
    X_test["opening_count"] = X_test["opening"].map(pop_map).fillna(0).astype(int)
    train_avg = X_train["rating_avg"]
    borders = np.quantile(train_avg, np.linspace(0, 1, 11))
    borders[0] = -np.inf
    borders[-1] = np.inf
    X_train["rating_avg_bin"] = pd.cut(train_avg, bins=borders, labels=False, duplicates="drop")
    X_test["rating_avg_bin"] = pd.cut(
        X_test["rating_avg"], bins=borders, labels=False, duplicates="drop"
    )
    X_train["rating_avg_bin"] = X_train["rating_avg_bin"].fillna(-1).astype(int)
    X_test["rating_avg_bin"] = X_test["rating_avg_bin"].fillna(-1).astype(int)
    le = LabelEncoder()
    X_train["opening_encoded"] = le.fit_transform(X_train["opening"])
    X_test["opening_encoded"] = X_test["opening"].map(
        lambda s: le.transform([s])[0] if s in le.classes_ else -1
    )
    features_finais = [
        "w_rating",
        "b_rating",
        "rating_diff",
        "rating_avg",
        "op_prob_0",
        "op_prob_1",
        "op_prob_2",
        "opening_encoded",
        "opening_count",
        "rating_avg_bin",
    ]
    X_train = X_train[features_finais]
    X_test = X_test[features_finais]
    print(f"✅ Features preparadas: {features_finais}")
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "encoder_aberturas": le,
        "features": features_finais,
        "artefatos_preproc": {
            "aberturas_validas": aberturas_validas,
            "smoothed_probs": smoothed,          
            "global_mean": global_mean.to_dict(),
            "opening_count_map": pop_map,
            "bins_rating_avg": borders,
        },
    }

# ------------------------------------------------------------
# 2) Otimização dos modelos com Optuna
# ------------------------------------------------------------
def tunar_modelo(nome, X_train, y_train):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    if nome == "RandomForest":
        def objetivo(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 300, 800),
                "max_depth": trial.suggest_int("max_depth", 5, 40),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                "class_weight": "balanced",
                "random_state": SEED,
                "n_jobs": -1,
            }
            model = RandomForestClassifier(**params)
            return cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        best.update({"class_weight": "balanced", "random_state": SEED, "n_jobs": -1})
        return RandomForestClassifier(**best)
    elif nome == "ExtraTrees":
        def objetivo(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 300, 800),
                "max_depth": trial.suggest_int("max_depth", 5, 40),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                "class_weight": "balanced",
                "random_state": SEED,
                "n_jobs": -1,
            }
            model = ExtraTreesClassifier(**params)
            return cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        best.update({"class_weight": "balanced", "random_state": SEED, "n_jobs": -1})
        return ExtraTreesClassifier(**best)
    elif nome == "HistGB":
        def objetivo(trial):
            params = {
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "max_iter": trial.suggest_int("max_iter", 200, 600),
                "max_depth": trial.suggest_int("max_depth", 3, 30),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 20, 150),
                "l2_regularization": trial.suggest_float("l2_regularization", 0.0, 3.0),
                "random_state": SEED,
            }
            model = HistGradientBoostingClassifier(**params)
            return cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        best["random_state"] = SEED
        return HistGradientBoostingClassifier(**best)
    elif nome == "XGBoost":
        def objetivo(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 300, 800),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 2.0),
                "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 2.0),
                "random_state": SEED,
                "use_label_encoder": False,
                "eval_metric": "mlogloss",
                "n_jobs": -1,
            }
            model = XGBClassifier(**params)
            return cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        best.update({"random_state": SEED, "use_label_encoder": False, "eval_metric": "mlogloss", "n_jobs": -1})
        return XGBClassifier(**best)
    elif nome == "LightGBM":
        def objetivo(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 300, 800),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "num_leaves": trial.suggest_int("num_leaves", 20, 150),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 2.0),
                "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 2.0),
                "random_state": SEED,
                "n_jobs": -1,
                "verbose": -1,
            }
            model = LGBMClassifier(**params)
            return cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        best.update({"random_state": SEED, "n_jobs": -1, "verbose": -1})
        return LGBMClassifier(**best)
    elif nome == "MLP":
        def objetivo(trial):
            n_layers = trial.suggest_int("n_layers", 1, 3)
            hidden_units = [trial.suggest_int(f"units_layer{i}", 50, 300) for i in range(n_layers)]
            params = {
                "hidden_layer_sizes": tuple(hidden_units),
                "activation": "relu",
                "alpha": trial.suggest_float("alpha", 0.0001, 0.1, log=True),
                "learning_rate_init": trial.suggest_float("learning_rate_init", 0.0005, 0.01, log=True),
                "max_iter": 500,
                "random_state": SEED,
            }
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_train)
            model = MLPClassifier(**params)
            return cross_val_score(model, X_scaled, y_train, cv=cv, scoring="accuracy").mean()
        study = optuna.create_study(direction="maximize")
        study.optimize(objetivo, n_trials=N_TRIALS_OPTUNA)
        best = study.best_params
        hidden = tuple(best[f"units_layer{i}"] for i in range(best["n_layers"]))
        best["hidden_layer_sizes"] = hidden
        for key in list(best.keys()):
            if key.startswith("units_layer") or key == "n_layers":
                del best[key]
        best.update({"max_iter": 500, "random_state": SEED, "activation": "relu"})
        return MLPClassifier(**best)
    else:
        raise ValueError(f"Modelo desconhecido: {nome}")

# ------------------------------------------------------------
# 3) Construção do Super Ensemble com Stacking
# ------------------------------------------------------------
def criar_super_modelo(dados):
    X_train = dados["X_train"]
    y_train = dados["y_train"]
    X_test = dados["X_test"]
    y_test = dados["y_test"]
    print("\n🚀 Iniciando tuning de elite com Optuna...")
    nomes_modelos = ["RandomForest", "ExtraTrees", "HistGB", "XGBoost", "LightGBM", "MLP"]
    modelos_tunados = {}
    for nome in nomes_modelos:
        print(f"   ⚙️  Tunando {nome} ...")
        modelos_tunados[nome] = tunar_modelo(nome, X_train, y_train)
    print("\n📊 Acurácia individual no conjunto de teste:")
    for nome, model in modelos_tunados.items():
        if nome == "MLP":
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            model.fit(X_train_scaled, y_train) 
            acc = model.score(X_test_scaled, y_test)
        else:
            model.fit(X_train, y_train) 
            acc = model.score(X_test, y_test)
        print(f"   {nome:>20s} : {acc:.4f}")
    print("\n🔮 Construindo Stacking Classifier com meta-modelo LogisticRegression...")
    stack_estimators = []
    for nome, model in modelos_tunados.items():
        if nome == "MLP":
            pipe = Pipeline([("scaler", StandardScaler()), ("mlp", model)])
            stack_estimators.append((nome, pipe))
        else:
            stack_estimators.append((nome, model))
    meta_model = LogisticRegression(
        solver="lbfgs", max_iter=1000, random_state=SEED
    )
    stacking = StackingClassifier(
        estimators=stack_estimators,
        final_estimator=meta_model,
        cv=5,
        passthrough=False,
        n_jobs=-1,
    )
    stacking.fit(X_train, y_train)
    acc_stack = stacking.score(X_test, y_test)
    print(f"\n🏆 Acurácia do Stacking Ensemble no teste: {acc_stack:.4f}")
    print("\n🤝 Criando VotingClassifier (soft) ...")
    voting_soft = VotingClassifier(estimators=stack_estimators, voting="soft", n_jobs=-1)
    voting_soft.fit(X_train, y_train)
    acc_vote = voting_soft.score(X_test, y_test)
    print(f"   Voting Soft Acurácia no teste: {acc_vote:.4f}")
    if acc_stack >= acc_vote:
        modelo_final = stacking
        nome_modelo = "Stacking_Ensemble"
    else:
        modelo_final = voting_soft
        nome_modelo = "Voting_Ensemble"
    print(f"\n✅ Modelo final escolhido: {nome_modelo}")
    return modelo_final, nome_modelo

# ------------------------------------------------------------
# Execução Principal
# ------------------------------------------------------------
if __name__ == "__main__":
    dados = preparar_dados_para_ia(PASTA_CSVS)
    modelo, nome = criar_super_modelo(dados)
    pacote = {
        "modelo": modelo,
        "nome_modelo": nome,
        "encoder_aberturas": dados["encoder_aberturas"],
        "features": dados["features"],
        "artefatos_preproc": dados["artefatos_preproc"],
    }
    joblib.dump(pacote, "modelo_arvore_campeao.pkl")
    print(f"\n✅ Modelo '{nome}' salvo como 'modelo_arvore_campeao.pkl' com sucesso!")
