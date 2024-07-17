from bs4 import BeautifulSoup
from scraper import pyparse
from scraper.utils import Failed_retrieve, notfound
from Hikoky.models.search import Search, SearchDetails
from typing import Optional, Tuple
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

source = "Team-X"
base_url = "https://teamoney.site/"


async def home(url) -> Home:
    soup = await pyparse(url)

    boxes = soup.find_all("div", class_="box")

    mangas = []
    for box in boxes:
        img_div = box.find("div", class_="imgu")

        chapters = []
        info_div = box.find("div", class_="info")
        tagA = info_div.find_all("a")
        for chapter in tagA[1:4]:
            latest_chapters = LatestChapters(
                number=chapter.text.strip().split()[-1], url=chapter["href"]
            )
            chapters.append(latest_chapters)

        mangas.append(
            MangaDetails(
                name=img_div.find("img")["alt"],
                link=img_div.find("a")["href"],
                cover=img_div.find("img")["src"],
                latestChapters=chapters,
            )
        )

    next_url = await get_next_page_url(soup)
    return Home(source=source, mangaData=mangas, nextUrl=next_url)


"""end home"""


async def manga(url: str) -> Manga:
    soup = await pyparse(url=url)

    container = soup.find("div", class_="container")
    info_box = container.find_all("div", class_="whitebox")[1]

    genres = info_box.find("div", class_="review-author-info")
    genres = [a.get_text(strip=True) for a in genres.find_all("a", class_="subtitle")]

    chapter_text = container.find("a", class_="nav-link").text
    chapter_number = "".join(filter(str.isdigit, chapter_text))

    info_manga = MangaInfo(
        name=info_box.find("div", class_="author-info-title").find("h1").text.strip(),
        cover=container.find("img", class_="shadow-sm")["src"],
        genres=genres,
        aboutStory=info_box.find("div", class_="review-content").p.get_text(strip=True),
        totalChapters=chapter_number,
    )

    chapters = []
    chapter_urls = container.find("div", class_="eplister").find("ul")
    for chapter_item in chapter_urls.find_all("li"):
        all_info = chapter_item.find("a")

        chapter_text = container.find("a", class_="nav-link").text
        chapter_number = (
            all_info.find_all("div", class_="epl-num")[1].text.strip().split()[-1]
        )
        chapter_title = all_info.find("div", class_="epl-title").get_text(strip=True)
        date = all_info.find("div", class_="epl-date").get_text(strip=True)

        chapter_details = ChapterDetails(
            number=chapter_number,
            link=all_info["href"],
            title=chapter_title if chapter_title else "N/A",
            date=date,
        )
        chapters.append(chapter_details)

    next_page_link = await get_next_page_url(container)
    return Manga(
        source=source,
        mangaList=info_manga,
        chapters=chapters,
        nextPageLink=next_page_link,
    )


"""end manga"""


async def chapter(url: str) -> Chapter:
    soup = await pyparse(url=url)

    # Extract URL this chapter
    url = soup.find("meta", property="og:url").get("content")

    # Extract image URLs from the page-break divs
    reader_area = soup.find_all("div", class_="page-break")
    image_urls = [
        img.get("src")
        for div in reader_area
        for img in div.find_all("img")
        if img.get("src")
    ]

    # Get chapter title
    title_element = soup.find("h1", id="chapter-heading")
    title = title_element.text.strip() if title_element else None
    chapter_number = await get_num(url)
    title = (
        f"{title} | Chapter {chapter_number}" if title else f"Chapter {chapter_number}"
    )

    # Extract next and previous chapter navigation links
    container = soup.find("div", class_="container")

    prev_navigation = await create_navigation_link(container, "prev-chapter")
    next_navigation = await create_navigation_link(container, "next-chapter")

    return Chapter(
        source=source,
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )


#  --Helper functions--
#  Creates a navigation link by getting the chapter link and chapter number.
async def create_navigation_link(
    container: BeautifulSoup, chapter_id: str
) -> Optional[NavigationLink]:
    chapter_link = await get_chapter_link(container, chapter_id)

    chapter_num = await get_num(chapter_link)
    return NavigationLink(chapterPath=chapter_num, chapterUrl=chapter_link)


#  Retrieves the chapter link based on the given chapter ID.
async def get_chapter_link(container: BeautifulSoup, chapter_id: str) -> Optional[str]:
    chapter_element = container.find("a", id=chapter_id)
    if chapter_element and chapter_element["href"] != "#":
        return chapter_element["href"]
    return None


#  Extracts the numeric part from a URL.
async def get_num(url: str) -> Optional[str]:
    if url:
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
    return None


"""end chapter"""


# --Common functions--
async def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_page = soup.find("a", rel="next")
    if next_page and next_page.has_attr("href"):
        return next_page["href"]
    return None


# Searches for manga based on a keyword.
async def search(keyword: str):
    url = "https://www.teamoney.site/ajax/search"
    params = {"keyword": keyword}
    response = await pyparse(url=url, max_retries=2, params=params)
    if response:
        list_group = response.find("ol", class_="list-group")
        if list_group and list_group.find_all():
            results = response.find_all("li", class_="list-group-item")
            data = []
            for manga in results:
                search_details = SearchDetails(
                    name=manga.find("a", class_="fw-bold").text.strip(),
                    link=manga.find("a", class_="fw-bold")["href"],
                    cover=manga.find("img")["src"] if manga.find("img") else None,
                    badge=(
                        manga.find("span", class_="badge").text.strip()
                        if manga.find("span", "badge")
                        else None
                    ),
                )
                data.append(search_details)
            return Search(source=source, results=data)
        else:
            raise await notfound(source)
    else:
        raise await Failed_retrieve(source)
