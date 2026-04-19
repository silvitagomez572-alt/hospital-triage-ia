# Hospital Triage IA – Trabajo Final Integrador

## Infraestructura Tecnológica para Inteligencia Artificial

## Objetivo

Diseñar e implementar una API de inferencia en Python que permita estimar un nivel de riesgo clínico a partir de datos básicos de pacientes en un contexto de triage hospitalario.

---

## Descripción del Proyecto

El sistema implementa una **API REST desarrollada con FastAPI** que recibe información clínica básica de un paciente y devuelve una estimación de riesgo.

Incluye:

- API de inferencia
- modelo de Machine Learning entrenado
- tests automáticos
- CI/CD con GitHub Actions
- infraestructura como código (Terraform)
- despliegue con Docker y Kubernetes

---

## Modelo de Machine Learning

Se entrenó un modelo de clasificación (`RandomForestClassifier`) con datos sintéticos.

El modelo se serializa en:

api/model/triage_model_v1.pkl

y es utilizado por el endpoint:

POST /predict

---

## Arquitectura del Sistema

### API de Serving
- FastAPI
- Endpoints REST
- Swagger automático

### Tests
Ubicación:
api/tests

### CI/CD
.github/workflows/tests.yml

### Infraestructura
- Terraform
- Kubernetes Deployment
- Horizontal Pod Autoscaler

k8s/triage-api-deployment.yaml  
k8s/triage-api-hpa.yaml

---

## Estructura del Repositorio

hospital-triage-ia/
├── api/
│   ├── main.py
│   ├── requirements.txt
│   ├── model/
│   │   └── triage_model_v1.pkl
│   ├── templates/
│   ├── static/
│   └── tests/
├── infra/
│   └── terraform/
├── k8s/
│   ├── triage-api-deployment.yaml
│   └── triage-api-hpa.yaml
├── training/
├── .github/workflows/
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── pytest.ini
└── README.md

---

## Endpoints

### Health Check
GET /health

Respuesta:

{
  "status": "ok",
  "time": "2026-04-19T12:00:00"
}

### Predicción
POST /predict

Entrada:

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
  "probability": 0.2,
  "model_path": "api/model/triage_model_v1.pkl"
}

---

## Ejecución

pip install -r requirements.txt  
uvicorn api.main:app --reload

Swagger:
http://localhost:8000/docs

---

## Tecnologías

- Python
- FastAPI
- Scikit-learn
- Pytest
- GitHub Actions
- Terraform
- Kubernetes
- Docker

---

## Repositorio

https://github.com/silvitagomez572-alt/hospital-triage-ia

---

## Aviso

Sistema académico. No reemplaza criterio clínico profesional.
