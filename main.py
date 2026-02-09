from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # <-- autorise toutes les origines, utile pour le dev

FIREBASE_PROJECT = "garrageapp-05"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents"

# ===============================
# Route pour récupérer toutes les voitures
# ===============================
@app.route("/voitures")
def get_voitures():
    url = f"{BASE_URL}/voitures"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les voitures", "code": r.status_code}), 500
    return jsonify(r.json())

# ===============================
# Route pour récupérer les pannes d'une voiture
# ===============================
@app.route("/voitures/<string:voiture_id>/pannes")
def get_pannes_voiture(voiture_id):
    # Requête Firestore pour trouver les pannes liées à une voiture
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "pannes"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "idVoiture"},
                    "op": "EQUAL",
                    "value": {"stringValue": voiture_id}
                }
            },
            "limit": 20
        }
    }
    
    url = f"{BASE_URL}:runQuery"
    r = requests.post(url, json=query)
    
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les pannes", "code": r.status_code}), 500
    
    return jsonify(r.json())

# ===============================
# Route pour récupérer les détails d'une panne
# ===============================
@app.route("/pannes/<string:panne_id>/details")
def get_details_panne(panne_id):
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "panneDetails"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "idPanne"},
                    "op": "EQUAL",
                    "value": {"stringValue": panne_id}
                }
            },
            "limit": 10
        }
    }
    
    url = f"{BASE_URL}:runQuery"
    r = requests.post(url, json=query)
    
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les détails", "code": r.status_code}), 500
    
    return jsonify(r.json())

# ===============================
# Route pour récupérer un type de panne spécifique
# ===============================
@app.route("/panneTypes/<string:type_id>")
def get_panne_type(type_id):
    url = f"{BASE_URL}/panneTypes/{type_id}"
    r = requests.get(url)
    
    if r.status_code != 200:
        return jsonify({"error": "Type de panne introuvable", "code": r.status_code}), 404
    
    return jsonify(r.json())

# ===============================
# Route pour récupérer le statut d'une panne
# ===============================
@app.route("/pannes/<string:panne_id>/statut")
def get_statut_panne(panne_id):
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "panneStatuts"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "idPanne"},
                    "op": "EQUAL",
                    "value": {"stringValue": panne_id}
                }
            },
            "limit": 1
        }
    }
    
    url = f"{BASE_URL}:runQuery"
    r = requests.post(url, json=query)
    
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer le statut", "code": r.status_code}), 500
    
    return jsonify(r.json())

# ===============================
# Route pour créer un nouveau statut de panne
# ===============================
@app.route("/pannes/<string:panne_id>/valider", methods=["POST"])
def valider_panne(panne_id):
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    # Préparer le document Firestore
    new_doc = {
        "fields": {
            "dateHeure": {"timestampValue": data.get("dateHeure")},
            "idPanne": {"stringValue": panne_id},
            "idStatutForPanne": {"stringValue": data.get("idStatutForPanne", "2")}
        }
    }
    
    url = f"{BASE_URL}/panneStatuts"
    r = requests.post(url, json=new_doc)
    
    if r.status_code != 200:
        return jsonify({"error": "Impossible de valider la panne", "code": r.status_code}), 500
    
    return jsonify({"success": True, "data": r.json()})

# ===============================
# Route pour récupérer toutes les données d'une voiture (voiture + pannes)
# ===============================
@app.route("/voitures/<string:voiture_id>/complete")
def get_voiture_complete(voiture_id):
    # Récupérer la voiture
    voiture_url = f"{BASE_URL}/voitures/{voiture_id}"
    voiture_resp = requests.get(voiture_url)
    
    if voiture_resp.status_code != 200:
        return jsonify({"error": "Voiture introuvable", "code": voiture_resp.status_code}), 404
    
    # Récupérer les pannes
    pannes = get_pannes_voiture(voiture_id).get_json()
    
    # Combiner les données
    result = {
        "voiture": voiture_resp.json(),
        "pannes": pannes
    }
    
    return jsonify(result)

# ===============================
# Route de test
# ===============================
@app.route("/")
def index():
    return jsonify({
        "message": "API Garage en ligne",
        "endpoints": {
            "/voitures": "GET - Liste toutes les voitures",
            "/voitures/<id>/pannes": "GET - Pannes d'une voiture",
            "/voitures/<id>/complete": "GET - Données complètes d'une voiture",
            "/pannes/<id>/details": "GET - Détails d'une panne",
            "/panneTypes/<id>": "GET - Type de panne",
            "/pannes/<id>/statut": "GET - Statut d'une panne",
            "/pannes/<id>/valider": "POST - Valider une panne réparée"
        }
    })

if __name__ == "__main__":
    app.run(debug=True)