class Config:
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    #'postgresql://postgres:Dimichev3.@localhost:5432/tecnoexpress'
    #postgresql://tecnoexpress_user:z4V8ZmwzObW0J9odCXY69rFMYFKVGIoz@dpg-cv3ngj7noe9s738n58qg-a.oregon-postgres.render.com/tecnoexpress
    # internal connection : postgresql://tecnoexpress_user:z4V8ZmwzObW0J9odCXY69rFMYFKVGIoz@dpg-cv3ngj7noe9s738n58qg-a/tecnoexpress
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Dimichev3.@localhost:5432/tecnoexpress'
    SQLALCHEMY_TRACK_MODIFICATIONS = False



class TestConfig(Config):
    DEBUG = False  
    TESTING = True  # Activa el modo de pruebas en Flask
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Dimichev3.@localhost:5432/test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'test': TestConfig,
}