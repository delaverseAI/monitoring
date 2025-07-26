import os
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from db_monitor import database_stats, database_recommendation, init_db
from server_monitor import get_nginx_stats, get_system_resources, get_process_info, get_recommendations

load_dotenv()

app = Flask(__name__)

# Configuration
class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    APP_PORT = int(os.environ.get('APP_PORT', 5000))
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY')

app.config.from_object(Config)

# Initialize database
db = SQLAlchemy()
init_db(app)

# API Key Middleware
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if api_key and api_key == app.config['API_KEY']:
            return f(*args, **kwargs)
        return jsonify({'error': 'Invalid or missing API key'}), 401
    return decorated


@app.route('/api/v1/comprehensive', methods=['GET'])
@require_api_key
def get_comprehensive_monitoring():
    try:
        resources = get_system_resources()
        nginx_stats = get_nginx_stats()
        processes = get_process_info()
        db_status = database_stats()
        all_recommendations = get_recommendations(resources, nginx_stats)
        all_recommendations.append(database_recommendation(db_status))
        
        return jsonify({
            'status': 'success',
            'data': {
                'resources': resources,
                'nginx': nginx_stats,
                'database': db_status,
                'processes': processes,
                'recommendations': all_recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500