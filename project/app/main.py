from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
from elasticsearch import Elasticsearch

app = Flask(__name__)
UPLOAD_FOLDER = '/app/data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Elasticsearch configuration
ELASTICSEARCH_URL = "http://elasticsearch:9200"
INDEX_NAME = "gym_data"
es = Elasticsearch([ELASTICSEARCH_URL])


@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Redirection vers la page tableau de bord après l'upload
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '')
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"Gender.keyword": query}},
                        {"term": {"Workout_Type.keyword": query}},
                        {"term": {"Experience_Level.keyword": query}}
                    ]
                }
            }
        }
        try:
            response = es.search(index=INDEX_NAME, body=search_query)
            hits = response.get('hits', {}).get('hits', [])
            return render_template('search.html', query=query, results=hits)
        except Exception as e:
            return jsonify({'error': f'Elasticsearch request failed: {str(e)}'}), 500
    return render_template('search.html', query='', results=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
