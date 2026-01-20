"""
Configuración de la aplicación usando patrones de diseño Factory.
Soporta múltiples entornos y variables de entorno.
"""
import os
from typing import Dict, Type


class Config:
    """Configuración base con valores comunes a todos los entornos."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Obtener configuración de variables de entorno o usar valores por defecto
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://neondb_owner:npg_iPNr6cuTSbF8@ep-dark-lab-ahal0y0t-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )
    
    # Configuración de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_SUPPORTS_CREDENTIALS = os.getenv('CORS_SUPPORTS_CREDENTIALS', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""
    DEBUG = True
    
    # URL de base de datos para desarrollo (puede ser local o remota)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'postgresql://neondb_owner:npg_iPNr6cuTSbF8@ep-dark-lab-ahal0y0t-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )


class TestConfig(Config):
    """Configuración para el entorno de pruebas."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:Dimichev3.@localhost:5432/test'
    )


class ProductionConfig(Config):
    """Configuración para el entorno de producción."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://neondb_owner:npg_iPNr6cuTSbF8@ep-dark-lab-ahal0y0t-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )


def get_config(environment: str = None) -> Type[Config]:
    """
    Factory function para obtener la configuración según el entorno.
    
    Args:
        environment: Nombre del entorno ('development', 'test', 'production')
                   Si es None, usa la variable de entorno FLASK_ENV
    
    Returns:
        Clase de configuración correspondiente al entorno
    """
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    config_map: Dict[str, Type[Config]] = {
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'test': TestConfig,
        'testing': TestConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig
    }
    
    return config_map.get(environment.lower(), DevelopmentConfig)


# Mantener compatibilidad con código existente
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig
}
