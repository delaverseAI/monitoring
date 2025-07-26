import uvicorn
from app import os
from app import app
from asgiref.wsgi import WsgiToAsgi

# Wrap Flask app for ASGI compatibility
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    uvicorn.run(
        "server:asgi_app",
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        reload=os.environ.get('FLASK_DEBUG', 'False') == 'True'
    )