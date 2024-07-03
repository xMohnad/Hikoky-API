from sqlalchemy import Column, String, Text, Index
from sqlalchemy import func

from .session import Database, Base

from fastapi import HTTPException
import re

# from sqlalchemy.orm import declarative_base
# Base = declarative_base()



def generate_manga_path(name: str):
    name = re.sub(r'[^\w\s-]', '', name, flags=re.UNICODE)
    name = name.replace(" ", "-").replace("_", "-")
    name = name.lower()
    return name

class PathManga(Base):
    __tablename__ = 'mangaPath'

    source = Column(String, primary_key=True)
    path = Column(String, primary_key=True)
    link = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_source', 'source'),
        Index('idx_path', 'path'),
    )

    def __init__(self, source, path, link):
        self.source = source
        self.path = path
        self.link = link

    def add_path(self):
        with Database.get_session() as session:
            session.merge(self)
            session.commit()
            
    @classmethod
    def get_link(cls, source, path):
        with Database.get_session() as session:
            link = session.query(PathManga.link).filter(
                func.lower(PathManga.source) == func.lower(source),
                func.lower(PathManga.path) == func.lower(path)
        ).scalar()
        if link:
            return link
        else:
            raise HTTPException(
            status_code=404,
            detail={"error": "Manga not available. Please check the path validity."},
            headers={"X-Error": "Manga Not Available - Possible path error"},
        )
    
    @classmethod
    def get_all_data(cls):
        with Database.get_session() as session:
            return session.query(cls).all()

# Database.init_db()

"""
new_path = PathManga("3asq","boruto", "www.3asq.com/boruto")
new_path.add_path()
link = PathManga.get_all_data()
"""