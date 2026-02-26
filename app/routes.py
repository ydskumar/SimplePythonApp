from flask import Blueprint, jsonify
from .service import welcome_message, health_status, greetings

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
    return {"version": os.environ.get("APP_VERSION")}
