from flask import Flask
import boto3
import json
from flask_login import LoginManager, UserMixin
from os import path
from decimal import Decimal
import firebase_admin
from firebase_admin import credentials, firestore, auth
from decouple import config  # Import decouple

# Load Firebase credentials from environment variable
cred = credentials.Certificate(config('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# User class
class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config('FLASK_SECRET_KEY')  # Load secret key from .env

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Define the user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Load user from Firestore using the user_id
            user_ref = db.collection('users').document(user_id).get()
            if user_ref.exists:
                user_data = user_ref.to_dict()
                return User(id=user_id, name=user_data.get('name'), email=user_data.get('email'))
            return None
        except Exception as e:
            print(f"Error loading user: {e}")
            return None

    return app

# AWS IoT client setup
aws_iot_client = boto3.client(
    'dynamodb',
    region_name='ap-southeast-2',
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),  # Load from .env
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')  # Load from .env
)
aws_iot_client1 = boto3.client(
    'iot-data',
    region_name='ap-southeast-2',
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),  # Load from .env
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')  # Load from .env
)

def get_iot_data():
    try:
        response = aws_iot_client1.get_thing_shadow(thingName='ESP8266_Sensor')
        payload = response['payload'].read()
        payload_data = json.loads(payload)
        data = json.loads(payload_data['state']['reported'])
        return data
    except Exception as e:
        print(f"Error fetching IoT data: {e}")
        return None

def get_tds_data(limit=10):
    try:
        response = aws_iot_client.scan(TableName='TDS_DATA', Limit=100)
        items = response.get('Items', [])
        formatted_items = [{'tds': float(item['TDS']['N']), 'timestamp': item['timestamp']['S']} for item in items]
        sorted_items = sorted(formatted_items, key=lambda x: x['timestamp'], reverse=True)
        return sorted_items[:limit]
    except Exception as e:
        print(f"Error fetching TDS data from DynamoDB: {str(e)}")
        return []

def get_thing_shadow(thing_name):
    try:
        response = aws_iot_client1.get_thing_shadow(thingName=thing_name)
        payload = json.loads(response['payload'].read())
        data = payload['state']['reported']
        return data
    except Exception as e:
        return None
