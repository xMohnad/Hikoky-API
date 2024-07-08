from bs4 import BeautifulSoup
import re
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


def home3asq(soup: BeautifulSoup, source: str):
    items = soup.find_all("div", class_="page-item-detail")
    data_mangas = []

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
            chapter_num = extract_chapter_number(chapter_text)

            latest_chapters = LatestChapters(num=chapter_num, url=chapter_url)
            latest_chapters.saver(source, name)
            chapters.append(latest_chapters)

        manga_data = MangaDetails(
            name=name, link=link, cover=cover, team=team, latestChapters=chapters
        )
        manga_data.saver(source)
        data_mangas.append(manga_data)

    next_url = extract_next_page_url(soup)
    return Home(mangaData=data_mangas, nextUrl=next_url)


def extract_chapter_number(text):
    match = re.match(r"^\D*(\d+)", text)
    return match.group(1) if match else text


def extract_next_page_url(soup):
    div_tag = soup.find("div", class_="nav-previous float-left")
    aTag = div_tag.find("a") if div_tag else None
    return aTag["href"] if aTag else None


# ===============================================================================================
def extract_chapter_info(title):
    match = re.match(r"(\d+(\.\d+)?[A-Za-z]*)\s*-\s*(.*)", title)
    if match:
        chapter_number = re.sub(r"[A-Z]", "", match.group(1))
        chapter_title = match.group(3) if match.group(3) else "N/A"
    else:
        chapter_number = title.strip()
        chapter_title = "N/A"

    return chapter_number, chapter_title


def manga3asq(
    soup: BeautifulSoup, source: str, manga_path: str = None, v1=False
) -> Manga:
    name = soup.find("div", class_="post-title").find("h1").text.strip()
    about_story = soup.find("div", class_="manga-excerpt")
    if about_story:
        about_story = about_story.p.get_text(strip=True)
    else:
        about_story = "N/A"

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
        "body > div.wrap > div > div.site-content > div > div.c-page-content.style-1 > div > div > div > div.main-col.col-md-8.col-sm-8 > div > div.c-page > div > div.page-content-listing.single-page > div > ul"
    )
    for li in ul.find_all("li", class_="wp-manga-chapter"):
        aTag = li.find("a")
        chapter_url = aTag["href"]
        date = li.find("span", class_="chapter-release-date").get_text(strip=True)

        chapterTitleText = aTag.text.strip()
        chapter_number, chapter_title = extract_chapter_info(chapterTitleText)
        chapter_details = ChapterDetails(
            number=chapter_number,
            link=chapter_url,
            title=chapter_title if chapter_title else "N/A",
            date=date,
        )

        if not v1:
            chapter_details.saver(source, manga_path)

        chapters.append(chapter_details)

    return Manga(
        mangaList=info_manga,
        chapters=chapters,
    )


# ====================================================================================


def get_num(url: str) -> Optional[str]:
    if url:
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            match = re.search(r"\d+", part)
            if match:
                return match.group(0)
            else:
                return parts[-1]
    return None


def chapter3asq(
    soup: BeautifulSoup, url: str, source: str, manga_path=None, v1=False
) -> Chapter:
    img_tag = soup.select(".page-break img.wp-manga-chapter-img")
    image_urls = [img["src"].strip() for img in img_tag]

    if not image_urls:
        logging.error("No images found in the chapter.")

    activeLi = soup.find("li", class_="active")
    if activeLi:
        title = activeLi.text.strip()
    else:
        title = None
        logging.error("Active chapter title not found.")

    def get_chapter_link(nav_links: BeautifulSoup, class_name: str) -> Optional[str]:
        try:
            link_tag = nav_links.find("a", class_=class_name)
            return link_tag["href"] if link_tag else None
        except (TypeError, KeyError, AttributeError):
            return None

    nav_links = soup.find("div", class_="nav-links")

    next_chapter_link = get_chapter_link(nav_links, "btn next_page")
    prev_chapter_link = get_chapter_link(nav_links, "btn prev_page")

    if next_chapter_link:
        next_navigation = NavigationLink(chapterUrl=next_chapter_link)
        next_num = get_num(next_chapter_link)
        if not v1:
            next_navigation.saver(source=source, manga_path=manga_path, number=next_num)
    else:
        next_navigation = None

    if prev_chapter_link:
        prev_navigation = NavigationLink(chapterUrl=prev_chapter_link)
        prev_num = get_num(prev_chapter_link)
        if not v1:
            prev_navigation.saver(source=source, manga_path=manga_path, number=prev_num)
    else:
        prev_navigation = None

    return Chapter(
        title=title,
        imageUrls=image_urls,
        nextNavigation=next_navigation,
        prevNavigation=prev_navigation,
    )
