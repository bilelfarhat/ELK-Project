
from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)
UPLOAD_FOLDER = '/usr/share/logstash/logs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ELASTICSEARCH_URL = "http://elasticsearch:9200/logs-*/_search"

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Interface pour uploader les fichiers
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return render_template('upload.html', message=f"File {file.filename} uploaded successfully!")

    return render_template('upload.html')

# Interface pour rechercher les logs
@app.route('/search', methods=['GET', 'POST'])
def search_logs():
    if request.method == 'POST':
        query = request.form['query']
        response = requests.get(ELASTICSEARCH_URL, json={"query": {"query_string": {"query": query}}})
        logs = response.json().get('hits', {}).get('hits', [])
        return render_template('search.html', logs=logs, query=query)

    return render_template('search.html', logs=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
