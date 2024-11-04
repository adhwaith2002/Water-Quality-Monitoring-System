from flask import flash, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from firebase_admin import firestore
from werkzeug.security import check_password_hash
from . import db, User
from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('loginemail')
        password = request.form.get('loginpassword')
        
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).stream()

        user = None
        for doc in query:
            user = doc.to_dict()
            user['id'] = doc.id
            break

        if user:
            if check_password_hash(user['password'], password):
                login_user(User(id=user['id'], name=user['name'], email=user['email']))
                flash('Logged in successfully', category='success')
                return redirect(url_for('views.dashboard'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
