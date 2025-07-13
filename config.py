class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:3672@localhost/mechanic_db'
    DEBUG = True

class TestingConfig:
    pass

class ProductionConfig:
    pass