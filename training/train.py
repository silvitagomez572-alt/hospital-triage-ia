import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

RANDOM_STATE = 42


def generate_synthetic_triage(n: int = 8000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(0, 100, size=n)
    pain_level = rng.integers(0, 11, size=n)
    systolic_bp = rng.integers(70, 190, size=n)
    diastolic_bp = rng.integers(40, 120, size=n)
    heart_rate = rng.integers(40, 160, size=n)
    temperature = rng.uniform(35.0, 41.0, size=n)

    risk = np.zeros(n, dtype=int)
    risk += (pain_level >= 8).astype(int) * 2
    risk += (systolic_bp < 90).astype(int) * 2
    risk += (heart_rate > 120).astype(int) * 2
    risk += (temperature >= 39.0).astype(int) * 2
    risk += ((age >= 75) & (systolic_bp < 100)).astype(int) * 1
    risk += (diastolic_bp < 60).astype(int) * 1

    target = np.where(risk >= 4, "high", np.where(risk >= 2, "medium", "low"))

    return pd.DataFrame({
        "age": age,
        "pain_level": pain_level,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "heart_rate": heart_rate,
        "temperature": temperature,
        "target": target
    })


def main():
    os.makedirs("../artifacts", exist_ok=True)
    os.makedirs("../api/model", exist_ok=True)

    df = generate_synthetic_triage()
    X = df.drop(columns=["target"])
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred, labels=["low", "medium", "high"])
    report = classification_report(y_test, y_pred)

    print("Accuracy:", acc)
    print("Confusion Matrix (low/medium/high):\n", cm)
    print("\nClassification report:\n", report)

    df.to_csv("../artifacts/synthetic_triage_dataset.csv", index=False)
    with open("../artifacts/metrics.txt", "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {acc}\n\n")
        f.write("Confusion Matrix (low/medium/high):\n")
        f.write(str(cm))
        f.write("\n\nClassification report:\n")
        f.write(report)

    joblib.dump(model, "../api/model/triage_model_v1.pkl")
    print("\n✅ Saved model to ../api/model/triage_model_v1.pkl")


if __name__ == "__main__":
    main()
