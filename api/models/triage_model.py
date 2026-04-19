from schemas.triage import TriageInput, TriageOutput


def predict(data: TriageInput) -> TriageOutput:
    """
    Modelo de triage súper simple, sólo para demo.
    Calcula un puntaje de riesgo a partir de los signos vitales.
    """

    score = 0

    # Edad
    if data.age >= 75:
        score += 3
    elif data.age >= 60:
        score += 2
    elif data.age >= 40:
        score += 1

    # Nivel de dolor (1 a 10)
    if data.pain_level >= 8:
        score += 3
    elif data.pain_level >= 5:
        score += 2
    elif data.pain_level >= 3:
        score += 1

    # Presión sistólica
    if data.systolic_bp >= 180 or data.systolic_bp <= 90:
        score += 3
    elif data.systolic_bp >= 160:
        score += 2

    # Presión diastólica
    if data.diastolic_bp >= 110 or data.diastolic_bp <= 50:
        score += 2
    elif data.diastolic_bp >= 100:
        score += 1

    # Frecuencia cardíaca
    if data.heart_rate >= 130 or data.heart_rate <= 40:
        score += 3
    elif data.heart_rate >= 110:
        score += 2
    elif data.heart_rate >= 90:
        score += 1

    # Temperatura corporal
    if data.temperature >= 38.5 or data.temperature <= 35.0:
        score += 2

    # Mapeo de puntaje a nivel de riesgo
    if score >= 10:
        risk_level = "crítico"
        probability = 0.9
    elif score >= 6:
        risk_level = "alto"
        probability = 0.7
    elif score >= 3:
        risk_level = "moderado"
        probability = 0.5
    else:
        risk_level = "bajo"
        probability = 0.2

    return TriageOutput(
        risk_level=risk_level,
        score=score,
        probability=probability,
    )
