from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # <-- autorise toutes les origines, utile pour le dev

FIREBASE_PROJECT = "garrageapp-05"

@app.route("/voitures")
def get_voitures():
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents/voitures"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les données", "code": r.status_code}), 500
    return jsonify(r.json())

# Si tu as d'autres routes, elles sont automatiquement couvertes par CORS

if __name__ == "__main__":
    app.run(debug=True)
