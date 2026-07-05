from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['model']
        pacote = joblib.load(file)
        modelo = pacote["modelo"]
        encoder = pacote["encoder_aberturas"]
        features_finais = pacote["features"]
        artefatos = pacote["artefatos_preproc"]
        w_rating = float(request.form['w_rating'])
        b_rating = float(request.form['b_rating'])
        opening = request.form['opening']
        rating_diff = w_rating - b_rating
        rating_avg = (w_rating + b_rating) / 2.0
        probs = artefatos["smoothed_probs"].get(
            opening, 
            {"op_prob_0": artefatos["global_mean"].get(0, 0.0),
             "op_prob_1": artefatos["global_mean"].get(1, 0.0),
             "op_prob_2": artefatos["global_mean"].get(2, 0.0)}
        )
        opening_encoded = encoder.transform([opening])[0] if opening in encoder.classes_ else -1
        opening_count = artefatos["opening_count_map"].get(opening, 0)
        borders = artefatos["bins_rating_avg"]
        rating_avg_bin = pd.cut([rating_avg], bins=borders, labels=False, duplicates="drop")[0]
        if pd.isna(rating_avg_bin):
            rating_avg_bin = -1
        df_input = pd.DataFrame([{
            "w_rating": w_rating,
            "b_rating": b_rating,
            "rating_diff": rating_diff,
            "rating_avg": rating_avg,
            "op_prob_0": probs["op_prob_0"],
            "op_prob_1": probs["op_prob_1"],
            "op_prob_2": probs["op_prob_2"],
            "opening_encoded": opening_encoded,
            "opening_count": int(opening_count),
            "rating_avg_bin": int(rating_avg_bin)
        }])[features_finais]
        predicao = modelo.predict(df_input)[0]
        mapa_resultado = {0: "Vitória das Brancas ⚪", 1: "Empate 🤝", 2: "Vitória das Pretas ⚫"}
        return jsonify({"prediction": mapa_resultado[predicao]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)