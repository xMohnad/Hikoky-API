import logging
from scraper.utils import Failed_retrieve, notfound
from scraper import pyparse
from bs4 import BeautifulSoup
import logging
from Hikoky.models import (
    Home,
    Manga,
    Chapter,
    MangaDetails,
    LatestChapters,
    MangaDetails,
    MangaInfo,
    ChapterDetails,
    NavigationLink,
)
from typing import Optional


source = "Team-X"
base_url = "https://www.teamxnovel.com/"


# =============================================
async def home(soup: BeautifulSoup) -> Home:
    boxes = soup.find_all("div", class_="box")

    data_mangas = []
    for box in boxes:
        img_div = box.find("div", class_="imgu")
        link = img_div.find("a")["href"]
        name = img_div.find("img")["alt"]
        cover = img_div.find("img")["src"]

        chapters = []
        info_div = box.find("div", class_="info")
        tagA = info_div.find_all("a")
        for chapter in tagA[1:4]:
            chapter_url = chapter["href"]
            chapter_num = chapter.text.strip().split()[-1]
            latest_chapters = LatestChapters(num=chapter_num, url=chapter_url)
            latest_chapters.saver(source, name)
            chapters.append(latest_chapters)
        manga_data = MangaDetails(
            name=name, link=link, cover=cover, team=None, latestChapters=chapters
        )
        manga_data.saver(source)
        data_mangas.append(manga_data)
    next_url = await get_next_page_url(soup)

    return Home(mangaData=data_mangas, nextUrl=next_url)


# =============================================================================
async def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_page = soup.find("a", rel="next")
    if next_page and next_page.has_attr("href"):
        return next_page["href"]
    return None


# =============================================================================
async def manga(soup: BeautifulSoup, manga_path: str = None) -> Manga:
    container = soup.find("div", class_="container")

    cover_manga = container.find("img", class_="shadow-sm")["src"]
    info_box = container.find_all("div", class_="whitebox")[1]
    manga_name = (
        info_box.find("div", class_="author-info-title").find("h1").text.strip()
    )

    genres = info_box.find("div", class_="review-author-info")
    genres = [a.get_text(strip=True) for a in genres.find_all("a", class_="subtitle")]

    about_story = info_box.find("div", class_="review-content").p.get_text(strip=True)
    chapter_text = container.find("a", class_="nav-link").text

    chapter_number = "".join(filter(str.isdigit, chapter_text))

    info_manga = MangaInfo(
        name=manga_name,
        cover=cover_manga,
        genres=genres,
        aboutStory=about_story,
        totalChapters=chapter_number,
    )

    chapters = []
    chapter_urls = container.find("div", class_="eplister").find("ul")
    for chapter_item in chapter_urls.find_all("li"):
        all_info = chapter_item.find("a")

        chapter_url = all_info["href"]
        chapter_text = container.find("a", class_="nav-link").text

        chapter_number = (
            all_info.find_all("div", class_="epl-num")[1].text.strip().split()[-1]
        )
        chapter_title = all_info.find("div", class_="epl-title").get_text(strip=True)

        date = all_info.find("div", class_="epl-date").get_text(strip=True)

        chapter_details = ChapterDetails(
            number=chapter_number,
            link=chapter_url,
            title=chapter_title if chapter_title else "N/A",
            date=date,
        )

        chapter_details.saver(source, manga_path)
        chapters.append(chapter_details)

    next_page_link = await get_next_page_url(container)
    return Manga(mangaList=info_manga, chapters=chapters, nextPageLink=next_page_link)


# ==========================================================================


async def chapter(soup: BeautifulSoup, url: str, manga_path=None) -> Chapter:

    reader_area = soup.find_all("div", class_="page-break")
    image_urls = [
        img.get("src")
        for div in reader_area
        for img in div.find_all("img")
        if img.get("src")
    ]
    if not image_urls:
        logging.error("Images not found.")

    title_element = soup.find("h1", id="chapter-heading")
    title = title_element.text.strip() if title_element else None
    chapter_number = get_num(url)
    title = f"{title} | الفصل {chapter_number}" if title else f"الفصل {chapter_number}"

    next_navigation, prev_navigation = await extract_chapter_links(soup, manga_path)

    return Chapter(
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )


async def extract_chapter_links(soup: BeautifulSoup, manga_path: str) -> tuple:
    async def get_chapter_link(
        container: BeautifulSoup, chapter_id: str
    ) -> Optional[str]:
        chapter_element = container.find("a", id=chapter_id)
        if chapter_element and chapter_element["href"] != "#":
            return chapter_element["href"]
        return None

    async def create_navigation_link(
        container: BeautifulSoup, chapter_id: str
    ) -> NavigationLink:
        chapter_link = await get_chapter_link(container, chapter_id)
        navigation = NavigationLink(chapterUrl=chapter_link)
        chapter_num = await get_num(chapter_link)
        navigation.saver(source=source, manga_path=manga_path, number=chapter_num)
        return navigation

    container = soup.find("div", class_="container")

    prev_navigation = await create_navigation_link(container, "prev-chapter")
    next_navigation = await create_navigation_link(container, "next-chapter")

    return next_navigation, prev_navigation


async def get_num(url: str) -> Optional[str]:
    if url:
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
    return None


async def search(keyword: str):
    url = "https://www.teamxnovel.com/ajax/search"
    params = {"keyword": keyword}
    response = await pyparse(url=url, max_retries=1, params=params)

    if response:
        list_group = response.find("ol", class_="list-group")
        if list_group and list_group.find_all():
            results = response.find_all("li", class_="list-group-item")
            data = []
            for manga in results:
                title = manga.find("a", class_="fw-bold").text.strip()
                link = manga.find("a", class_="fw-bold")["href"]
                cover = manga.find("img")["src"] if manga.find("img") else None
                badge = (
                    manga.find("span", class_="badge").text.strip()
                    if manga.find("span", "badge")
                    else None
                )
                data.append(
                    {
                        "title": title,
                        "link": link,
                        "cover": cover,
                        "type": None,
                        "badge": badge,
                    }
                )
            return {"source": source, "data": data}
        else:
            raise await notfound(source)
    else:
        logging.error(f"Failed to retrieve data in {source}")
        raise await Failed_retrieve(source)
