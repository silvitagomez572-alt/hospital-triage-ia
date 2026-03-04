import warnings
warnings.filterwarnings("ignore")


from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path
import os
import json
import uuid
import tempfile
import fcntl
import glob

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

# ML
import joblib
import numpy as np


# ============================================================
# TIMEZONE (Argentina)
# ============================================================
AR_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


# ============================================================
# PATHS BASE
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"
REGISTROS_PATH = DATA_DIR / "registros.json"
LOCK_PATH = DATA_DIR / "registros.lock"
MODEL_DIR = BASE_DIR / "model"  # api/model


# ============================================================
# APP
# ============================================================
app = FastAPI(title="Hospital Triage API", version="1.0.0")

# CORS (desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ============================================================
# DATA (JSON local)
# ============================================================
os.makedirs(DATA_DIR, exist_ok=True)

if not REGISTROS_PATH.exists():
    with open(REGISTROS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)


# ============================================================
# MANCHESTER
# ============================================================
MANCHESTER_MINUTES = {
    "ROJO": 0,
    "NARANJA": 10,
    "AMARILLO": 60,
    "VERDE": 120,
    "AZUL": 240,
    "NEGRO": 0,
}

MANCHESTER_PRIORIDAD = {
    "ROJO": 1,
    "NARANJA": 2,
    "AMARILLO": 3,
    "VERDE": 4,
    "AZUL": 5,
    "NEGRO": 6,
}

MANCHESTER_LABELS = {
    "ROJO": "Rojo (Inmediato)",
    "NARANJA": "Naranja (Muy urgente)",
    "AMARILLO": "Amarillo (Urgente)",
    "VERDE": "Verde (Poco urgente)",
    "AZUL": "Azul (No urgente)",
    "NEGRO": "Negro (Óbito/Expectante)",
}


# ============================================================
# HELPERS
# ============================================================
def now_iso() -> str:
    """Fecha/hora local Argentina en ISO."""
    return datetime.now(AR_TZ).isoformat(timespec="seconds")


def parse_dt(s: str) -> Optional[datetime]:
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=AR_TZ)
        return dt
    except Exception:
        return None


def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        s = str(x).strip().replace(",", ".")
        if s == "":
            return None
        return float(s)
    except Exception:
        return None


# ============================================================
# ML: cargar modelo pkl
# ============================================================
_MODEL = None
_MODEL_PATH_USED: Optional[str] = None

FEATURES = ["temperatura", "frecuencia_respiratoria", "spo2", "fc", "pas", "dolor"]
VALID_ML_CLASSES = {"VERDE", "AMARILLO", "ROJO"}


def _find_latest_model_path() -> Optional[str]:
    pattern = str(MODEL_DIR / "triage_model_*.pkl")
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort()
    return files[-1]


def get_model() -> Tuple[Any, Optional[str]]:
    global _MODEL, _MODEL_PATH_USED
    if _MODEL is not None:
        return _MODEL, _MODEL_PATH_USED

    path = _find_latest_model_path()
    if not path:
        return None, None

    try:
        _MODEL = joblib.load(path)
        _MODEL_PATH_USED = path
        return _MODEL, _MODEL_PATH_USED
    except Exception as e:
        print(f"[WARN] No se pudo cargar modelo: {e}")
        return None, None


