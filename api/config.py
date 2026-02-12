"""Configuración de la aplicación."""
import os

class Config:
    """Configuración base."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }
    DEFAULT_DB = 'postgresql://neondb_owner:npg_iPNr6cuTSbF8@ep-dark-lab-ahal0y0t-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_DB)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', Config.DEFAULT_DB)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:Dimichev3.@localhost:5432/test')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', Config.DEFAULT_DB)

def get_config(env=None):
    """Factory para obtener la configuración."""
    env = env or os.getenv('FLASK_ENV', 'development').lower()
    mapping = {
        'development': DevelopmentConfig, 'dev': DevelopmentConfig,
        'test': TestConfig, 'testing': TestConfig,
        'production': ProductionConfig, 'prod': ProductionConfig,
        'default': DevelopmentConfig
    }
    return mapping.get(env, DevelopmentConfig)

config = {
    'development': DevelopmentConfig, 'default': DevelopmentConfig,
    'test': TestConfig, 'production': ProductionConfig
}
