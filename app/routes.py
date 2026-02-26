from flask import Blueprint, jsonify
from .service import get_metrics, get_version, welcome_message, health_status, greetings

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return welcome_message()

@bp.route('/health')
def health():
    return jsonify(health_status())

@bp.route('/how-are-you')
def greet():
    return greetings()

@bp.route("/version")
def version():
    return get_version()

@bp.route("/metrics")
def metrics():    
    return get_metrics(
        start_time=bp.config.get('START_TIME', 0)
    )
