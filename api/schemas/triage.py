from pydantic import BaseModel, Field


class TriageInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Edad del paciente en años")
    pain_level: int = Field(
        ..., ge=0, le=10, description="Nivel de dolor (0 sin dolor, 10 máximo dolor)"
    )
    systolic_bp: int = Field(
        ..., ge=40, le=250, description="Presión arterial sistólica (mmHg)"
    )
    diastolic_bp: int = Field(
        ..., ge=20, le=150, description="Presión arterial diastólica (mmHg)"
    )
    heart_rate: int = Field(
        ..., ge=30, le=250, description="Frecuencia cardíaca (latidos por minuto)"
    )
    temperature: float = Field(
        ..., ge=30, le=45, description="Temperatura corporal (°C)"
    )


class TriageOutput(BaseModel):
    # 👀 IMPORTANTE: este nombre debe coincidir con lo que devolvemos en main.py
    risk_level: str
    probability: float

