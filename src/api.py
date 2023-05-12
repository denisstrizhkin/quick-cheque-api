from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
