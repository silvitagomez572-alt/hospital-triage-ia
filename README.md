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

La arquitectura sigue un enfoque modular orientado a servicios.

### Componentes principales

**API de Serving**
- Framework: **FastAPI**
- Motor de plantillas: **Jinja2**
- Exposición de endpoints REST y formularios web

**Modelo de Machine Learning**
- Modelo serializado en formato `.pkl`
- Cargado al iniciar la API
- Utilizado para inferencias en endpoints `/predict` y `/predict_full`

**Persistencia**
- Registro de triages en archivos **JSON**
- Control de acceso concurrente mediante file-lock

**Interfaz de usuario**
- Formularios HTML para triage
- Panel médico
- Panel directivos con indicadores

**CI/CD**
- Pipeline automatizado mediante **GitHub Actions**
- Ejecución de tests con **pytest** en cada push

**Infraestructura**
- Preparación para despliegue con **Docker**
- Infraestructura como código con **Terraform**
- Configuración de **Horizontal Pod Autoscaler para Kubernetes**

---

# Estructura del Repositorio
hospital-triage-ia
│
├── api/
│ ├── main.py
│ ├── templates/
│ ├── static/
│ └── tests/
│
├── training/
│ Scripts de entrenamiento y versionado del modelo
│
├── infra/terraform/
│ Infraestructura como código
│
├── .github/workflows/
│ Pipeline de CI/CD con GitHub Actions
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

---

### Inferencia ML (modo simple)
POST /predict
Entrada JSON:

```json
{
  "age": 45,
  "pain_level": 6,
  "systolic_bp": 120,
  "diastolic_bp": 80,
  "heart_rate": 95,
  "temperature": 38.2
}
Respuesta:{
  "risk_level": "low",
  "probability": 0.2
}
Inferencia completa
POST /predict_full
Utilizado para evaluaciones más completas dentro del sistema.
Formulario de Triage
GET /triage
Formulario clínico para registrar datos del paciente.

Registro de Triage
POST /triage/predict

Procesa el formulario, ejecuta inferencia y genera una ficha de triage.

Panel Médico
GET /medico

Vista operativa del sistema.

Panel Directivos
GET /directivos

Panel con indicadores de gestión.

Ejecución del Proyecto
Ejecutar con Docker

Desde la carpeta api:
cd api
docker compose up --build
Una vez levantado el servicio:

Formulario de triage
http://localhost:8001/triage
Panel médico
http://localhost:8001/medico
Panel directivos
http://localhost:8001/directivos
Health check
http://localhost:8001/health
Documentación Swagger
http://localhost:8001/docs
CI/CD
El proyecto incluye un pipeline de Integración Continua mediante GitHub Actions.

El workflow ejecuta:

Instalación de Python

Instalación de dependencias

Ejecución de tests con pytest

Archivo de configuración:

.github/workflows/tests.yml

Esto permite validar automáticamente el funcionamiento de la API en cada cambio realizado en el repositorio.
 Tecnologías Utilizadas

- Python
- FastAPI
- Scikit-learn
- Jinja2
- Docker
- GitHub Actions
- Terraform
- Kubernetes
- Pytest

---

# Repositorio

Proyecto disponible en:

https://github.com/silvitagomez572-alt/hospital-triage-ia

---

# Aviso

Este sistema es un **prototipo académico desarrollado con fines educativos** y **no reemplaza el criterio clínico profesional**.
