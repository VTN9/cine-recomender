"""
CineMatch AI - Recomendador Local de Películas y Series
Desarrollado con FastAPI y OpenRouter API.
"""

import os
import json
import re
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Carga de variables de entorno
ENV_PATH = Path(__file__).parent / ".env"
if not ENV_PATH.exists():
    ENV_PATH.write_text("OPENROUTER_API_KEY=\nOPENROUTER_MODEL=minimax/minimax-m3.1-flash:free\nTMDB_API_KEY=\n", encoding="utf-8")

load_dotenv(dotenv_path=ENV_PATH, override=True)

app = FastAPI(title="CineMatch AI", description="Recomendador inteligente de cine y series con OpenRouter")

# CORS para desarrollo local flexible
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Modelos disponibles en OpenRouter (incluyendo opciones 100% gratuitas comprobadas)
DEFAULT_MODELS = [
    {"id": "minimax/minimax-m3.1-flash:free", "name": "Minimax M3.1 Flash (Gratuito / Rápido)", "free": True},
    {"id": "nvidia/nemotron-3.5-lightning:free", "name": "Nvidia Nemotron 3.5 Lightning (Gratuito)", "free": True},
    {"id": "google/gemma-4-26b-a4b-it:free", "name": "Google Gemma 4 (Gratuito)", "free": True},
    {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B (De Pago / Saldo OpenRouter)", "free": False},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat (De Pago / Saldo OpenRouter)", "free": False},
    {"id": "google/gemini-2.5-flash", "name": "Google Gemini 2.5 Flash (De Pago)", "free": False}
]

