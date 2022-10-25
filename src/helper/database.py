from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from helper.configSQL import config

database_url = 'mysql+mysqlconnector://{}:{}@{}/{}?charset=utf8mb4'.format(config['user'], config['password'],
                                                                               config['host'], 'china_stock_wiki')
sqlEngine = create_engine(database_url, pool_recycle=3600)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=sqlEngine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import helper.models
    Base.metadata.create_all(bind=sqlEngine)