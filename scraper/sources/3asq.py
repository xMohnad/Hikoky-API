import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from scraper import pyparse
from scraper.utils import Failed_retrieve, notfound
from Hikoky.models.search import Search, SearchDetails
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

source = "3asq"
base_url = "https://3asq.org/manga/"


# Extracts manga details from the home page
async def home(url: str) -> Home:
    soup = await pyparse(url=url)

    items = soup.find_all("div", class_="page-item-detail")

    mangas = []
    for item in items:
        # Extract manga name and link
        name_tag = item.find("h3", class_="h5")
        name = name_tag.find_all("a")[-1].text.strip()
        link = name_tag.find_all("a")[-1]["href"]

        # Extract cover image URL
        img_tag = item.find("div", class_="item-thumb hover-details c-image-hover").a
        cover = (
            [
                entry.split(" ")[0]
                for entry in img_tag.find("img")["srcset"].split(", ")
            ][-1]
            if img_tag
            else "N/A"
        )

        # Extract translation team
        translation_team_tag = item.find("span", class_="manga-title-badges")
        team = translation_team_tag.text.strip() if translation_team_tag else None

        # Extract latest chapters
        chapters_tags = item.find_all("div", class_="chapter-item")

        chapters = []
        for chapter_tag in chapters_tags[:2]:
            chapter_num = await extract_chapter_number(
                chapter_tag.find("a").text.strip()
            )
            latest_chapter = LatestChapters(
                number=chapter_num, url=chapter_tag.find("a")["href"]
            )
            chapters.append(latest_chapter)

        # Append manga details to the list
        mangas.append(
            MangaDetails(
                name=name, link=link, cover=cover, team=team, latestChapters=chapters
            )
        )

    # Extract next page URL
    next_url = await extract_next_page_url(soup)
    return Home(source=source, mangaData=mangas, nextUrl=next_url)


# Extracts chapter number from a given text string.
async def extract_chapter_number(text: str) -> str:
    match = re.match(r"^\D*(\d+)", text)
    return match.group(1) if match else text


# --Helper functions--
# Extracts the URL of the next page from the home page.
async def extract_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    div_tag = soup.find("div", class_="nav-previous float-left")
    aTag = div_tag.find("a") if div_tag else None
    return aTag["href"] if aTag else None


"""end home"""


# Extracts manga details from the manga page
async def manga(url: str) -> Manga:
    soup = await pyparse(url=url)

    # Extract manga description
    about_story = soup.find("div", class_="manga-excerpt")
    about_story = about_story.p.get_text(strip=True) if about_story else "N/A"

    # Create MangaInfo object
    info_manga = MangaInfo(
        name=soup.find("div", class_="post-title").find("h1").text.strip(),
        cover=soup.find("div", class_="summary_image").find("img")["src"],
        genres=[
            a.get_text(strip=True)
            for a in soup.find("div", class_="genres-content").find_all("a")
        ],
        aboutStory=about_story,
    )

    # Extract chapters
    chapters = []
    ul = soup.select_one(
        "div.main-col.col-md-8.col-sm-8 > div > div.c-page > div > div.page-content-listing.single-page > div > ul"
    )
    for li in ul.find_all("li", class_="wp-manga-chapter"):
        aTag = li.find("a")
        chapterTitleText = aTag.text.strip()
        chapter_number, chapter_title = await extract_chapter_info(chapterTitleText)

        # Create ChapterDetails object
        chapter_details = ChapterDetails(
            number=chapter_number,
            link=aTag["href"],
            title=chapter_title if chapter_title else "N/A",
            date=li.find("span", class_="chapter-release-date").get_text(strip=True),
        )
        chapters.append(chapter_details)

    # Return Manga object
    return Manga(
        source=source,
        mangaList=info_manga,
        chapters=chapters,
    )


#  --Helper functions--
# Extracts chapter number and title from a given chapter title string.
async def extract_chapter_info(title: str) -> Tuple[str, str]:
    match = re.match(r"(\d+(\.\d+)?[A-Za-z]*)\s*-\s*(.*)", title)
    if match:
        chapter_number = re.sub(r"[A-Z]", "", match.group(1))
        chapter_title = match.group(3) if match.group(3) else "N/A"
    else:
        chapter_number = title.strip()
        chapter_title = "N/A"
    return chapter_number, chapter_title


"""end manga"""


# Extracts chapter details from the chapter page
async def chapter(url: str) -> Chapter:
    soup = await pyparse(url=url)

    # Extract image URLs from the page-break divs
    img_tag = soup.select(".page-break img.wp-manga-chapter-img")
    image_urls = [img["src"].strip() for img in img_tag]

    # Get chapter title
    active_li = soup.find("li", class_="active")
    title = active_li.text.strip() if active_li else None

    # Extract next and previous chapter navigation links
    nav_links = soup.find("div", class_="nav-links")
    next_navigation = await create_navigation_link(nav_links, "btn next_page")
    prev_navigation = await create_navigation_link(nav_links, "btn prev_page")

    return Chapter(
        source=source,
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )


#  --Helper functions--
# Creates a navigation link by getting the chapter link and chapter number.
async def create_navigation_link(
    nav_links: BeautifulSoup, class_name: str
) -> NavigationLink:
    chapter_link = await get_chapter_link(nav_links, class_name)
    chapter_num = await get_num(chapter_link)
    navigation = NavigationLink(chapterPath=chapter_num, chapterUrl=chapter_link)
    return navigation


# Retrieves the chapter link.
async def get_chapter_link(nav_links: BeautifulSoup, class_name: str) -> Optional[str]:
    try:
        link_tag = nav_links.find("a", class_=class_name)
        return link_tag["href"] if link_tag else None
    except (TypeError, KeyError, AttributeError):
        return None


# Extracts the numeric part from a URL.
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


"""end chapter"""


# Searches for manga based on a keyword.
async def search(keyword: str) -> Search:
    url = "https://3asq.org/wp-admin/admin-ajax.php"
    data = {
        "action": "wp-manga-search-manga",
        "title": keyword,
    }

    # Send POST request to search for manga
    response = await pyparse(url=url, max_retries=2, method="POST", data=data)

    if response.get("success", False):
        result = response.get("data", [])
        if result:
            data = []
            for manga in result:
                # Create SearchDetails object
                search_details = SearchDetails(
                    name=manga.get("title"),
                    link=manga.get("url"),
                    type=manga.get("type"),
                )
                data.append(search_details)

            return Search(source=source, results=data)
    else:
        error_data = response.get("data", [{}])[0]
        error_type = error_data.get("error", "Failed to retrieve data")
        if error_type == "not found":
            raise await notfound(source)
        else:
            raise await Failed_retrieve(source)


"""end search"""
