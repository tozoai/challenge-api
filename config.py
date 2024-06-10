import os

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_STRING')
    MONGO_AUTH = os.environ.get('MONGO_AUTH')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
