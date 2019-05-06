class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    debug = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:Frankline@localhost/project_db"