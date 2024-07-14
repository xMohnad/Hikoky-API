import os
from pymongo import MongoClient, ASCENDING, UpdateOne
from pymongo.server_api import ServerApi

from fastapi import HTTPException
import re


def generate_manga_path(name: str):
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = name.replace(" ", "-").replace("_", "-")
    name = name.lower()
    return name


database_url = os.getenv("DATABASE_URL")

if database_url is None:
    raise ValueError("The DATABASE_URL environment variable is not set")

client = MongoClient(
    database_url,
    server_api=ServerApi("1"),
    tls=True,
    tlsAllowInvalidCertificates=True,
)

db = client["hikoky-api"]


# ===============================================================
def insert_manga(data):
    collection = db["MangaPath"]
    operations = [
        UpdateOne(
            {"source": item["source"], "manga_path": item["manga_path"]},
            {"$set": item},
            upsert=True,
        )
        for item in data
    ]
    collection.bulk_write(operations)


def insert_chapter(data):
    collection = db["ChapterPath"]
    operations = [
        UpdateOne(
            {
                "source": item["source"],
                "manga_path": item["manga_path"],
                "chapter_num": item["chapter_num"],
            },
            {"$set": item},
            upsert=True,
        )
        for item in data
    ]
    collection.bulk_write(operations)


# =============================================================
def get_link_manga(source, manga_path):
    collection = db["MangaPath"]
    result = collection.find_one(
        {"source": source, "manga_path": manga_path}, {"_id": 0, "link": 1}
    )
    if result:
        return result.get("link")

    raise HTTPException(
        status_code=404,
        detail={"error": "Manga not available. Please check the path validity."},
        headers={"X-Error": "Manga Not Available - Possible path error"},
    )


def get_link_chapter(source, manga_path, chapter_num):
    collection = db["ChapterPath"]
    result = collection.find_one(
        {"source": source, "manga_path": manga_path, "chapter_num": chapter_num},
        {"_id": 0, "link": 1},
    )
    if result:
        return result.get("link")

    raise HTTPException(
        status_code=404,
        detail={"error": "Chapter not available. Please check the path validity."},
        headers={"X-Error": "Chapter Not Available - Possible path error"},
    )
