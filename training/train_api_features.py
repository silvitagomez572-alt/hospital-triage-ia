import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

RANDOM_STATE = 42

FEATURES = ["temperatura", "frecuencia_respiratoria", "spo2", "fc", "pas", "dolor"]
CLASSES = ["VERDE", "AMARILLO", "ROJO"]

def generate_synthetic_api_triage(n: int = 12000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    temperatura = rng.uniform(34.5, 41.0, size=n)
    frecuencia_respiratoria = rng.integers(10, 45, size=n)
    spo2 = rng.integers(80, 100, size=n)
    fc = rng.integers(40, 160, size=n)
    pas = rng.integers(70, 190, size=n)
    dolor = rng.integers(0, 11, size=n)

    # Riesgo simple (para dataset sintético)
    risk = np.zeros(n, dtype=int)

    # Disparadores "ROJO"
    risk += (spo2 <= 90).astype(int) * 4
    risk += (pas < 90).astype(int) * 4
    risk += (frecuencia_respiratoria >= 36).astype(int) * 3
    risk += ((temperatura >= 40) | (temperatura <= 35)).astype(int) * 3
    risk += (fc >= 140).astype(int) * 2
    risk += (dolor >= 9).astype(int) * 1

    # Map a clases Manchester simplificado:
    # Alto riesgo -> ROJO, medio -> AMARILLO, bajo -> VERDE
    target = np.where(risk >= 6, "ROJO", np.where(risk >= 2, "AMARILLO", "VERDE"))

    df = pd.DataFrame({
        "temperatura": temperatura,
        "frecuencia_respiratoria": frecuencia_respiratoria,
        "spo2": spo2,
        "fc": fc,
        "pas": pas,
        "dolor": dolor,
        "target": target
    })
    return df

def main():
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("api/model", exist_ok=True)

    df = generate_synthetic_api_triage()

    X = df[FEATURES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=250,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample"
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred, labels=CLASSES)
    report = classification_report(y_test, y_pred, labels=CLASSES)

    print("Accuracy:", acc)
    print("Confusion Matrix (VERDE/AMARILLO/ROJO):\n", cm)
    print("\nClassification report:\n", report)

    # Guardar dataset + métricas
    df.to_csv("artifacts/synthetic_triage_api_features.csv", index=False)
    with open("artifacts/metrics_api_features.txt", "w", encoding="utf-8") as f:
        f.write(f"FEATURES: {FEATURES}\n")
        f.write(f"Accuracy: {acc}\n\n")
        f.write("Confusion Matrix (VERDE/AMARILLO/ROJO):\n")
        f.write(str(cm))
        f.write("\n\nClassification report:\n")
        f.write(report)

    # Guardar modelo donde la API lo busca
    out_path = "api/model/triage_model_20260303.pkl"
    joblib.dump(model, out_path)
    print(f"\n✅ Saved model to {out_path}")

if __name__ == "__main__":
    main()
