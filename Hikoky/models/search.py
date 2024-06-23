from sqlalchemy import create_engine, Column, String, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import List, Optional

Base = declarative_base()

class Search(Base):
    __tablename__ = 'search'

    name = Column(String, primary_key=True)
    link = Column(Text, nullable=False)
    cover = Column(Text, nullable=True)
    badge = Column(Text, nullable=True)
    source = Column(String, primary_key=True)

    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_source', 'source'),
    )

    engine = None
    Session = None

    def __init__(self, name, link, cover=None, badge=None, source=None):
        self.name = name
        self.link = link
        self.cover = cover
        self.badge = badge
        self.source = source

    @classmethod
    def init_db(cls):
        if cls.engine is None:
            cls.engine = create_engine('sqlite:///search.db', echo=True)
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

    def save(self):
        with self.get_session() as session:
            session.merge(self)
            session.commit()

    @classmethod
    def search_by_source(cls, source, keyword):
        with cls.get_session() as session:
            pattern = f"%{keyword}%"
            return session.query(cls).filter(cls.source == source, cls.name.like(pattern)).all()

    @classmethod
    def search_by_name(cls, keyword):
        with cls.get_session() as session:
            pattern = f"%{keyword}%"
            return session.query(cls).filter(cls.name.like(pattern)).all()

    @classmethod
    def get_all_data(cls):
        with cls.get_session() as session:
            return session.query(cls).all()


""""
# استخدام الكود
# إضافة سجل جديد
new_search = Search(name='Example', link='http://example.com', cover='cover.jpg', badge='badge.png', source='example_source')
new_search.save()

# البحث حسب المصدر
results = Search.search_by_source('example_source', 'Example')
for result in results:
    print(result.name, result.link)

# البحث حسب الاسم
results = Search.search_by_name('Example')
for result in results:
    print(result.name, result.link)

# استعراض جميع البيانات
all_data = Search.get_all_data()
for data in all_data:
    print(data.name, data.link)
"""

















# import sqlite3
# from typing import List, Optional
# from dataclasses import dataclass, asdict

# class Search:
#     def __init__(self, name, link, cover=None, badge=None, source=None):
#         self.name = name
#         self.link = link
#         self.cover = cover
#         self.badge = badge
#         self.source = source

#     @classmethod
#     def create_table(cls):
#         conn = sqlite3.connect('search.db')
#         cursor = conn.cursor()
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Search (
#             name TEXT,
#             link TEXT,
#             cover TEXT,
#             badge TEXT,
#             source TEXT,
#             PRIMARY KEY (name, source)
#         )
#         ''')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON Search (name)')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON Search (source)')
#         conn.commit()
#         conn.close()

#     def save(self):
#         conn = sqlite3.connect('search.db')
#         cursor = conn.cursor()
#         cursor.execute('''
#         INSERT INTO Search (name, link, cover, badge, source) 
#         VALUES (?, ?, ?, ?, ?)
#         ON CONFLICT(name, source) DO UPDATE SET
#             link=excluded.link,
#             cover=excluded.cover,
#             badge=excluded.badge
#         ''', (self.name, self.link, self.cover, self.badge, self.source))
#         conn.commit()
#         conn.close()

#     @classmethod
#     def search_by_source(cls, source, keyword):
#         conn = sqlite3.connect('search.db')
#         cursor = conn.cursor()
#         pattern = f"%{keyword}%"
#         query = 'SELECT * FROM Search WHERE source = ? AND name LIKE ?'
#         cursor.execute(query, (source, pattern))
#         results = cursor.fetchall()
#         conn.close()
#         return results

#     @classmethod
#     def search_by_name(cls, keyword):
#         conn = sqlite3.connect('search.db')
#         cursor = conn.cursor()
#         pattern = f"%{keyword}%"
#         query = 'SELECT * FROM Search WHERE name LIKE ?'
#         cursor.execute(query, (pattern,))
#         results = cursor.fetchall()
#         conn.close()
#         return results

#     @classmethod
#     def get_all_data(cls):
#         conn = sqlite3.connect('search.db')
#         cursor = conn.cursor()
#         query = 'SELECT * FROM Search'
#         cursor.execute(query)
#         results = cursor.fetchall()
#         conn.close()
#         return results

# # Create the table
# Search.create_table()
