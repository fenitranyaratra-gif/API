from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

FIREBASE_PROJECT = "garrageapp-05"

@app.route("/voitures")
def get_voitures():
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents/voitures"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify({"error": "Impossible de récupérer les données", "code": r.status_code}), 500
    return jsonify(r.json())

if __name__ == "__main__":
    app.run()
