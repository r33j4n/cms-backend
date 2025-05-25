from flask_sqlalchemy import SQLAlchemy
from database import db
import datetime

class FlatOwner(db.Model):
    __tablename__ = 'flat_owners'

    id = db.Column(db.Integer, primary_key=True)
    pin_no = db.Column(db.String(10), nullable=False)
    flat_no = db.Column(db.String(10), nullable=False, unique=True)
    contact_no = db.Column(db.String(15), nullable=False)
    complaints = db.relationship('Complaint', backref='owner', lazy=True)

    def __init__(self, pin_no, flat_no, contact_no):
        self.pin_no = pin_no
        self.flat_no = flat_no
        self.contact_no = contact_no

class Admin(db.Model):
    __tablename__ = 'admins'

    # NOTE: This model was updated to use plain text passwords instead of hashed passwords.
    # The column name was changed from 'password_hash' to 'password'.
    # If you have existing data, you'll need to:
    # 1. Either drop and recreate the database (losing all data)
    # 2. Or manually update the database schema to rename the column

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_password(self, password):
        return self.password == password

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=True)
    proof_image = db.Column(db.String(255), nullable=True)  # Path to the image file
    solution = db.Column(db.Text, nullable=True)
    is_checked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Foreign key relationship
    owner_id = db.Column(db.Integer, db.ForeignKey('flat_owners.id'), nullable=False)

    def __init__(self, description, owner_id, proof_image=None):
        self.description = description
        self.owner_id = owner_id
        self.proof_image = proof_image
        self.is_checked = False

# Create a default admin user
def create_default_admin(app):
    with app.app_context():
        # Check if admin already exists
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()