# Catálogo local de respaldo y tendencias enriquecido por plataforma
CURATED_CATALOG = [
    {
        "id": 1,
        "title": "Interstellar",
        "original_title": "Interstellar",
        "year": 2014,
        "type": "Película",
        "duration": "2h 49m",
        "director": "Christopher Nolan",
        "rating": 8.7,
        "genres": ["Ciencia Ficción", "Drama", "Aventura"],
        "platforms": ["Max", "Movistar+"],
        "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
        "hook": "Un viaje épico más allá de las estrellas para salvar a la humanidad.",
        "synopsis": "Un equipo de exploradores viaja a través de un agujero de gusano en el espacio en un intento por asegurar la supervivencia de la especie humana.",
        "mood_tags": ["Mente explotada", "Emocionante", "Ciencia Rigurosa"]
    },
    {
        "id": 2,
        "title": "Severance",
        "original_title": "Severance",
        "year": 2022,
        "type": "Serie",
        "duration": "2 Temporadas",
        "director": "Dan Erickson & Ben Stiller",
        "rating": 8.7,
        "genres": ["Suspense", "Ciencia Ficción", "Misterio"],
        "platforms": ["Apple TV+"],
        "poster": "https://image.tmdb.org/t/p/w500/pPHpeIql5LkdJ4R1kR5TyG93cQl.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/9hpGA2m1953x3h00o9eF1m1p1qY.jpg",
        "hook": "¿Y si tus recuerdos laborales estuvieran totalmente separados de tu vida personal?",
        "synopsis": "Mark lidera un equipo de oficinistas cuyos recuerdos han sido divididos quirúrgicamente entre su trabajo y su vida personal.",
        "mood_tags": ["Distopía", "Tensión Psicológica", "Giro Inesperado"]
    },
    {
        "id": 3,
        "title": "Puñales por la espalda (Knives Out)",
        "original_title": "Knives Out",
        "year": 2019,
        "type": "Película",
        "duration": "2h 10m",
        "director": "Rian Johnson",
        "rating": 7.9,
        "genres": ["Comedia", "Crimen", "Misterio"],
        "platforms": ["Netflix", "Prime Video"],
        "poster": "https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/Ab8mkHmkYADjU7wQiOkia99GQI.jpg",
        "hook": "Un detective extravagante investiga la extraña muerte de un patriarca millonario.",
        "synopsis": "Cuando el renombrado novelista de misterio Harlan Thrombey es encontrado muerto en su mansión, el detective Benoit Blanc es misteriosamente reclutado.",
        "mood_tags": ["Diversión", "Whodunit", "Para ver en pareja"]
    },
    {
        "id": 4,
        "title": "The Bear",
        "original_title": "The Bear",
        "year": 2022,
        "type": "Serie",
        "duration": "3 Temporadas",
        "director": "Christopher Storer",
        "rating": 8.6,
        "genres": ["Drama", "Comedia"],
        "platforms": ["Disney+"],
        "poster": "https://image.tmdb.org/t/p/w500/r3A70R5OqMhG9vYQ4J1J9a5D8vY.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/mQ93Zq2N02m2a7dF5B0sF6y7a5b.jpg",
        "hook": "Adrenalina pura entre fogones con una de las mejores interpretaciones de la década.",
        "synopsis": "Carmy, un joven chef de alta cocina, regresa a Chicago para administrar el negocio de sándwiches de su familia tras una pérdida personal.",
        "mood_tags": ["Adrenalina", "Intenso", "Gastronomía"]
    },
    {
        "id": 5,
        "title": "Dune: Parte Dos",
        "original_title": "Dune: Part Two",
        "year": 2024,
        "type": "Película",
        "duration": "2h 46m",
        "director": "Denis Villeneuve",
        "rating": 8.6,
        "genres": ["Ciencia Ficción", "Aventura", "Acción"],
        "platforms": ["Max", "Movistar+"],
        "poster": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/xOMo8BRK7PfcJv9JCnx7s520DRq.jpg",
        "hook": "La venganza mesiánica y la guerra total por el control del planeta Arrakis.",
        "synopsis": "Paul Atreides se une a Chani y los Fremen mientras busca venganza contra los conspiradores que destruyeron a su familia.",
        "mood_tags": ["Espectáculo Visual", "Épica", "Ciencia Ficción"]
    },
    {
        "id": 6,
        "title": "La sociedad de la nieve",
        "original_title": "Society of the Snow",
        "year": 2023,
        "type": "Película",
        "duration": "2h 24m",
        "director": "J.A. Bayona",
        "rating": 7.9,
        "genres": ["Aventura", "Drama", "Historia"],
        "platforms": ["Netflix"],
        "poster": "https://image.tmdb.org/t/p/w500/2rHg9vdR7pE5a5gK0f9wA5u5XyZ.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/5a4Jdoon0RJ2V8vB5D8vY6n9m4q.jpg",
        "hook": "La conmovedora historia real de supervivencia del equipo de rugby en los Andes.",
        "synopsis": "En 1972, un vuelo procedente de Uruguay se estrella en el corazón de los Andes. Solo 29 de los 45 pasajeros sobreviven al impacto.",
        "mood_tags": ["Supervivencia", "Para reflexionar", "Emoción pura"]
    },
    {
        "id": 7,
        "title": "Shōgun",
        "original_title": "Shōgun",
        "year": 2024,
        "type": "Serie",
        "duration": "1 Temporada",
        "director": "Rachel Kondo & Justin Marks",
        "rating": 8.7,
        "genres": ["Drama", "Historia", "Guerra"],
        "platforms": ["Disney+"],
        "poster": "https://image.tmdb.org/t/p/w500/7O4iVfOMQmdCSxhOg1WNzG1AgYT.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/5zmiBoMzeWKVc6FNiVqVG9vDlvq.jpg",
        "hook": "Intriga política, honor samurái y guerra civil en el Japón feudal del siglo XVII.",
        "synopsis": "Lord Toranaga lucha por su supervivencia mientras sus enemigos en el Consejo de Regentes se unen contra él en el Japón del año 1600.",
        "mood_tags": ["Épica Histórica", "Estrategia", "Obra Maestra"]
    },
    {
        "id": 8,
        "title": "Fallout",
        "original_title": "Fallout",
        "year": 2024,
        "type": "Serie",
        "duration": "1 Temporada",
        "director": "Jonathan Nolan & Lisa Joy",
        "rating": 8.4,
        "genres": ["Ciencia Ficción", "Acción", "Aventura"],
        "platforms": ["Prime Video"],
        "poster": "https://image.tmdb.org/t/p/w500/AnsZu4Z9m219fQv9l5sH1rE2d0z.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/2u0v8E8X2L5Q2p9l8F8d8z9L0Z.jpg",
        "hook": "Un páramo postapocalíptico desquiciado, sangriento y rebosante de humor retro-futurista.",
        "synopsis": "Lucy sale de su refugio subterráneo antinuclear por primera vez para aventurarse en el devastado y hostil desierto de Los Ángeles.",
        "mood_tags": ["Postapocalíptico", "Humor Negro", "Aventura"]
    },
    {
        "id": 9,
        "title": "The Last of Us",
        "original_title": "The Last of Us",
        "year": 2023,
        "type": "Serie",
        "duration": "1 Temporada",
        "director": "Craig Mazin & Neil Druckmann",
        "rating": 8.8,
        "genres": ["Drama", "Ciencia Ficción", "Terror"],
        "platforms": ["Max"],
        "poster": "https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2V7JMrRI.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/uDgy6hyPd82kOHh6I95FLtLnj6p.jpg",
        "hook": "Un superviviente endurecido debe escoltar a una niña de 14 años que podría ser la cura de la humanidad.",
        "synopsis": "20 años después de que una pandemia fúngica arrase la civilización, Joel es contratado para sacar clandestinamente a Ellie de una zona de cuarentena.",
        "mood_tags": ["Emotivo", "Tensión", "Supervivencia"]
    },
    {
        "id": 10,
        "title": "Anatomía de una caída",
        "original_title": "Anatomie d'une chute",
        "year": 2023,
        "type": "Película",
        "duration": "2h 31m",
        "director": "Justine Triet",
        "rating": 7.8,
        "genres": ["Drama", "Crimen", "Misterio"],
        "platforms": ["Filmin", "Movistar+"],
        "poster": "https://image.tmdb.org/t/p/w500/kQs6iqtsJgeDYY2v90iO0yQ86u5.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/v5X2jFfK6w8X9Y1M1F2J5o7Z8X9.jpg",
        "hook": "¿Accidente, suicidio o asesinato? Un juicio matrimonial que disecciona la verdad con bisturí.",
        "synopsis": "Una mujer es sospechosa del asesinato de su marido en un aislado chalet en los Alpes. Su hijo ciego es el único testigo del caso.",
        "mood_tags": ["Cine de Autor", "Drama Judicial", "Para reflexionar"]
    },
    {
        "id": 11,
        "title": "Ted Lasso",
        "original_title": "Ted Lasso",
        "year": 2020,
        "type": "Serie",
        "duration": "3 Temporadas",
        "director": "Jason Sudeikis & Bill Lawrence",
        "rating": 8.8,
        "genres": ["Comedia", "Drama", "Deportes"],
        "platforms": ["Apple TV+"],
        "poster": "https://image.tmdb.org/t/p/w500/2MuYQf7p0f2Y2a6k0h0k5o0k5o0.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/3MuYQf7p0f2Y2a6k0h0k5o0k5o0.jpg",
        "hook": "El entrenador universitario más optimista de EE.UU. aterriza en la Premier League inglesa.",
        "synopsis": "Un entrenador de fútbol americano es contratado para dirigir a un equipo de fútbol profesional británico, a pesar de no tener experiencia alguna en el deporte.",
        "mood_tags": ["Sentirse Bien (Feel-Good)", "Risas", "Optimismo"]
    },
    {
        "id": 12,
        "title": "Stranger Things",
        "original_title": "Stranger Things",
        "year": 2016,
        "type": "Serie",
        "duration": "4 Temporadas",
        "director": "The Duffer Brothers",
        "rating": 8.7,
        "genres": ["Ciencia Ficción", "Terror", "Misterio"],
        "platforms": ["Netflix"],
        "poster": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/56v2KjUmLeLo5aMw79Ykt9iQWb2.jpg",
        "hook": "Nostalgia ochentera, experimentos secretos y una dimensión paralela aterradora en Hawkins.",
        "synopsis": "Cuando un niño desaparece, sus amigos, la familia y el sheriff local se ven envueltos en un extraordinario misterio que involucra experimentos gubernamentales de alto secreto.",
        "mood_tags": ["Aventura Juvenil", "Ochentas", "Sobrenatural"]
    }
]


