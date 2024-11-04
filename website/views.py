from flask import Blueprint, render_template, jsonify, request, flash
import pytz
from datetime import datetime
from . import get_thing_shadow
from flask_login import login_required, current_user
from . import get_tds_data, db
from firebase_admin import firestore
from werkzeug.security import generate_password_hash

views = Blueprint('views', __name__)

def get_indian_time():
    india_timezone = pytz.timezone('Asia/Kolkata')
    return datetime.now(india_timezone).strftime('%H:%M')

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/data')
@login_required
def get_latest_data():
    latest_data = get_tds_data(limit=1)
    if latest_data:
        return jsonify(latest_data[0])
    return jsonify({'error': 'No data available'})

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        number = request.form.get("number")
        
        hashed_password = generate_password_hash(password)
        user_data = {
            'name': name,
            'password': hashed_password,
            'email': email,
            'number': number
        }

        try:
            db.collection('users').add(user_data)
            flash('Account created successfully', category='success')
        except Exception as e:
            flash(f'Error: {e}', category='error')
        
    return render_template("register.html")

@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/dashboard')
@login_required
def dashboard():
    thing_name = "ESP8266_Sensor"
    data = get_thing_shadow(thing_name)
    fetched_data = data if data else {'TDS': None, 'time': None}
    formatted_time = get_indian_time()
    return render_template("dashboard.html", data=fetched_data, formatted_time=formatted_time, user=current_user)

@views.route('/chart')
@login_required
def chart():
    tds_data = get_tds_data(limit=10)
    sorted_data = sorted(tds_data, key=lambda x: x['timestamp'])
    return render_template('chart.html', data=sorted_data, user=current_user)
