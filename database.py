from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
import os

db = SQLAlchemy()
migrate = Migrate()

def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("MYSQL_DB_URL")  # e.g., mysql+pymysql://user:pass@host/db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables automatically
    with app.app_context():
        db.create_all()
