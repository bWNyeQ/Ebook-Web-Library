from flask_login import login_user, current_user,LoginManager, UserMixin, login_required, logout_user
from flask import Blueprint, redirect, render_template, url_for,current_app, request, flash
from models import User
from app import db
import datetime

auth = Blueprint('user_blueprint',__name__,
    template_folder='templates',
    static_folder='static')

@auth.route('/login', methods=['GET','POST'])
def login_post():
    if current_user.is_authenticated:
        flash("You cannot login whilst already being logged in. Try to logout first.", "error") 
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html')

    user = User.query.filter(User.email == request.form.get('email')).first()
    if user and user.is_activated:
        flash("Welcome " + user.email) 
        login_user(user)

        user.last_loggedin = datetime.datetime.now()
        db.session.commit()

        return redirect('/')

    if user:
        flash("Account not activated. Ask an administrator to unlock this account","error")
    else:
        flash("could not login","error")

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash('You are no longer signed in')
        return redirect('/')

@auth.route('/profile')
@login_required
def user_profile():
    return render_template('profile.html')
