from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


# Flask app
app = Flask(__name__)

# Secret Key
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# DB connection
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}' + \
    f'@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'

db = SQLAlchemy(app)

"""

## User

- ID (PK, int)
- Name (varchar(50))
- Email (UNIQUE, varchar(50))
- Password (varchar(16), min 8, eng letters + numbers)
- Photo Url (varchar(100))

## Room

- ID (PK, int)
- Name (varchar(30))
- OwnerID (FK -> User, int)

## Room <-> User

- RoomID (FK -> Room, int)
- UserID (FK -> User, int)

## Cheque

- ID (PK, int)
- RoomID (FK -> Room, int)
- OwnerID (FK -> User, int)
- Name (varchar(30))

## ProductItem

- ID (PK, int)
- Name (varchar(30))
- Price (int)
- Count (int)
- RoomId (FK -> Room)

## ProductItem <-> User

- ProductID (FK -> ProductItem, int)
- UserID (FK -> User, int)

"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)
    photo_url = db.Column(db.String(100))

