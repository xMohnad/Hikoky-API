from bs4 import BeautifulSoup
import logging
import re

from Hikoky.models import(
    Home, 
    Manga, 
    Chapter, 
    MangaDetails, 
    LatestChapters, 
    MangaDetails, 
    MangaInfo, 
    ChapterDetails
)

from typing import Optional

# 
def home_teamx(soup: BeautifulSoup) -> Home:
    boxes = soup.find_all("div", class_="box")
    
    data_mangas = []
    for box in boxes:
        img_div = box.find("div", class_="imgu")
        name = img_div.find("img")["alt"]
        link = img_div.find("a")["href"]
        cover = img_div.find("img")["src"]
        
        info_div = box.find("div", class_="info")
        chapter_list = info_div.find_all("a")
        
        latest_num = extract_chapter_number(chapter_list, 1)
        latest_url = f"{link}/{latest_num}" if latest_num else None
        
        penultimate_num = extract_chapter_number(chapter_list, 2)
        penultimate_url = f"{link}/{penultimate_num}" if penultimate_num else None

        chapters = LatestChapters(
            latestNum=latest_num, 
            penultimateNum=penultimate_num, 
            latestUrl=latest_url, 
            penultimateUrl=penultimate_url
        )
        manga_data = MangaDetails(
            name=name, 
            link=link, 
            cover=cover, 
            chapters=chapters,
            team=None
        )
        manga_data.saver(source="Team-X")
        data_mangas.append(manga_data)

    next_url = extract_next_page_url(soup)
    
    return Home(data_mangas, next_url)

def extract_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_page = soup.find("a", rel="next")
    return next_page["href"] if next_page else None

def extract_chapter_number(chapter_list, index: int) -> Optional[str]:
    if len(chapter_list) > index:
        return chapter_list[index].text.strip().split()[-1]
    return None
    
    
# 
def manga_teamx(soup: BeautifulSoup) -> Manga:
    container = soup.find('div', class_="container")
    
    cover_manga = container.find('img', class_="shadow-sm")['src']
    info_box = container.find_all("div", class_="whitebox")[1]
    manga_name = info_box.find('div', class_="author-info-title").find("h1").text.strip()
    
    genres = info_box.find('div', class_="review-author-info")
    genres = [a.get_text(strip=True) for a in genres.find_all('a', class_='subtitle')]
    
    about_story = info_box.find('div', class_='review-content').p.get_text(strip=True)
    chapter_text = container.find('a', class_='nav-link').text
    chapter_number = ''.join(filter(str.isdigit, chapter_text))

    info_manga = MangaInfo(
        name=manga_name,
        cover=cover_manga,
        genres=genres,
        aboutStory=about_story,
        totalChapters=chapter_number
    )

    chapters = []
    chapter_urls = container.find('div', class_="eplister").find('ul')
    for chapter_item in chapter_urls.find_all('li'):
        all_info = chapter_item.find('a')
        
        chapter_url = all_info['href']
        chapter_text = container.find('a', class_='nav-link').text
        
        chapter_number = all_info.find_all('div', class_="epl-num")[1].text.strip().split()[-1]
        chapter_title = all_info.find('div', class_="epl-title").get_text(strip=True)

        date = all_info.find('div', class_="epl-date").get_text(strip=True)
        
        chapters.append(ChapterDetails(
            number=chapter_number,
            link=chapter_url,
            title=chapter_title,
            date=date 
        ))
        
        
    next_page_link = get_next_page_url(container)
    
    return Manga(
        mangaList=info_manga,
        chapters=chapters,
        nextPageLink=next_page_link
    )

def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_page = soup.find("a", rel="next")
    return next_page["href"] if next_page else None


def getNextPageUrl(soup):
    nextLink = soup.find('a', rel='next')
    if nextLink and nextLink.has_attr('href'):
        return nextLink['href']
    return None

#
def getNum(url: str) -> Optional[str]:
    match = re.search(r'(?<=\/)\d+(\.\d+)?', url)
    return match.group() if match else None

def chapter_teamx(soup: BeautifulSoup, url: str) -> Chapter:
    readerArea = soup.find_all('div', class_="page-break")
    image_urls = [img.get("src") for div in readerArea for img in div.find_all("img") if img.get("src")]
    if not image_urls:
        logging.error("Images not found.")

    titleElement = soup.find("h1", id="chapter-heading")
    title = titleElement.text.strip() if titleElement else None
    chapterNumber = getNum(url)
    title = f"{title} | الفصل {chapterNumber}" if title else f"الفصل {chapterNumber}"

    next_chapter_link, prev_chapter_link = extractChapterLinks(soup)

    return Chapter(
        title=title,
        imageUrls=image_urls,
        nextLink=next_chapter_link,
        prevLink=prev_chapter_link
    )

def extractChapterLinks(soup: BeautifulSoup) -> (Optional[str]):
    next_chapter_link = None
    prev_chapter_link = None
    container = soup.find('div', class_="container")
    if container:
        next_chapter_element = container.find('a', id='next-chapter')
        if next_chapter_element and next_chapter_element['href'] != "#":
            next_chapter_link = next_chapter_element['href']
        else:
            logging.info("Next chapter link is not available")

        prev_chapter_element = container.find('a', id='prev-chapter')
        if prev_chapter_element and prev_chapter_element['href'] != "#":
            prev_chapter_link = prev_chapter_element['href']
        else:
            logging.info("Previous chapter link is not available")
    
    return next_chapter_link, prev_chapter_link