# Pydantic Models
class ConfigUpdate(BaseModel):
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    tmdb_api_key: Optional[str] = None

class RecommendationRequest(BaseModel):
    prompt: str
    platform: Optional[str] = "Todas"
    content_type: Optional[str] = "both"  # "movie", "tv", "both"
    mood: Optional[str] = "cualquiera"
    model: Optional[str] = None

class CoupleMatchRequest(BaseModel):
    user1_preferences: str
    user2_preferences: str
    platform: Optional[str] = "Todas"


def extract_json_from_text(text: str) -> dict:
    """Extrae de forma robusta un objeto JSON de respuestas con razonamiento o markdown"""
    # Eliminar bloques de razonamiento si existen (<think>...</think>)
    text_clean = re.sub(r'<think>[\s\S]*?</think>', '', text)
    # Buscar el primer bloque entre { y }
    match = re.search(r'(\{[\s\S]*\})', text_clean)
    if match:
        candidate = match.group(1).strip()
        return json.loads(candidate)
    return json.loads(text_clean.strip())


@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"message": "Frontend en desarrollo"})
    return FileResponse(index_file)


@app.get("/api/config")
async def get_config():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    active_model = os.getenv("OPENROUTER_MODEL", "minimax/minimax-m3.1-flash:free").strip()
    has_tmdb = bool(os.getenv("TMDB_API_KEY", "").strip())
    
    return {
        "has_openrouter_key": bool(api_key),
        "key_preview": f"...{api_key[-4:]}" if len(api_key) > 6 else "",
        "active_model": active_model,
        "models": DEFAULT_MODELS,
        "has_tmdb_key": has_tmdb
    }


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    if config.openrouter_api_key is not None:
        key = config.openrouter_api_key.strip()
        os.environ["OPENROUTER_API_KEY"] = key
        set_key(str(ENV_PATH), "OPENROUTER_API_KEY", key)
    
    if config.openrouter_model is not None:
        model = config.openrouter_model.strip()
        os.environ["OPENROUTER_MODEL"] = model
        set_key(str(ENV_PATH), "OPENROUTER_MODEL", model)
        
    if config.tmdb_api_key is not None:
        tmdb = config.tmdb_api_key.strip()
        os.environ["TMDB_API_KEY"] = tmdb
        set_key(str(ENV_PATH), "TMDB_API_KEY", tmdb)
        
    return {"status": "ok", "message": "Configuración guardada correctamente en tu equipo."}


