import time

from flask import Flask
from .routes import bp

def create_app():
    app = Flask(__name__)
    start_time = time.time()
    app.register_blueprint(bp, url_prefix="/api/v1")
    app.config['START_TIME'] = start_time
    return app