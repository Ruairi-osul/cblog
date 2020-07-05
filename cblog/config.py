import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_USER = os.environ.get("GMAIL_USER")
    MAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_PORT = 587
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
