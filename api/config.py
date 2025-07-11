class Config:
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    #'postgresql://postgres:Dimichev3.@localhost:5432/tecnoexpress'
    #postgresql://tecnoexpress_user:z4V8ZmwzObW0J9odCXY69rFMYFKVGIoz@dpg-cv3ngj7noe9s738n58qg-a.oregon-postgres.render.com/tecnoexpress
    # internal connection : postgresql://tecnoexpress_t9ja_user:NvvQL6uRAGCdwzNPzYSFJhgO9TIVQThX@dpg-cvnvbo3e5dus73e1t47g-a/tecnoexpress_t9ja
    SQLALCHEMY_DATABASE_URI = 'postgresql://tecnoexpress_owner:npg_zNdIya8tj6TG@ep-round-paper-acxjrr4q-pooler.sa-east-1.aws.neon.tech/tecnoexpress?sslmode=require&channel_binding=require'   

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