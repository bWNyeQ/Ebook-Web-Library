from flask import Flask, g, render_template
from flask_login import login_user, current_user,LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    load_config(app)
    load_blueprints(app)

    login_manager.init_app(app)
    db.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @app.before_request
    def associate_user():
        if current_user.is_authenticated:
            g.user = current_user
        else:
            g.user = None

    @app.errorhandler(401)
    def not_athorized(e):
        return render_template('error.html',msg="404"), 401


    return app

def load_config(app):
    UPLOAD_FOLDER = './uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = 'SUPER SECRET'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

def load_blueprints(app):
    from blueprints.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/')

    from blueprints.auth import auth
    app.register_blueprint(auth, name='auth', url_prefix='/auth')

    from blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, name='admin', url_prefix="/admin")



if __name__ == '__main__':
    app = create_app()
    app.run()