import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://admin:admin_password@db:5432/geodb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False