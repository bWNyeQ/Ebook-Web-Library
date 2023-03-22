from flask import Blueprint, render_template, request, flash, redirect, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from os import listdir, path
from models import Book, History

from utils import allowed_file 
from utils.pdf import pdf_to_png

from app import db

from io import BytesIO

from pdf2image import convert_from_path
import base64

user_bp = Blueprint('user',__name__,
    template_folder='templates',
    static_folder='static')

@user_bp.route('/')
def index():
    return render_template('index.html')

@user_bp.route('/library')
@login_required
def library():
    books = Book.query.filter_by(visable=True).all()
    return render_template('library.html', books=books)

@user_bp.route('/view')
@login_required
def view():
    book_id = request.args.get('bookId',0)
    book = Book.query.get(book_id)

    history = History(current_user.id,book_id)
    db.session.add(history)
    db.session.commit()

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], book.filename)

@user_bp.route('/view/cover')
@login_required
def viewCover():
    book_id = request.args.get('bookId',0)
    book = Book.query.get(book_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], book.cove_filename)
