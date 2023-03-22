from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    db.create_all()

    new_user = User('adam@example.com','somepassword')
    new_user.activated = True
    db.session.add(new_user)
    db.session.commit()