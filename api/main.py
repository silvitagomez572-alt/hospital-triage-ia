from fastapi import FastAPI
from schemas.triage import TriageInput, TriageOutput

app = FastAPI(
    title="Hospital Triage API",
    version="0.1.0",
    docs_url="/docs",          # Swagger UI
    openapi_url="/openapi.json"
)


@app.get("/", tags=["root"])
def root():
    return {"message": "Hospital Triage API running"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=TriageOutput, tags=["triage"])
def predict(input_data: TriageInput):
    """
    Reglas simples de triage (ejemplo):

    - Dolor muy alto (>= 8) suma 2 puntos
    - Presión sistólica < 90 mmHg suma 2 puntos
    - Frecuencia cardíaca > 110 lpm suma 1 punto
    """

    score = 0

    # Dolor
    if input_data.pain_level >= 8:
        score += 2

    # Presión sistólica baja
    if input_data.systolic_bp < 90:
        score += 2

    # Taquicardia
    if input_data.heart_rate > 110:
        score += 1

    # Asignar nivel de riesgo según el puntaje
    if score >= 3:
        risk_level = "high"
        probability = 0.9
    elif score == 2:
        risk_level = "medium"
        probability = 0.7
    else:
        risk_level = "low"
        probability = 0.5

    # 👈 Aquí estaba el error: antes devolvías `risk=...`
    return TriageOutput(risk_level=risk_level, probability=probability)
