# Hospital Triage IA – Trabajo Final Integrador
## Infraestructura Tecnológica para Inteligencia Artificial

## Objetivo

Diseñar, implementar y contenerizar una API de inferencia en Python que permita servir un modelo de Machine Learning para priorización de pacientes en un sistema de triage hospitalario.

El sistema incluye:

- API de inferencia para clasificación de riesgo
- Formularios clínicos de triage
- Paneles operativos y de gestión
- Persistencia de registros
- Pipeline de CI/CD
- Preparación para despliegue en Kubernetes

---

# Descripción del Proyecto

El sistema implementa un **prototipo de priorización de pacientes basado en Manchester Triage**, complementado con un **modelo de Machine Learning** que estima un nivel de riesgo clínico.

El objetivo es asistir al personal sanitario en la priorización de pacientes mediante:

- evaluación de signos vitales
- clasificación por color de triage
- estimación de riesgo mediante ML
- registro trazable de atenciones

El sistema también incluye **paneles de visualización para personal médico y directivos**, permitiendo analizar indicadores operativos.

---

# Arquitectura del Sistema

La arquitectura del sistema está basada en una API REST desarrollada en Python utilizando FastAPI.

El servicio expone endpoints que permiten verificar el estado del sistema y realizar predicciones de riesgo a partir de datos clínicos básicos.

Componentes principales

API de Serving

Framework: FastAPI

Exposición de endpoints REST

Documentación automática mediante Swagger UI

Lógica de inferencia

La API recibe información clínica básica de un paciente:

edad

nivel de dolor

presión arterial

frecuencia cardíaca

temperatura

Con estos datos el sistema calcula un nivel estimado de riesgo y devuelve una respuesta en formato JSON.

Tests automáticos

El proyecto incluye tests desarrollados con pytest, ubicados en:
api/tests

Estos tests verifican el correcto funcionamiento de los endpoints principales de la API.

CI/CD

El repositorio incluye un pipeline de Integración Continua mediante GitHub Actions.

El workflow ejecuta automáticamente:

instalación de dependencias

ejecución de tests con pytest

Esto permite validar automáticamente el funcionamiento del proyecto en cada cambio realizado en el repositorio.

Infraestructura

El proyecto incluye archivos de infraestructura relacionados con despliegue en entornos cloud:

Terraform para infraestructura como código

Horizontal Pod Autoscaler (HPA) para Kubernetes

Archivo incluido:
triage-api-hpa.yaml
Estructura del Repositorio

hospital-triage-ia
│
├── api/
│   ├── main.py
│   └── tests/
│
├── infra/
│   └── terraform/
│
├── .github/workflows/
│   └── tests.yml
│
├── requirements.txt
├── pytest.ini
├── triage-api-hpa.yaml
└── README.md

Endpoints Principales
Health Check
GET /health
Permite verificar el estado de la API.

Ejemplo de respuesta:
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
