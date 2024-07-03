from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from contextlib import contextmanager

Base = declarative_base()

class Database:
    engine = None
    Session = None

    @classmethod
    def init_db(cls, db_url: str = 'sqlite:///Hikoky/models/database/Hikoky.db'):
        if cls.engine is None:
            cls.engine = create_engine(db_url, echo=True)
            Base.metadata.create_all(cls.engine)
            cls.Session = scoped_session(sessionmaker(bind=cls.engine))

    @classmethod
    @contextmanager
    def get_session(cls):
        cls.init_db()
        session = cls.Session()
        try:
            yield session
        finally:
            session.close()
