import os


class Config:
    SECRET_KEY = os.environ.get("TELTECH_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("TELTECH_SQLALCHEMY_DATABASE_URI")
    MAIL_SERVER = "smtp-relay.sendinblue.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("SMTP_MAIL_NAME")
    MAIL_PASSWORD = os.environ.get("SMTP_MAIL_PASSWORD")
