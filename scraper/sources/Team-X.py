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
    MangaDetails,
    MangaInfo,
    ChapterDetails,
    NavigationLink,
)

source = "Team-X"
base_url = "https://www.teamxnovel.com/"


async def home(soup: BeautifulSoup) -> Home:
    boxes = soup.find_all("div", class_="box")

    mangas = []
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

            latest_chapters = LatestChapters(number=chapter_num, url=chapter_url)
            chapters.append(latest_chapters)

        mangas.append(
            MangaDetails(name=name, link=link, cover=cover, latestChapters=chapters)
        )

    next_url = await get_next_page_url(soup)
    return Home(source=source, mangaData=mangas, nextUrl=next_url)


"""end home"""


async def manga(soup: BeautifulSoup) -> Manga:
    container = soup.find("div", class_="container")

    cover_manga = container.find("img", class_="shadow-sm")["src"]
    info_box = container.find_all("div", class_="whitebox")[1]
    name = info_box.find("div", class_="author-info-title").find("h1").text.strip()
    genres = info_box.find("div", class_="review-author-info")
    genres = [a.get_text(strip=True) for a in genres.find_all("a", class_="subtitle")]
    about_story = info_box.find("div", class_="review-content").p.get_text(strip=True)

    chapter_text = container.find("a", class_="nav-link").text
    chapter_number = "".join(filter(str.isdigit, chapter_text))

    info_manga = MangaInfo(
        name=name,
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
        chapters.append(chapter_details)

    next_page_link = await get_next_page_url(container)
    return Manga(
        source=source,
        mangaList=info_manga,
        chapters=chapters,
        nextPageLink=next_page_link,
    )


"""end manga"""


async def chapter(soup: BeautifulSoup) -> Chapter:
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
    next_navigation, prev_navigation = await extract_chapter_links(soup)

    return Chapter(
        source=source,
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )


# Extracts the next and previous chapter navigation links.
async def extract_chapter_links(
    soup: BeautifulSoup,
) -> Tuple[Optional[NavigationLink], Optional[NavigationLink]]:
    container = soup.find("div", class_="container")

    prev_navigation = await create_navigation_link(container, "prev-chapter")
    next_navigation = await create_navigation_link(container, "next-chapter")

    return next_navigation, prev_navigation


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
    url = "https://www.teamxnovel.com/ajax/search"
    params = {"keyword": keyword}
    response = await pyparse(url=url, max_retries=2, params=params)

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
                search_details = SearchDetails(
                    name=title, link=link, cover=cover, badge=badge
                )
                data.append(search_details)
            return Search(source=source, results=data)
        else:
            raise await notfound(source)
    else:
        raise await Failed_retrieve(source)
