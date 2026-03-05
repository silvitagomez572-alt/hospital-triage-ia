# Hospital Triage IA – Trabajo Final Integrador
## Infraestructura Tecnológica para Inteligencia Artificial

## Objetivo

Diseñar e implementar una API de inferencia en Python que permita estimar un nivel de riesgo clínico a partir de datos básicos de pacientes en un contexto de triage hospitalario.

El proyecto forma parte del trabajo final de la materia **Infraestructura Tecnológica para Inteligencia Artificial**.

---

# Descripción del Proyecto

El sistema implementa una **API REST desarrollada con FastAPI** que recibe información clínica básica de un paciente y devuelve una estimación de riesgo.

El objetivo es demostrar la construcción de una arquitectura simple para servicios de IA incluyendo:

- API de inferencia
- tests automáticos
- pipeline de CI/CD
- infraestructura como código

---

# Arquitectura del Sistema

La arquitectura del sistema está compuesta por los siguientes elementos:

### API de Serving

- Framework: **FastAPI**
- Endpoints REST para inferencia
- Documentación automática con **Swagger**

### Tests

Se incluyen **tests automáticos con pytest** para validar el funcionamiento de la API.

Ubicación:
api/tests

### CI/CD

Se implementó un pipeline de **Integración Continua con GitHub Actions** que ejecuta automáticamente los tests en cada push o pull request.

Archivo de configuración:
github/workflows/tests.yml

### Infraestructura

El proyecto incluye archivos de infraestructura relacionados con despliegue en entornos cloud:

- **Terraform**
- **Horizontal Pod Autoscaler para Kubernetes**

Archivo incluido:
triage-api-hpa.yaml

---

# Estructura del Repositorio
hospital-triage-ia
│
├── api/
│ ├── main.py
│ └── tests/
│
├── infra/
│ └── terraform/
│
├── .github/workflows/
│ └── tests.yml
│
├── requirements.txt
├── pytest.ini
├── triage-api-hpa.yaml
└── README.md

---

# Endpoints Principales

### Health Check
GET /health

Permite verificar el estado de la API.

Ejemplo de respuesta:

```json
{
  "status": "ok"
}
Predicción de riesgo
POST /predict

Entrada JSON:
{
  "age": 45,
  "pain_level": 6,
  "systolic_bp": 120,
  "diastolic_bp": 80,
  "heart_rate": 95,
  "temperature": 38.2
}
Respuesta:
{
  "risk_level": "low",
  "probability": 0.2
}
Ejecución del Proyecto

Instalar dependencias:
pip install -r requirements.txt
Ejecutar la API:

uvicorn api.main:app --reload

La API estará disponible en:

http://localhost:8000

Documentación Swagger:

http://localhost:8000/docs
Tecnologías Utilizadas

Python

FastAPI

Pytest

GitHub Actions

Terraform

Kubernetes

Repositorio

Proyecto disponible en:

https://github.com/silvitagomez572-alt/hospital-triage-ia

Aviso

Este sistema es un prototipo académico desarrollado con fines educativos y no reemplaza el criterio clínico profesional.
