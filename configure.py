import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'ecofinds.db'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_ALGORITHM = 'HS256'

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = ':memory:'  # In-memory database for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
