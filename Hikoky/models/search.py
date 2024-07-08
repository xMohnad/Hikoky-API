# app/models/search.py
from fastapi import HTTPException
from typing import Optional

from sqlalchemy import Column, String, Text, Index
from .session import Base, Database


class Search(Base):
    __tablename__ = "search"

    source = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    link = Column(Text, nullable=False)
    cover = Column(Text, nullable=True)
    badge = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_name", "name"),
        Index("idx_source", "source"),
    )

    def __init__(self, name, link, cover=None, badge=None, source=None):
        self.name = name
        self.link = link
        self.cover = cover
        self.badge = badge
        self.source = source

    def save(self):
        with Database.get_session() as session:
            session.merge(self)
            session.commit()

    @classmethod
    def search_by_source(cls, source, keyword):
        with Database.get_session() as session:
            pattern = f"%{keyword}%"
            return (
                session.query(cls)
                .filter(cls.source == source, cls.name.like(pattern))
                .all()
            )

    @classmethod
    def search_by_name(cls, keyword):
        with Database.get_session() as session:
            pattern = f"%{keyword}%"
            return session.query(cls).filter(cls.name.like(pattern)).all()

    @classmethod
    def get_all_data(cls):
        with Database.get_session() as session:
            return session.query(cls).all()

    @classmethod
    def perform_search(cls, source: Optional[str], keyword: str):
        if source:
            with Database.get_session() as session:
                if not session.query(cls).filter(cls.source == source).first():
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "success": False,
                            "Error": f"Invalid source, No source found {source}",
                            "message": "المصدر غير متوفر",
                        },
                    )

            result = cls.search_by_source(source, keyword)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "Error": f"not found in {source}",
                        "message": "لا توجد مانجا",
                    },
                )
            return result

        else:
            search_results = cls.search_by_name(keyword)
            if not search_results:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "Error": "not found in any source",
                        "message": "لا توجد مانجا في أي مصدر",
                    },
                )

            return search_results
