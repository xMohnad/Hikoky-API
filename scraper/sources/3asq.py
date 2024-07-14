import logging, re
from typing import Optional
from bs4 import BeautifulSoup
from scraper import pyparse
from Hikoky.models import (
    Home,
    Manga,
    Chapter,
    MangaDetails,
    LatestChapters,
    MangaInfo,
    ChapterDetails,
    NavigationLink,
)
from scraper.utils.helpers_sources import save_manga_chapter_paths

source = "3asq"
base_url = "https://3asq.org/manga/"


async def home(soup: BeautifulSoup):
    items = soup.find_all("div", class_="page-item-detail")

    mangas = []
    for item in items:
        name_tag = item.find("h3", class_="h5")
        name = name_tag.find_all("a")[-1].text.strip()
        link = name_tag.find_all("a")[-1]["href"]

        img_tag = item.find("div", class_="item-thumb hover-details c-image-hover").a
        cover = (
            [
                entry.split(" ")[0]
                for entry in img_tag.find("img")["srcset"].split(", ")
            ][-1]
            if img_tag
            else "N/A"
        )

        translation_team_tag = item.find("span", class_="manga-title-badges")
        team = translation_team_tag.text.strip() if translation_team_tag else None

        chapters_tags = item.find_all("div", class_="chapter-item")
        chapters = []

        for chapter_tag in chapters_tags[:2]:
            chapter_url = chapter_tag.find("a")["href"]
            chapter_text = chapter_tag.find("a").text.strip()
            chapter_num = await extract_chapter_number(chapter_text)

            latest_chapter = LatestChapters(num=chapter_num, url=chapter_url)
            latest_chapter.save(source, name)
            chapters.append(latest_chapter)

        mangas.append(
            MangaDetails(
                name=name, link=link, cover=cover, team=team, latestChapters=chapters
            )
        )

    next_url = await extract_next_page_url(soup)
    return Home(source=source, mangaData=mangas, nextUrl=next_url)


async def extract_chapter_number(text):
    match = re.match(r"^\D*(\d+)", text)
    return match.group(1) if match else text


async def extract_next_page_url(soup):
    div_tag = soup.find("div", class_="nav-previous float-left")
    aTag = div_tag.find("a") if div_tag else None
    return aTag["href"] if aTag else None


# ===============================================================================================
async def extract_chapter_info(title):
    match = re.match(r"(\d+(\.\d+)?[A-Za-z]*)\s*-\s*(.*)", title)
    if match:
        chapter_number = re.sub(r"[A-Z]", "", match.group(1))
        chapter_title = match.group(3) if match.group(3) else "N/A"
    else:
        chapter_number = title.strip()
        chapter_title = "N/A"

    return chapter_number, chapter_title


async def manga(soup: BeautifulSoup, manga_path: str = None) -> Manga:
    name = soup.find("div", class_="post-title").find("h1").text.strip()

    about_story = soup.find("div", class_="manga-excerpt")
    about_story = about_story.p.get_text(strip=True) if about_story else "N/A"

    genres = [
        a.get_text(strip=True)
        for a in soup.find("div", class_="genres-content").find_all("a")
    ]
    cover_manga = soup.find("div", class_="summary_image").find("img")["src"]

    info_manga = MangaInfo(
        name=name,
        cover=cover_manga,
        genres=genres,
        aboutStory=about_story,
    )

    chapters = []
    ul = soup.select_one(
        "div.main-col.col-md-8.col-sm-8 > div > div.c-page > div > div.page-content-listing.single-page > div > ul"
    )
    for li in ul.find_all("li", class_="wp-manga-chapter"):
        aTag = li.find("a")
        chapter_url = aTag["href"]
        date = li.find("span", class_="chapter-release-date").get_text(strip=True)

        chapterTitleText = aTag.text.strip()
        chapter_number, chapter_title = await extract_chapter_info(chapterTitleText)

        chapter_details = ChapterDetails(
            number=chapter_number,
            link=chapter_url,
            title=chapter_title if chapter_title else "N/A",
            date=date,
        )
        chapter_details.save(source, manga_path)
        chapters.append(chapter_details)

    save_manga_chapter_paths(source, manga_path, chapters)
    return Manga(
        source=source,
        mangaList=info_manga,
        chapters=chapters,
    )


# ====================================================================================
async def chapter(soup: BeautifulSoup, url: str, manga_path=None) -> Chapter:
    img_tag = soup.select(".page-break img.wp-manga-chapter-img")
    image_urls = [img["src"].strip() for img in img_tag]

    active_li = soup.find("li", class_="active")
    title = active_li.text.strip() if active_li else None

    next_navigation, prev_navigation = await extract_chapter_links(soup, manga_path)

    return Chapter(
        source=source,
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )


async def extract_chapter_links(soup: BeautifulSoup, manga_path: str) -> tuple:
    async def get_chapter_link(
        nav_links: BeautifulSoup, class_name: str
    ) -> Optional[str]:
        try:
            link_tag = nav_links.find("a", class_=class_name)
            return link_tag["href"] if link_tag else None
        except (TypeError, KeyError, AttributeError):
            return None

    async def create_navigation_link(
        nav_links: BeautifulSoup, class_name: str
    ) -> NavigationLink:
        chapter_link = await get_chapter_link(nav_links, class_name)
        chapter_num = await get_num(chapter_link)
        navigation = NavigationLink(chapterNum=chapter_num, chapterUrl=chapter_link)
        navigation.save(source=source, manga_path=manga_path, number=chapter_num)
        return navigation

    nav_links = soup.find("div", class_="nav-links")

    next_navigation = await create_navigation_link(nav_links, "btn next_page")
    prev_navigation = await create_navigation_link(nav_links, "btn prev_page")

    return next_navigation, prev_navigation


async def get_num(url: str) -> Optional[str]:
    if url:
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            match = re.search(r"\d+", part)
            if match:
                return match.group(0)
            else:
                return parts[-1]
    return None


# ==============================================
from scraper.utils import Failed_retrieve, notfound
from Hikoky.models.search import Search, SearchDetails


async def search(keyword: str):
    url = "https://3asq.org/wp-admin/admin-ajax.php"
    data = {
        "action": "wp-manga-search-manga",
        "title": keyword,
    }

    response = await pyparse(url=url, max_retries=2, method="POST", data=data)

    if response.get("success", False):
        result = response.get("data", [])
        if result:
            data = []
            for manga in result:
                title = manga.get("title")
                link = manga.get("url")
                type_ = manga.get("type")

                search_details = SearchDetails(name=title, link=link, type=type_)
                search_details.save(source)
                data.append(search_details)

            return Search(source=source, result=data)
    else:
        error_data = response.get("data", [{}])[0]
        error_type = error_data.get("error", "Failed to retrieve data")
        if error_type == "not found":
            raise await notfound(source)
        else:
            logging.error(f"Failed to retrieve data in {source}")
            raise await Failed_retrieve(source)