def predict_triage_ml(form: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve:
      {"ok": bool, "pred": str|None, "proba": float|None, "model_path": str|None, "missing": list}
    """
    model, path = get_model()
    if model is None:
        return {"ok": False, "pred": None, "proba": None, "model_path": None, "missing": FEATURES[:]}

    x: List[float] = []
    missing: List[str] = []

    for k in FEATURES:
        v = _to_float(form.get(k))
        if v is None:
            missing.append(k)
            v = 0.0
        x.append(v)

    try:
        X = np.array([x], dtype=float)
        pred = model.predict(X)[0]
        pred = str(pred).strip().upper()

        proba = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            classes = [str(c).strip().upper() for c in getattr(model, "classes_", [])]
            if classes and pred in classes:
                idx = classes.index(pred)
                proba = round(float(probs[idx]) * 100.0, 2)

        if pred not in VALID_ML_CLASSES:
            return {"ok": False, "pred": None, "proba": None, "model_path": path, "missing": missing}

        return {"ok": True, "pred": pred, "proba": proba, "model_path": path, "missing": missing}

    except Exception as e:
        print(f"[WARN] Error en predict ML: {e}")
        return {"ok": False, "pred": None, "proba": None, "model_path": path, "missing": missing}


# ============================================================
# DEMO score (fallback)
# ============================================================
def demo_score(form: Dict[str, Any]) -> int:
    score = 0

    t = _to_float(form.get("temperatura"))
    fr = _to_float(form.get("frecuencia_respiratoria"))
    spo2 = _to_float(form.get("spo2"))
    fc = _to_float(form.get("fc"))
    pas = _to_float(form.get("pas"))
    pad = _to_float(form.get("pad"))  # opcional
    dolor = _to_float(form.get("dolor"))

    # SpO2
    if spo2 is not None:
        if spo2 < 90:
            score += 5
        elif spo2 <= 91:
            score += 4
        elif spo2 <= 93:
            score += 2
        elif spo2 == 94:
            score += 1

    # Frecuencia respiratoria
    if fr is not None:
        if fr >= 36:
            score += 4
        elif fr >= 30:
            score += 3
        elif fr >= 24:
            score += 1

    # Frecuencia cardiaca
    if fc is not None:
        if fc >= 140:
            score += 3
        elif fc >= 120:
            score += 2
        elif fc >= 100:
            score += 1

    # PAS
    if pas is not None:
        if pas < 90:
            score += 4
        elif pas <= 100:
            score += 2
        elif pas <= 110:
            score += 1

    # PAD (opcional)
    if pad is not None and pad < 60:
        score += 1

    # Temperatura
    if t is not None:
        if t >= 40:
            score += 3
        elif t >= 39:
            score += 2
        elif t >= 38:
            score += 1
        elif t <= 35:
            score += 3

    # Dolor
    if dolor is not None:
        if dolor >= 9:
            score += 2
        elif dolor >= 7:
            score += 1

    return score


def demo_probabilidad(score: int) -> float:
    return round(min(score / 12.0, 1.0) * 100.0, 2)


def sugerir_manchester_demo(score: int, form: Dict[str, Any]) -> str:
    """Reglas demo más consistentes."""
    t = _to_float(form.get("temperatura"))
    fr = _to_float(form.get("frecuencia_respiratoria"))
    spo2 = _to_float(form.get("spo2"))
    fc = _to_float(form.get("fc"))
    pas = _to_float(form.get("pas"))

    # Disparadores ROJO
    if spo2 is not None and spo2 <= 90:
        return "ROJO"
    if pas is not None and pas < 90:
        return "ROJO"
    if fr is not None and fr >= 36:
        return "ROJO"
    if t is not None and (t >= 40 or t <= 35):
        return "ROJO"
    if fc is not None and fc >= 140:
        return "ROJO"

    # Score
    if score >= 6:
        return "AMARILLO"
    return "VERDE"


# ============================================================
# REGISTROS / LOCK
# ============================================================
def load_registros_unlocked() -> List[dict]:
    try:
        with open(REGISTROS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_registros_atomic_unlocked(data: List[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="registros_", suffix=".json", dir=str(DATA_DIR))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, str(REGISTROS_PATH))
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def with_file_lock(fn):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOCK_PATH, "a", encoding="utf-8") as lockf:
        fcntl.flock(lockf.fileno(), fcntl.LOCK_EX)
        try:
            return fn()
        finally:
            fcntl.flock(lockf.fileno(), fcntl.LOCK_UN)


def append_registro(registro: dict) -> None:
    def _do():
        data = load_registros_unlocked()
        data.append(registro)
        save_registros_atomic_unlocked(data)
    with_file_lock(_do)


def enriquecer_registro(r: dict) -> dict:
    # No re-generar ID si ya existe
    r.setdefault("id", str(uuid.uuid4()))

    inicio = parse_dt(r.get("hora_inicio") or r.get("fecha") or "")
    color = (r.get("manchester", {}).get("color_final") or r.get("manchester_color_final") or "VERDE").upper()
    minutos_max = MANCHESTER_MINUTES.get(color, 120)

    r["manchester_color_final"] = color
    r["manchester_minutes"] = minutos_max
    r["prioridad_num"] = MANCHESTER_PRIORIDAD.get(color, 4)

    if inicio:
        limite = inicio + timedelta(minutes=minutos_max)
        ahora = datetime.now(AR_TZ)
        transcurrido = int((ahora - inicio).total_seconds() // 60)

        r["hora_inicio"] = inicio.isoformat(timespec="seconds")
        r["hora_limite"] = limite.isoformat(timespec="seconds")
        r["tiempo_transcurrido_min"] = transcurrido
        r["estado_manchester"] = "VENCIDO" if ahora > limite else "EN_TIEMPO"
    else:
        r["hora_limite"] = None
        r["tiempo_transcurrido_min"] = None
        r["estado_manchester"] = "SIN_HORA"

    r.setdefault("cerrado", False)
    return r


def load_registros_enriquecidos() -> List[dict]:
    def _do():
        data = load_registros_unlocked()
        return [enriquecer_registro(r) for r in data]
    return with_file_lock(_do)


# ============================================================
# RUTAS
# ============================================================
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/triage")


@app.get("/triage", include_in_schema=False)
async def triage_form(request: Request):
    manchester_options = [
        {"value": k, "label": MANCHESTER_LABELS[k], "minutes": MANCHESTER_MINUTES[k]}
        for k in ["ROJO", "NARANJA", "AMARILLO", "VERDE", "AZUL", "NEGRO"]
    ]
    return templates.TemplateResponse(
        "triage_form.html",
        {"request": request, "manchester_options": manchester_options},
    )


@app.post("/predict_ml", include_in_schema=False)
async def predict_json(payload: Dict[str, Any] = Body(...)):
    ml = predict_triage_ml(payload)

    score = demo_score(payload)
    prob_demo = demo_probabilidad(score)
    sugerido_demo = sugerir_manchester_demo(score, payload)
    sugerido_final = ml["pred"] if ml["ok"] else sugerido_demo

    return {
        "sugerido_final": sugerido_final,
        "usado": "ml" if ml["ok"] else "demo",
        "ml": ml,
        "demo": {"score": score, "probabilidad": prob_demo, "sugerido": sugerido_demo},
    }


@app.post("/triage/predict", include_in_schema=False)
async def triage_predict(request: Request):
    form = dict(await request.form())

    profesional = (form.get("profesional") or "").strip()
    rol = (form.get("rol") or "ENFERMERIA").strip().upper()
    elegido = (form.get("manchester_color") or "").strip().upper()

    ml = predict_triage_ml(form)

    score = demo_score(form)
    prob_demo = demo_probabilidad(score)
    sugerido_demo = sugerir_manchester_demo(score, form)
    sugerido_final = ml["pred"] if ml["ok"] else sugerido_demo

    manchester_color_final = elegido if elegido in MANCHESTER_MINUTES else sugerido_final
    manchester_wait = MANCHESTER_MINUTES.get(manchester_color_final, 120)

    now = now_iso()

    registro = {
        "id": str(uuid.uuid4()),
        "hora_inicio": now,
        "firma_digital": {
            "usuario": profesional,
            "rol": rol,
            "fecha_hora": now,
            "leyenda": "Documento de uso asistencial – no reemplaza criterio médico.",
        },
        "manchester": {
            "color_final": manchester_color_final,
            "minutos_max": manchester_wait,
            "label": MANCHESTER_LABELS.get(manchester_color_final, manchester_color_final),
            "color_elegido": elegido if elegido else None,
            "color_sugerido_demo": sugerido_demo,
            "color_sugerido_ml": ml["pred"] if ml["ok"] else None,
        },
        "fecha": now,
        "demo": {"score": score, "probabilidad": prob_demo},
        "ml": {
            "ok": ml["ok"],
            "pred": ml["pred"],
            "probabilidad": ml["proba"],
            "model_path": ml["model_path"],
            "missing": ml.get("missing", []),
        },
        "datos": form,
        "cerrado": False,
    }

    append_registro(registro)

    return templates.TemplateResponse(
        "triage_result.html",
        {"request": request, "registro": registro},
    )


@app.get("/triage/ver/{triage_id}", include_in_schema=False)
async def triage_ver(request: Request, triage_id: str):
    data = load_registros_enriquecidos()
    registro = next((r for r in data if r.get("id") == triage_id), None)
    if not registro:
        return HTMLResponse("<h2>No se encontró el triage</h2>", status_code=404)

    return templates.TemplateResponse(
        "triage_result.html",
        {"request": request, "registro": registro},
    )


@app.get("/registros", include_in_schema=False)
async def ver_registros(request: Request):
    data = load_registros_enriquecidos()
    data_sorted = sorted(data, key=lambda x: x.get("hora_inicio") or x.get("fecha") or "")
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "registros": data_sorted},
    )


@app.get("/directivos", response_class=HTMLResponse, include_in_schema=False)
async def directivos(request: Request):
    data = load_registros_enriquecidos()

    colores = ["ROJO", "NARANJA", "AMARILLO", "VERDE", "AZUL", "NEGRO"]
    por_color = {c: 0 for c in colores}
    vencidos = 0

    tipos_acc: List[str] = []
    lugares_int: List[str] = []
    tiempos: List[int] = []

    for r in data:
        c = (r.get("manchester_color_final") or "VERDE").upper()
        por_color[c] = por_color.get(c, 0) + 1

        if r.get("estado_manchester") == "VENCIDO":
            vencidos += 1

        t = r.get("tiempo_transcurrido_min")
        if isinstance(t, (int, float)):
            tiempos.append(int(t))

        d = r.get("datos") or {}
        ta = (d.get("tipo_accidente") or "").strip()
        if ta:
            tipos_acc.append(ta)

        li = (d.get("lugar_internacion") or "").strip()
        if li:
            lugares_int.append(li)

    por_tipo_accidente = dict(Counter(tipos_acc))
    por_lugar_internacion = dict(Counter(lugares_int))

    siniestros_total = sum(por_tipo_accidente.values())
    internaciones_total = sum(por_lugar_internacion.values())

    promedio_tiempo = round(sum(tiempos) / len(tiempos), 1) if tiempos else ""

    vencidos_list = [r for r in data if r.get("estado_manchester") == "VENCIDO"]
    top_vencidos = sorted(
        vencidos_list,
        key=lambda x: x.get("tiempo_transcurrido_min") or 0,
        reverse=True
    )[:5]

    return templates.TemplateResponse(
        "directivos.html",
        {
            "request": request,
            "total": len(data),
            "por_color": por_color,
            "vencidos": vencidos,
            "promedio_tiempo": promedio_tiempo,
            "siniestros_total": siniestros_total,
            "internaciones_total": internaciones_total,
            "por_tipo_accidente": por_tipo_accidente,
            "por_lugar_internacion": por_lugar_internacion,
            "top_vencidos": top_vencidos,
        },
    )


@app.get("/medico", response_class=HTMLResponse, include_in_schema=False)
async def medico(request: Request):
    data = load_registros_enriquecidos()
    abiertos = [r for r in data if not r.get("cerrado")]
    abiertos_sorted = sorted(
        abiertos,
        key=lambda x: (x.get("prioridad_num", 99), x.get("hora_inicio") or ""),
        reverse=False,
    )
    return templates.TemplateResponse(
        "medico.html",
        {"request": request, "registros": abiertos_sorted},
    )


@app.post("/cerrar/{triage_id}", include_in_schema=False)
async def cerrar(triage_id: str):
    def _do():
        data = load_registros_unlocked()
        for r in data:
            if r.get("id") == triage_id:
                r["cerrado"] = True
                r["cerrado_en"] = now_iso()
        save_registros_atomic_unlocked(data)

    with_file_lock(_do)
    return RedirectResponse(url="/medico", status_code=303)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok", "time": now_iso()}


@app.get("/health")
def health():
    return {"status": "ok"}


# --- API JSON (para tests y para integración) ---
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    pain_level: int = Field(..., ge=0, le=10)
    systolic_bp: int = Field(..., ge=0, le=300)
    diastolic_bp: int = Field(..., ge=0, le=200)
    heart_rate: int = Field(..., ge=0, le=250)
    temperature: float = Field(..., ge=25.0, le=45.0)

@app.post("/predict_full")
def predict_api(payload: PredictRequest):
    """
    Endpoint JSON mínimo para validación automática.
    Devuelve un nivel de riesgo + probabilidad.
    """
    # Regla simple (suficiente para tests y para no romper tu flujo HTML)
    score = 0
    if payload.systolic_bp < 90:
        score += 2
    if payload.heart_rate >= 110:
        score += 1
    if payload.pain_level >= 8:
        score += 1
    if payload.temperature >= 38.0:
        score += 1
    if payload.age >= 65:
        score += 1

    if score >= 4:
        risk_level, probability = "high", 0.9
    elif score >= 2:
        risk_level, probability = "medium", 0.6
    else:
        risk_level, probability = "low", 0.2

    return {"risk_level": risk_level, "probability": probability}

# --- /predict JSON simple (para tests) ---
from pydantic import BaseModel, Field

class PredictRequestTest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    pain_level: int = Field(..., ge=0, le=10)
    systolic_bp: int = Field(..., ge=0, le=300)
    diastolic_bp: int = Field(..., ge=0, le=200)
    heart_rate: int = Field(..., ge=0, le=250)
    temperature: float = Field(..., ge=25.0, le=45.0)

@app.post("/predict")
def predict_for_tests(payload: PredictRequestTest):
    logger.info(f"Predict request: age={payload.age}, pain={payload.pain_level}")
    score = 0
    if payload.systolic_bp < 90:
        score += 2
    if payload.heart_rate >= 110:
        score += 1
    if payload.pain_level >= 8:
        score += 1
    if payload.temperature >= 38.0:
        score += 1
    if payload.age >= 65:
        score += 1

    if score >= 4:
        return {"risk_level": "high", "probability": 0.9}
    if score >= 2:
        return {"risk_level": "medium", "probability": 0.6}
    return {"risk_level": "low", "probability": 0.2}
