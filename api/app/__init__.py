from flask import Flask
from .models import db
from .views import api_v1
from api.config import config
from flask_cors import CORS 

def create_app(enviroment):
    app = Flask(__name__)
    app.config.from_object(enviroment)
    CORS(app)
    if 'api_v1' not in app.blueprints:
        app.register_blueprint(api_v1, url_prefix='/api/v1')
    with app.app_context():
        db.init_app(app)            
        db.create_all()
    return app