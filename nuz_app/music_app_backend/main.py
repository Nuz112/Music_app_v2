
from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from os import path
from flask_cors import CORS
from website.worker import *
from website.database import db
from flask_caching import Cache




# db = SQLAlchemy()
DB_NAME = "database.db"





def create_app() :
    app = Flask(__name__ )
    CORS(app,origins='http://localhost:8080')
    app.config['SECRET_KEY'] = 'dfjdfgngjngjkrgn'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['JWT_SECRET_KEY'] = 'OppsSecretIsRequired'  
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  
    
    
    jwt = JWTManager(app)
    db.init_app(app)
    return app

app = create_app()
app.app_context().push() 

from website.auth import auth
from website.views import views
from website.playlist import playlist
from website.album import album
from website.admin import admin
from website.api import api_bp

app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(views, url_prefix= '/')
app.register_blueprint(playlist, url_prefix='/')
app.register_blueprint(album, url_prefix='/')
app.register_blueprint(admin, url_prefix= '/')
app.register_blueprint(api_bp, url_prefix='/api')



def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()



celery=celery
CELERY_BROKER_URL="redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/2"

celery.conf.update(
    broker_url="redis://127.0.0.1:6379/1",
    result_backend="redis://127.0.0.1:6379/2",
    timezone="Asia/Kolkata"
)


celery.Task = ContextTask




if __name__ == "__main__":
    # db.create_all()
    create_database()

    app.run()