@app.get("/api/trending")
async def get_trending(platform: str = "Todas"):
    """Devuelve títulos destacados filtrados por plataforma o todas"""
    if not platform or platform == "Todas":
        return {"items": CURATED_CATALOG}
    
    p_norm = platform.strip().lower()
    filtered = [
        item for item in CURATED_CATALOG
        if any(p_norm in plat.lower() for plat in item.get("platforms", []))
    ]
    return {"items": filtered}


import urllib.parse

# Cadena ordenada de modelos gratuitos fiables de respaldo en OpenRouter
FREE_FALLBACK_CHAIN = [
    "minimax/minimax-m3.1-flash:free",
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "recursive/flint-v1.0:free"
]


async def query_openrouter_with_auto_fallback(
    api_key: str, 
    requested_model: str, 
    messages: list, 
    temperature: float = 0.6
) -> tuple[str, str, bool]:
    """
    Envía la consulta a OpenRouter. Si el modelo preferido se agota (HTTP 429),
    da error 404, 402 (sin saldo) o 503, cambia AUTOMÁTICAMENTE al siguiente
    modelo gratuito de la lista hasta encontrar uno disponible.
    Devuelve: (contenido_respuesta, modelo_usado, se_uso_fallback).
    """
    # Lista de modelos a intentar: primero el solicitado, luego el resto de gratuitos
    models_to_try = [requested_model]
    for m in FREE_FALLBACK_CHAIN:
        if m not in models_to_try:
            models_to_try.append(m)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "CineMatch AI Recommender",
        "Content-Type": "application/json"
    }

    last_error = ""

    async with httpx.AsyncClient(timeout=35.0) as client:
        for idx, model_name in enumerate(models_to_try):
            try:
                payload = {
                    "model": model_name,
                    # Respaldo secundario automático dentro del propio OpenRouter
                    "models": [model_name] + [m for m in FREE_FALLBACK_CHAIN if m != model_name],
                    "messages": messages,
                    "temperature": temperature
                }

                resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        content = choices[0]["message"]["content"]
                        actual_model = data.get("model", model_name)
                        used_fallback = (idx > 0)
                        if used_fallback:
                            print(f"🔄 [Auto-Fallback Activo] Modelo inicial no disponible. Respuesta generada con éxito por: {actual_model}")
                        else:
                            print(f"✅ Respuesta exitosa generada con: {actual_model}")
                        return content, actual_model, used_fallback

                # Si falló (ej: 429 límite alcanzado, 402 sin créditos, 404 retirado, 503 sobrecarga)
                err_text = resp.text
                print(f"⚠️ Modelo '{model_name}' dio HTTP {resp.status_code} ({err_text[:80]}...). Probando siguiente modelo gratuito...")
                last_error = f"HTTP {resp.status_code}: {err_text[:120]}"

            except (httpx.TimeoutException, httpx.RequestError) as ex:
                print(f"⚠️ Timeout/Red con '{model_name}': {ex}. Cambiando a otro modelo gratuito...")
                last_error = str(ex)

    raise HTTPException(
        status_code=503, 
        detail=f"Todos los modelos gratuitos de OpenRouter están temporalmente saturados. Detalle: {last_error}"
    )

