from flask import Flask, jsonify
import os
import psycopg2
from prometheus_flask_exporter import PrometheusMetrics  # ← ajout

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # ← ajout (crée /metrics automatiquement)

@app.route('/')
def home():
    return jsonify({"message": "Hello from Flask on EKS! DevOps project ready."})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/db-check')
def db_check():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=5432,
            connect_timeout=5
        )
        conn.close()
        return jsonify({"db": "connected"})
    except Exception as e:
        return jsonify({"db_error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)