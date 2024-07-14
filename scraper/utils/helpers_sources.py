from typing import List
from Hikoky.models.paths import insert_chapter
from Hikoky.models import ChapterDetails, NavigationLink


def save_manga_chapter_paths(source: str, manga_path, chapters: List["ChapterDetails"]):
    if manga_path:
        chapter_paths = [chapter.save(source, manga_path) for chapter in chapters]
        insert_chapter(chapter_paths)


def create_navigation_link(
    source: str, chapter_link: str, manga_path: str, chapter_num: str
) -> NavigationLink:
    if manga_path:
        navigation = NavigationLink(chapterNum=chapter_num, chapterUrl=chapter_link)
        navigation.save(source=source, manga_path=manga_path, number=chapter_num)
        return navigation
