from flask import Flask
from .models import db
from .views import api_v1
from ..config import config

def create_app(enviroment):
    app = Flask(__name__)
    app.config.from_object(enviroment) 
    if 'api_v1' not in app.blueprints:
        app.register_blueprint(api_v1, url_prefix='/api/v1')
    with app.app_context():
        db.init_app(app)
        #print("DATABASE URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))       
        db.create_all()
    return app