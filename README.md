# Hospital Triage IA – Trabajo Final Integrador (Infraestructura Tecnológica para IA)

## Objetivo
Diseñar, implementar y dockerizar una API de inferencia en Python que sirva un modelo de Machine Learning,
incluyendo trazabilidad, métricas operativas y preparación para despliegue en Kubernetes (GKE).

## Descripción del proyecto
Sistema de priorización de pacientes basado en Manchester Triage con soporte ML (modelo .pkl).
Incluye panel para directivos con indicadores reales: distribución por color, vencimientos, promedios de tiempo,
siniestros e internaciones.

## Arquitectura (mínima requerida)
- **API (Serving):** FastAPI + Jinja2 (paneles)
- **Modelo ML:** serializado en `.pkl` (versionado por timestamp)
- **Training service:** scripts para entrenamiento/evaluación/versionado (carpeta `training/`)
- **Persistencia:** JSON local con file-lock (prototipo trazable)

## Endpoints principales
- `GET /health` → health check
- `GET /triage` → formulario
- `POST /triage/predict` → inferencia + registro
- `GET /directivos` → panel de métricas
- `GET /medico` → panel operativo

## Cómo correr en local (Docker Compose)
```bash
cd api
docker compose up --build


## Accesos (una vez levantado el servicio)

- Triage (formulario):  
  http://localhost:8001/triage

- Panel Directivos (métricas y vencimientos):  
  http://localhost:8001/directivos

- Panel Médico (vista operativa):  
  http://localhost:8001/medico

- Health check del servicio:  
  http://localhost:8001/health
