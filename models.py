from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    activated = db.Column(db.Boolean, default=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_loggedin = db.Column(db.DateTime(timezone=True))

    def __init__(self, email, password) -> None:
        super().__init__()
        self.email = email
        self.password = password
        self.activated = False

    @property
    def is_admin(self) -> bool:
        return self.email == "adam@example.com"
    
    @property
    def is_activated(self) -> bool:
        return self.activated
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), unique=True)
    cove_filename = db.Column(db.String(100))
    hash = db.Column(db.String(100), unique=True)
    visable = db.Column(db.Boolean, default=False)

    def __init__(self, filename, cover_filename, hash) -> None:
        super().__init__()
        self.filename = filename
        self.cove_filename = cover_filename
        self.hash = hash

    @property
    def is_visable(self) -> bool:
        return self.visable
    
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, user_id, book_id) -> None:
        super().__init__()
        self.user_id = user_id
        self.book_id = book_id