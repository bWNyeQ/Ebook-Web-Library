from flask import Blueprint, render_template, request, flash, redirect, current_app, send_from_directory, url_for, g, abort
from werkzeug.utils import secure_filename
from os import listdir, path
from models import Book, History, User
from app import db

from utils.allowed_file import allowed_file

from io import BytesIO

from pdf2image import convert_from_path
import base64



admin_bp = Blueprint('admin',__name__,
    template_folder='templates',
    static_folder='static')

@admin_bp.before_request

def force_admin_check():
    if not (g.user and g.user.is_admin):
        abort(403)

@admin_bp.route('/')
def index():
    return render_template('admin/admin.html')

@admin_bp.route('/upload', methods = ['GET','POST'])
def upload():
    template = render_template('admin/admin_upload.html')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file found!','error')
            return template
        
        file = request.files['file']

        if file.filename == '':
            flash("No file found!",'error')
            return template
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename == "":
                flash("Bad file name!",'error')
                return template
            file.save(path.join(current_app.config['UPLOAD_FOLDER'], filename))



        book = Book(
            filename=filename,
            cover_filename=save_cover_image(filename),
            hash=filename
        )

        db.session.add(book)
        db.session.commit()

        flash("Uploaded file(s) sucessfully",category='message')
        return template
    
    return render_template('admin/admin_upload.html')


@admin_bp.route('/users')
def users():
    users = User.query.all()
    return render_template('admin/admin_users.html', users=users)

@admin_bp.route('/users/new', methods=['GET','POST'])
def users_new():
    template = render_template('admin/admin_users_new.html',
                               target_url=url_for('admin.users_new'),
                               title='New user')
    
    if request.method == 'GET':
        return template
    
    email = request.form['email']
    password = request.form['password']

    input_is_valid = validate_email(email) and validate_password(password)

    if not input_is_valid:
        flash("Email or password is not valid", "error")
        return template

    flash("new user added: " + email)

    new_user = User(email,password)
    db.session.add(new_user)
    db.session.commit()

    return redirect('/admin/users')


@admin_bp.route('/users/edit/<user_id>', methods=['GET','POST'])
def users_edit(user_id):
    user = User.query.get(user_id)
    template = render_template('admin/admin_users_new.html',
                                user=user, 
                                target_url=url_for('admin.users_edit', user_id=user_id),
                                title='Edit user'
                                )


    if request.method == 'GET':
        return template
    

    email = request.form['email']
    password = request.form['password']

    input_is_valid = validate_email(email) and validate_password(password)

    if not input_is_valid:
        flash("Email or password is not valid", "error")
        return template

    flash("Applied changes to " + email)

    if email != '':
        user.email = email

    if password != '':
        user.password = password

    db.session.commit()

    return redirect('/admin/users')


@admin_bp.route('/users/activate')
def activate():
    user_id = request.args['userId']

    return set_active_state(
        user_id=user_id,
        target_state=True,
        success_msg="User {} is now activated".format(user_id),
        fail_msg="Cannot activate an already active account",
        return_url=url_for('admin.users')
    )

@admin_bp.route('/users/deactivate')
def deactivate():
    user_id = request.args['userId']

    return set_active_state(
        user_id=user_id,
        target_state=False,
        success_msg="User {} is now deactivated".format(user_id),
        fail_msg="Cannot deactivate an already deactivated account",
        return_url=url_for('admin.users')
    )

@admin_bp.route('/books')
def books():
    files = listdir(current_app.config['UPLOAD_FOLDER'])
    books = Book.query.all()

    xs = []
    for file in files:
        filename = file
        missing_parent = not (file in map(lambda x: x.filename, books) or file in  map(lambda x: x.cove_filename, books))
        x = {
            'filename': filename,
            'is_missing_parent':missing_parent,
            'type': filename.split('.')[-1]
        }
        xs.append(x)

    ys = []
    for book in books:
        y = book
        y.is_missing_cover = not book.cove_filename in files
        y.is_missing_pdf = not book.filename in files
        ys.append(y)

    return render_template('admin/admin_books.html', 
                           books=ys, 
                           pdfs= [x for x in xs if x['type'] == 'pdf'], 
                           files=[x for x in xs if x['type'] == 'png']
                           )

@admin_bp.route('/books/new', methods=['get','post'])
def books_new():
    if request.method == 'GET':
        files = listdir(current_app.config['UPLOAD_FOLDER'])
        check_set = lambda v: request.args.get(v, default='')

        pdf = check_set('pdf')
        cover = check_set('cover')
        desc = check_set('desc')


        return render_template('admin/admin_books_new.html', files=files, pdf=pdf,cover=cover,desc=desc)
    
    pdf_filename = request.form.get('pdf_filename')
    desc = request.form.get('description', default='')
    coverFromPdf = request.form.get('fromPDF', default= False)
    cover_filename = ""
    if coverFromPdf:
        cover_filename = save_cover_image(pdf_filename)
    else:
        cover_filename = request.form.get('cover_filename')
    new_book = Book(pdf_filename,cover_filename+'.png',pdf_filename)

    db.session.add(new_book)
    db.session.commit()
    
    return redirect(url_for('admin.books'))

@admin_bp.route('/books/activate')
def books_activate():
    book_id = request.args.get('bookId')
    book = Book.query.get(book_id)
    book.visable = True
    db.session.commit()
    return redirect(url_for('admin.books'))

@admin_bp.route('/books/deactivate')
def books_deactivate():
    book_id = request.args.get('bookId')
    book = Book.query.get(book_id)
    book.visable = False
    db.session.commit()
    return redirect(url_for('admin.books'))

@admin_bp.route('/books/delete')
def books_delete():
    book_id = request.args.get('bookId')

    Book.query.filter_by(id=book_id).delete()
    db.session.commit()

    flash("Deleted book with id {}".format(book_id))

    return redirect(url_for('admin.books'))


@admin_bp.route('/view')
def view():
    file = request.args.get('file', default='')
    if file == '':
        abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], file)

@admin_bp.route('/history')
def history():
    history = History.query.all()
    return render_template('admin/admin_history.html',history=history)

def set_active_state(user_id,target_state,success_msg,fail_msg, return_url):
    user = User.query.get(user_id)
    if user.activated == target_state:
        flash(fail_msg, 'error')
    else:
        user.activated = target_state
        db.session.commit()
        flash(success_msg,format(user.email))
    return redirect(return_url)

def validate_email(email):
    return True

def validate_password(password):
    return True

def save_cover_image(file):
    pages = convert_from_path(path.join(current_app.config['UPLOAD_FOLDER'], file),50,first_page=0,last_page=1)

    filename = 'cover_' + file.split('.')[0]
    pages[0].save(path.join(current_app.config['UPLOAD_FOLDER'],filename + '.png'),'PNG')

    return filename