async def search_movie_poster(title: str, original_title: Optional[str] = None, year: Optional[int] = None) -> dict:
    """Busca en TMDb y OMDb el poster oficial en alta resolución"""
    tmdb_key = os.getenv("TMDB_API_KEY", "").strip() or DEFAULT_TMDB_KEY
    queries = [title]
    if original_title and original_title.strip() and original_title.lower() != title.lower():
        queries.append(original_title.strip())

    # 1. Búsqueda en TMDb en español e inglés
    for q in queries:
        try:
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_key}&query={urllib.parse.quote(q)}&language=es-ES"
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        item = results[0]
                        poster_path = item.get("poster_path")
                        backdrop_path = item.get("backdrop_path")
                        if poster_path:
                            return {
                                "poster": f"https://image.tmdb.org/t/p/w500{poster_path}",
                                "backdrop": f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else None,
                                "vote_average": item.get("vote_average")
                            }
        except Exception:
            pass

    # 2. Fallback de alta fiabilidad en OMDb
    for q in queries:
        try:
            omdb_url = f"https://www.omdbapi.com/?t={urllib.parse.quote(q)}&apikey=trilogy"
            async with httpx.AsyncClient(timeout=3.5) as client:
                oresp = await client.get(omdb_url)
                if oresp.status_code == 200:
                    odata = oresp.json()
                    poster = odata.get("Poster")
                    if poster and poster != "N/A" and poster.startswith("http"):
                        return {"poster": poster}
        except Exception:
            pass

    return {}


