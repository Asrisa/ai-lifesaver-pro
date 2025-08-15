import os, json
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import SymptomInput, ConditionAssessment, TTSRequest
from chains import build_condition_chain
from tools.hospitals import nearby_hospitals
from tools.tts import tts_to_mp3_bytes
from tools.weather import current_weather

load_dotenv()

app = FastAPI(title="Med Assist Backend", version="0.2.0")

# CORS for your Gradio front-end
origins = (os.getenv("ALLOWED_ORIGINS") or "").split(",")
origins = [o.strip() for o in origins if o.strip()]
if not origins:
    origins = ["*"]  # loosen during dev only

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangChain chain
condition_chain = build_condition_chain()

def _fallback_city_country():
    return os.getenv("DEFAULT_CITY") or "Unknown", os.getenv("DEFAULT_COUNTRY") or "Unknown"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze", response_model=ConditionAssessment)
async def analyze(sym: SymptomInput):
    age = sym.user.age if sym.user and sym.user.age else ""
    gender = sym.user.gender if sym.user and sym.user.gender else ""
    city = (sym.user.city if sym.user and sym.user.city else None)
    country = (sym.user.country if sym.user and sym.user.country else None)
    if not city or not country:
        city, country = _fallback_city_country()

    raw = await condition_chain.ainvoke({
        "symptoms": sym.symptoms,
        "age": age,
        "gender": gender,
        "city": city,
        "country": country,
    })
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model did not return valid JSON")

    return ConditionAssessment(**data)

@app.post("/hospitals")
async def hospitals(sym: SymptomInput):
    if not sym.user or sym.user.latitude is None or sym.user.longitude is None:
        raise HTTPException(status_code=400, detail="latitude/longitude required")
    hos = await nearby_hospitals(sym.user.latitude, sym.user.longitude)
    return {"hospitals": hos}

@app.post("/assist", response_model=ConditionAssessment)
async def assist(sym: SymptomInput):
    assessment: ConditionAssessment = await analyze(sym)

    lat = sym.user.latitude if sym.user else None
    lon = sym.user.longitude if sym.user else None

    if lat is not None and lon is not None:
        assessment.nearest_hospitals = await nearby_hospitals(lat, lon)
        try:
            assessment.weather_context = await current_weather(lat, lon)
        except Exception:
            assessment.weather_context = None

    return assessment

@app.post("/tts")
async def tts(req: TTSRequest):
    try:
        audio_bytes = tts_to_mp3_bytes(req.text, voice=(req.voice or "alloy"))
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
