from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def database_stats() -> dict:
    database_health = {}
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_connections,
                SUM(CASE WHEN state = 'Sleep' THEN 1 ELSE 0 END) as sleeping,
                SUM(CASE WHEN state != 'Sleep' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN state != 'Sleep' AND time > 300 THEN 1 ELSE 0 END) as long_running,
                MAX(CASE WHEN state != 'Sleep' THEN time ELSE NULL END) as longest_query_time
            FROM information_schema.processlist 
            WHERE db = :db_name AND user = :db_user
        """), {
            'db_name': db.engine.url.database,
            'db_user': db.engine.url.username
        })
        
        stats = result.fetchone()
        database_health = {
            'total_connections': stats[0],
            'sleeping_connections': int(stats[1]),
            'active_connections': int(stats[2]),
            'long_running_queries': int(stats[3]),
            'longest_query_seconds': stats[4]
        }
    
    return database_health

def database_recommendation(database_health: dict) -> dict:
    if database_health['sleeping_connections'] > database_health['active_connections'] * 2:
        return {
            'type': 'info',
            'category': 'Database',
            'message': 'High number of sleeping connections. Consider connection pool optimization.',
            'severity': 'medium'
        }
    
    return {}