@app.post("/api/recommend")
async def recommend_movies(req: RecommendationRequest):
    """Genera recomendaciones utilizando OpenRouter API con formato JSON estructurado"""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = req.model or os.getenv("OPENROUTER_MODEL", "minimax/minimax-m3.1-flash:free")

    if not api_key:
        filtered = [
            item for item in CURATED_CATALOG 
            if (req.platform == "Todas" or req.platform in item["platforms"])
        ]
        return {
            "demo_mode": True,
            "summary": "Modo Demostración Local. Agrega tu API Key de OpenRouter para recomendaciones 100% personalizadas por IA.",
            "recommendations": filtered or CURATED_CATALOG[:3]
        }

    system_prompt = (
        "Eres CineMatch AI, un curador y crítico de cine de prestigio. "
        "Recomienda exactamente 3 o 4 películas o series según la petición. "
        "Tu respuesta debe ser UNICAMENTE un objeto JSON con este esquema exacto:\n"
        "{\n"
        '  "summary": "Una frase que resume la selección",\n'
        '  "recommendations": [\n'
        "    {\n"
        '      "title": "Título en español",\n'
        '      "year": 2023,\n'
        '      "type": "Película" o "Serie",\n'
        '      "director": "Nombre director",\n'
        '      "rating": 8.3,\n'
        '      "match_percentage": 96,\n'
        '      "genres": ["Género 1", "Género 2"],\n'
        '      "platforms": ["Netflix", "Prime Video", "Max", "Disney+", "Filmin", "Apple TV+", "Movistar+"],\n'
        '      "hook": "Gancho de una frase",\n'
        '      "synopsis": "Sinopsis de 2 líneas sin spoilers",\n'
        '      "why_recommended": "Por qué encaja con la petición",\n'
        '      "mood_tags": ["Tag 1", "Tag 2"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_query = f"Petición del usuario: '{req.prompt}'.\n"
    if req.platform and req.platform != "Todas":
        user_query += f"Plataforma requerida: {req.platform}.\n"
    if req.content_type and req.content_type != "both":
        user_query += f"Formato: {'Solo películas' if req.content_type == 'movie' else 'Solo series'}.\n"
    if req.mood and req.mood != "cualquiera":
        user_query += f"Estado de ánimo / Mood: {req.mood}.\n"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        raw_content, actual_model, used_fallback = await query_openrouter_with_auto_fallback(
            api_key=api_key,
            requested_model=model,
            messages=messages,
            temperature=0.6
        )
        parsed_data = extract_json_from_text(raw_content)

        for rec in parsed_data.get("recommendations", []):
            tmdb_info = await search_movie_poster(
                title=rec.get("title", ""),
                original_title=rec.get("original_title", ""),
                year=rec.get("year")
            )
            if tmdb_info.get("poster"):
                rec["poster"] = tmdb_info["poster"]
            else:
                rec["poster"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80"
            if tmdb_info.get("backdrop"):
                rec["backdrop"] = tmdb_info["backdrop"]

        return {
            "demo_mode": False,
            "model_used": actual_model,
            "fallback_active": used_fallback,
            "summary": parsed_data.get("summary", "Aquí tienes tus recomendaciones personalizadas:"),
            "recommendations": parsed_data.get("recommendations", [])
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="La IA devolvió una respuesta que no pudimos interpretar como JSON. Intenta reformular ligeramente tu búsqueda.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con OpenRouter: {str(e)}")


@app.post("/api/match")
async def match_couple(req: CoupleMatchRequest):
    """Encuentra la película o serie perfecta para dos personas con gustos distintos"""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "minimax/minimax-m3.1-flash:free")

    if not api_key:
        return {
            "demo_mode": True,
            "match_title": "Puñales por la espalda",
            "reason": "Excelente equilibrio entre comedia ligera y misterio para satisfacer a ambos.",
            "recommendation": CURATED_CATALOG[2]
        }

    system_prompt = (
        "Eres un mediador cinematográfico experto en resolver desacuerdos en pareja sobre qué ver. "
        "Encuentra la película o serie de compromiso perfecto. Responde estrictamente con un JSON:\n"
        "{\n"
        '  "compromise_analysis": "Por qué es el punto medio ideal",\n'
        '  "compatibility_score": 95,\n'
        '  "title": "Título en español",\n'
        '  "year": 2023,\n'
        '  "type": "Película",\n'
        '  "genres": ["Comedia", "Intriga"],\n'
        '  "platforms": ["Netflix", "Prime Video"],\n'
        '  "hook": "El gancho para convencer a ambos",\n'
        '  "why_person_1_will_love_it": "Por qué le gustará a la persona 1",\n'
        '  "why_person_2_will_love_it": "Por qué le gustará a la persona 2"\n'
        "}"
    )

    query = f"Persona 1: '{req.user1_preferences}'.\nPersona 2: '{req.user2_preferences}'.\nPlataforma: {req.platform}."

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        raw_content, actual_model, used_fallback = await query_openrouter_with_auto_fallback(
            api_key=api_key,
            requested_model=model,
            messages=messages,
            temperature=0.6
        )
        match_data = extract_json_from_text(raw_content)
        poster_info = await search_movie_poster(match_data.get("title", ""))
        if poster_info.get("poster"):
            match_data["poster"] = poster_info["poster"]
        match_data["model_used"] = actual_model
        return match_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("Iniciando CineMatch AI en http://localhost:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
