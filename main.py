from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

FIREBASE_PROJECT = "garrageapp-05"
FIRESTORE_BASE = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents"

# ----------------------------
# GET /voitures
# ----------------------------
@app.route("/voitures")
def get_voitures():
    url = f"{FIRESTORE_BASE}/voitures"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les données", "code": r.status_code}), 500
    return jsonify(r.json())

# ----------------------------
# POST /pannes  -> filtrer par idVoiture
# ----------------------------
@app.route("/pannes", methods=["POST"])
def get_pannes():
    data = request.json or {}
    id_voiture = data.get("idVoiture", "")
    
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "pannes"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "idVoiture"},
                    "op": "EQUAL",
                    "value": {"stringValue": id_voiture}
                }
            },
            "limit": 20
        }
    }
    
    url = f"{FIRESTORE_BASE}:runQuery"
    r = requests.post(url, json=query)
    
    if r.status_code != 200:
        return jsonify({"error": "Erreur serveur Firestore", "code": r.status_code}), 500
    return jsonify(r.json())

# ----------------------------
# POST /panneDetails -> filtrer par idPanne
# ----------------------------
@app.route("/panneDetails", methods=["POST"])
def get_panne_details():
    data = request.json or {}
    id_panne = data.get("idPanne", "")
    
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "panneDetails"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "idPanne"},
                    "op": "EQUAL",
                    "value": {"stringValue": id_panne}
                }
            },
            "limit": 10
        }
    }
    
    url = f"{FIRESTORE_BASE}:runQuery"
    r = requests.post(url, json=query)
    
    if r.status_code != 200:
        return jsonify({"error": "Erreur serveur Firestore", "code": r.status_code}), 500
    return jsonify(r.json())

# ----------------------------
# GET /panneTypes/<id_type>
# ----------------------------
@app.route("/panneTypes/<id_type>")
def get_panne_type(id_type):
    url = f"{FIRESTORE_BASE}/panneTypes/{id_type}"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer le type de panne", "code": r.status_code}), 500
    return jsonify(r.json())

# ----------------------------
# POST /panneStatuts -> création d'un statut
# ----------------------------
@app.route("/panneStatuts", methods=["POST"])
def create_panne_statut():
    data = request.json or {}
    url = f"{FIRESTORE_BASE}/panneStatuts"
    
    r = requests.post(url, json=data)
    if r.status_code not in (200, 201):
        return jsonify({"error": "Impossible de créer le statut", "code": r.status_code}), 500
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/pannes/<string:panne_id>/paiement")
def get_paiement_panne(panne_id):
    """Vérifier si une panne a été payée"""
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "panneStatuts"}],
            "where": {
                "compoundFilter": {
                    "op": "AND",
                    "filters": [
                        {
                            "fieldFilter": {
                                "field": {"fieldPath": "idPanne"},
                                "op": "EQUAL",
                                "value": {"stringValue": panne_id}
                            }
                        },
                        {
                            "fieldFilter": {
                                "field": {"fieldPath": "idStatutForPaiement"},
                                "op": "EQUAL",
                                "value": {"stringValue": "3"}  # 3 = payé
                            }
                        }
                    ]
                }
            },
            "limit": 1
        }
    }
    
    url = f"{BASE_URL}:runQuery"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'identity'
    }
    
    r = requests.post(url, json=query, headers=headers, timeout=10)
    
    if r.status_code != 200:
        return jsonify({
            "error": {
                "code": r.status_code,
                "message": r.text[:200] if r.text else "Pas de réponse"
            }
        }), r.status_code
    
    return jsonify(r.json())