import sqlite3
from typing import List, Optional
from dataclasses import dataclass, asdict

class Search:
    def __init__(self, name, link, cover=None, badge=None, source=None):
        self.name = name
        self.link = link
        self.cover = cover
        self.badge = badge
        self.source = source

    @classmethod
    def create_table(cls):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Search (
            name TEXT,
            link TEXT,
            cover TEXT,
            badge TEXT,
            source TEXT,
            PRIMARY KEY (name, source)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON Search (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON Search (source)')
        conn.commit()
        conn.close()

    def save(self):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Search (name, link, cover, badge, source) 
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name, source) DO UPDATE SET
            link=excluded.link,
            cover=excluded.cover,
            badge=excluded.badge
        ''', (self.name, self.link, self.cover, self.badge, self.source))
        conn.commit()
        conn.close()

    @classmethod
    def search_by_source(cls, source, keyword):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        pattern = f"%{keyword}%"
        query = 'SELECT * FROM Search WHERE source = ? AND name LIKE ?'
        cursor.execute(query, (source, pattern))
        results = cursor.fetchall()
        conn.close()
        return results

    @classmethod
    def search_by_name(cls, keyword):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        pattern = f"%{keyword}%"
        query = 'SELECT * FROM Search WHERE name LIKE ?'
        cursor.execute(query, (pattern,))
        results = cursor.fetchall()
        conn.close()
        return results

    @classmethod
    def get_all_data(cls):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        query = 'SELECT * FROM Search'
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

# Create the table
Search.create_table()
