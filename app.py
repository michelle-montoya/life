from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

API_KEY = "6b9f13370886d7141f7965d339305526"
BASE_URL = "https://api.themoviedb.org/3"

def get_serie_data():
    url = f"{BASE_URL}/search/tv"
    params = {
        "api_key": API_KEY,
        "query": "Life",
        "first_air_date_year": 2007,
        "language": "es-ES"
    }
    response = requests.get(url, params=params)
    data = response.json()
    serie = data["results"][0]
    serie_id = serie["id"]

    detalles = requests.get(
        f"{BASE_URL}/tv/{serie_id}",
        params={"api_key": API_KEY, "language": "es-ES"}
    ).json()

    actores = requests.get(
        f"{BASE_URL}/tv/{serie_id}/credits",
        params={"api_key": API_KEY}
    ).json()

    temporadas = requests.get(
        f"{BASE_URL}/tv/{serie_id}",
        params={"api_key": API_KEY, "language": "es-ES", "append_to_response": "seasons"}
    ).json()

    videos = requests.get(
        f"{BASE_URL}/tv/{serie_id}/videos",
        params={"api_key": API_KEY}
    ).json()

    similares = requests.get(
        f"{BASE_URL}/tv/{serie_id}/similar",
        params={"api_key": API_KEY, "language": "es-ES"}
    ).json()

    return {
        "serie": detalles,
        "actores": actores.get("cast", [])[:8],
        "videos": videos.get("results", [])[:3],
        "similares": similares.get("results", [])[:6],
        "serie_id": serie_id
    }

@app.route("/")
def home():
    data = get_serie_data()
    return render_template("index.html", **data)

@app.route("/elenco")
def elenco():
    data = get_serie_data()
    actores_completos = requests.get(
        f"{BASE_URL}/tv/{data['serie_id']}/credits",
        params={"api_key": API_KEY}
    ).json()
    data["actores"] = actores_completos.get("cast", [])[:20]
    return render_template("elenco.html", **data)

@app.route("/temporadas")
def temporadas():
    data = get_serie_data()
    return render_template("temporadas.html", **data)

@app.route("/galeria")
def galeria():
    data = get_serie_data()
    imagenes = requests.get(
        f"{BASE_URL}/tv/{data['serie_id']}/images",
        params={"api_key": API_KEY}
    ).json()
    data["imagenes"] = imagenes.get("backdrops", [])[:12]
    data["posters"] = imagenes.get("posters", [])[:6]
    return render_template("galeria.html", **data)

if __name__ == "__main__":
    app.run(debug=True)