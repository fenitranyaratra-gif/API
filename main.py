# app.py - Version corrigée

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # Autorise toutes les origines

FIREBASE_PROJECT = "garrageapp-05"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents"

@app.route("/voitures")
def get_voitures():
    """Endpoint qui simule exactement la réponse Firestore"""
    try:
        url = f"{BASE_URL}/voitures"
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'identity'  # Important : désactive gzip
        }
        
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"Erreur Firestore: {r.status_code} - {r.text}")
            return jsonify({
                "error": {
                    "code": r.status_code,
                    "message": r.text[:200] if r.text else "Pas de réponse"
                }
            }), r.status_code
        
        # Retourner exactement la même structure que Firestore
        return jsonify(r.json())
        
    except requests.exceptions.RequestException as e:
        print(f"Exception: {e}")
        return jsonify({
            "error": {
                "code": 500,
                "message": f"Erreur de connexion: {str(e)}"
            }
        }), 500

@app.route("/query", methods=["POST"])
def run_query():
    """Endpoint pour les requêtes Firestore structurées"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        url = f"{BASE_URL}:runQuery"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'identity'
        }
        
        r = requests.post(url, json=data, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"Erreur Firestore query: {r.status_code} - {r.text}")
            return jsonify({
                "error": {
                    "code": r.status_code,
                    "message": r.text[:200] if r.text else "Pas de réponse"
                }
            }), r.status_code
        
        return jsonify(r.json())
        
    except Exception as e:
        print(f"Exception dans /query: {e}")
        return jsonify({
            "error": {
                "code": 500,
                "message": str(e)
            }
        }), 500

@app.route("/documents/<path:doc_path>")
def get_document(doc_path):
    """Endpoint pour les documents individuels"""
    try:
        url = f"{BASE_URL}/{doc_path}"
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'identity'
        }
        
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"Erreur document {doc_path}: {r.status_code} - {r.text}")
            return jsonify({
                "error": {
                    "code": r.status_code,
                    "message": r.text[:200] if r.text else "Pas de réponse"
                }
            }), r.status_code
        
        return jsonify(r.json())
        
    except Exception as e:
        print(f"Exception document {doc_path}: {e}")
        return jsonify({
            "error": {
                "code": 500,
                "message": str(e)
            }
        }), 500

@app.route("/")
def index():
    return jsonify({
        "message": "API Garage - Version corrigée",
        "endpoints": {
            "/voitures": "GET - Liste toutes les voitures",
            "/query": "POST - Exécute une requête Firestore",
            "/documents/<path>": "GET - Récupère un document"
        },
        "status": "online"
    })

if __name__ == "__main__":
    app.run(debug=True)