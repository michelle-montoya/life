# ============================================================
#  EXPLORADOR DE SERIES — API de The Movie Database (TMDB)
#  Proyecto: Life (2007)
#  Autor: [Tu nombre]
#  Descripción: Aplicación web construida con Flask que consume
#               la API de TMDB para mostrar información detallada
#               de una serie de televisión en múltiples páginas.
# ============================================================

# Flask: micro-framework web para Python
from flask import Flask, render_template, jsonify

# requests: librería para hacer peticiones HTTP a la API
import requests

# Inicialización de la aplicación Flask
app = Flask(__name__)

# ── Configuración de la API ──────────────────────────────────
# API Key obtenida desde themoviedb.org (perfil → API)
# IMPORTANTE: En producción, usar variables de entorno:
#   import os
#   API_KEY = os.environ.get("TMDB_API_KEY")
API_KEY = "6b9f13370886d7141f7965d339305526"

# URL base de todos los endpoints de TMDB v3
BASE_URL = "https://api.themoviedb.org/3"


# ── Función principal de datos ───────────────────────────────
def get_serie_data():
    """
    Función centralizada que consume múltiples endpoints de TMDB
    y retorna un diccionario con toda la información de la serie.

    Endpoints utilizados:
    1. /search/tv         → buscar la serie por nombre y año
    2. /tv/{id}           → detalles completos de la serie
    3. /tv/{id}/credits   → elenco (actores y equipo)
    4. /tv/{id}/videos    → tráilers y videos relacionados
    5. /tv/{id}/similar   → series similares recomendadas
    """

    # ── ENDPOINT 1: Búsqueda de la serie ────────────────────
    # GET /search/tv — busca series por texto con filtros opcionales
    url = f"{BASE_URL}/search/tv"
    params = {
        "api_key": API_KEY,
        "query": "Life",               # nombre de la serie a buscar
        "first_air_date_year": 2007,   # filtrar por año de estreno
        "language": "es-ES"            # resultados en español
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Tomar el primer resultado de la búsqueda
    serie = data["results"][0]

    # Extraer el ID único de la serie para los siguientes endpoints
    serie_id = serie["id"]

    # ── ENDPOINT 2: Detalles completos de la serie ──────────
    # GET /tv/{serie_id} — información detallada: géneros, temporadas,
    # puntuación, país de origen, duración de episodios, etc.
    detalles = requests.get(
        f"{BASE_URL}/tv/{serie_id}",
        params={"api_key": API_KEY, "language": "es-ES"}
    ).json()

    # ── ENDPOINT 3: Créditos (elenco y equipo) ──────────────
    # GET /tv/{serie_id}/credits — lista de actores (cast) y
    # equipo técnico (crew) con foto, personaje interpretado, etc.
    actores = requests.get(
        f"{BASE_URL}/tv/{serie_id}/credits",
        params={"api_key": API_KEY}
    ).json()

    # ── ENDPOINT 4: Detalles con temporadas anexadas ─────────
    # GET /tv/{serie_id}?append_to_response=seasons — combina los
    # detalles de la serie con la lista de temporadas en una sola petición
    temporadas = requests.get(
        f"{BASE_URL}/tv/{serie_id}",
        params={"api_key": API_KEY, "language": "es-ES", "append_to_response": "seasons"}
    ).json()

    # ── ENDPOINT 5: Videos relacionados ─────────────────────
    # GET /tv/{serie_id}/videos — tráilers, clips y otros videos
    # alojados en YouTube u otras plataformas
    videos = requests.get(
        f"{BASE_URL}/tv/{serie_id}/videos",
        params={"api_key": API_KEY}
    ).json()

    # ── ENDPOINT 6: Series similares ────────────────────────
    # GET /tv/{serie_id}/similar — series con temática o género
    # parecido, útil para secciones de recomendaciones
    similares = requests.get(
        f"{BASE_URL}/tv/{serie_id}/similar",
        params={"api_key": API_KEY, "language": "es-ES"}
    ).json()

    # Retornar todos los datos en un diccionario estructurado
    # Los [:N] limitan la cantidad de resultados para no sobrecargar la vista
    return {
        "serie": detalles,                       # objeto con toda la info de la serie
        "actores": actores.get("cast", [])[:8],  # primeros 8 actores del elenco
        "videos": videos.get("results", [])[:3], # primeros 3 videos
        "similares": similares.get("results", [])[:6],  # primeras 6 series similares
        "serie_id": serie_id                     # ID para peticiones adicionales
    }


# ── Rutas de la aplicación ───────────────────────────────────

@app.route("/")
def home():
    """
    Página principal — muestra el hero con póster, descripción,
    estadísticas generales, elenco resumido y series similares.
    """
    data = get_serie_data()
    return render_template("index.html", **data)
    # **data desempaca el diccionario como argumentos nombrados
    # para que el template Jinja2 pueda usarlos directamente


@app.route("/elenco")
def elenco():
    """
    Página de elenco — muestra todos los actores con foto,
    nombre y personaje que interpretan.
    Hace una petición adicional para obtener más actores (hasta 20).
    """
    data = get_serie_data()

    # Petición adicional al mismo endpoint de créditos
    # pero ampliando el límite a 20 actores para esta vista
    actores_completos = requests.get(
        f"{BASE_URL}/tv/{data['serie_id']}/credits",
        params={"api_key": API_KEY}
    ).json()

    # Reemplazar la lista reducida con la lista completa
    data["actores"] = actores_completos.get("cast", [])[:20]

    return render_template("elenco.html", **data)


@app.route("/temporadas")
def temporadas():
    """
    Página de temporadas — muestra cada temporada con su póster,
    número de episodios, fecha de estreno y calificación.
    Los datos de temporadas vienen incluidos en el objeto 'serie'
    gracias al append_to_response=seasons del endpoint de detalles.
    """
    data = get_serie_data()
    return render_template("temporadas.html", **data)


@app.route("/galeria")
def galeria():
    """
    Página de galería — muestra imágenes de la serie en dos
    categorías: escenas (backdrops) y pósters oficiales.

    Endpoint adicional utilizado aquí:
    7. /tv/{id}/images — imágenes en alta resolución de la serie
    organizadas en backdrops, posters y logos
    """
    data = get_serie_data()

    # ── ENDPOINT 7: Imágenes de la serie ────────────────────
    # GET /tv/{serie_id}/images — devuelve colecciones de imágenes
    # clasificadas por tipo: backdrops (fondos), posters y logos
    imagenes = requests.get(
        f"{BASE_URL}/tv/{data['serie_id']}/images",
        params={"api_key": API_KEY}
    ).json()

    # Agregar imágenes al diccionario de datos
    data["imagenes"] = imagenes.get("backdrops", [])[:12]  # hasta 12 escenas
    data["posters"] = imagenes.get("posters", [])[:6]      # hasta 6 pósters

    return render_template("galeria.html", **data)


# ── Punto de entrada de la aplicación ───────────────────────
if __name__ == "__main__":
    # debug=True activa recarga automática al guardar cambios
    # y muestra errores detallados en el navegador
    # IMPORTANTE: desactivar debug=False antes de publicar en producción
    app.run(debug=True)