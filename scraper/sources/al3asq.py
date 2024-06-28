
from bs4 import BeautifulSoup
import re
import logging

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


def home3asq(soup : BeautifulSoup):

    items = soup.find_all("div", class_="page-item-detail")
    
    data_mangas = []
    for item in items:
        name_tag = item.find("h3", class_="h5")
        name = name_tag.find_all("a")[-1].text.strip()
        link = name_tag.find_all("a")[-1]["href"]

        img_tag = item.find("div", {"class": "item-thumb hover-details c-image-hover"}).a

        if img_tag:
            img_tags = img_tag.find('img')['srcset']
            cover = [entry.split(" ")[0] for entry in img_tags.split(", ")][-1]
        else:
            cover = None
        translation_team_tag = item.find('span', class_='manga-title-badges')
        team = translation_team_tag.text.strip() if translation_team_tag else None

        chapters = item.find_all('div', class_='chapter-item')

        if len(chapters) > 0:
            latest_chapter = chapters[0]
            latest_url = latest_chapter.find('a')['href']
            latest_chapter_text = latest_chapter.find('a').text.strip()
            latest_num = extract_chapter_number(latest_chapter_text)
        else:
            latest_num = None
            latest_url = None
        
        if len(chapters) > 1:
            penultimate_chapter = chapters[1]
            penultimate_url = penultimate_chapter.find('a')['href']
            penultimate_chapter_text = penultimate_chapter.find('a').text.strip()
            penultimate_num = extract_chapter_number(penultimate_chapter_text)
        else:
            penultimate_num = None
            penultimate_url = None

        
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
            team=team,
            chapters=chapters
        )

        manga_data.saver(source="3asq")
        data_mangas.append(manga_data)

    next_url = extract_next_page_url(soup)

    return Home(data_mangas, next_url)

def extract_chapter_number(text):
    match = re.match(r'^\D*(\d+)', text)
    return match.group(1) if match else text

def extract_next_page_url(soup):
    div_tag = soup.find('div', class_='nav-previous float-left')
    aTag = div_tag.find('a') if div_tag else None
    return aTag['href'] if aTag else None
# ======================
def extractChapterInfo(title):
    match = re.match(r'(\d+(\.\d+)?)\s*-\s*(.*)', title)
    if match:
        chapter_number = match.group(1)
        chapter_title = match.group(3)
    else:
        chapter_number = title.strip()
        chapter_title = None
    
    return chapter_number, chapter_title

def manga3asq(soup: BeautifulSoup) -> Manga:
    name = soup.find("div", class_="post-title").find("h1").text.strip()
    about_story = soup.find('div', class_='manga-excerpt')
    if about_story:
        about_story = about_story.p.get_text(strip=True)
    else:
        about_story = None
        
    genres = [a.get_text(strip=True) for a in soup.find('div', class_='genres-content').find_all('a')]
    cover_manga = soup.find('div', class_='summary_image').find('img')['src']
    
    info_manga = MangaInfo(
            name=name,
            cover=cover_manga,
            genres=genres,
            aboutStory=about_story,
        )
        
    chapters = []
    ul = soup.select_one('body > div.wrap > div > div.site-content > div > div.c-page-content.style-1 > div > div > div > div.main-col.col-md-8.col-sm-8 > div > div.c-page > div > div.page-content-listing.single-page > div > ul')
    for li in ul.find_all('li', class_='wp-manga-chapter'):
        aTag = li.find('a')
        chapter_url = aTag['href']
        date = li.find("span", class_="chapter-release-date").get_text(strip=True)
        
        chapterTitleText = aTag.text.strip()
        chapter_number, chapter_title = extractChapterInfo(chapterTitleText)
        
        chapters.append(ChapterDetails(
            number=chapter_number,
            link=chapter_url,
            title=chapter_title,
            date=date 
        ))
        
    return Manga(
        mangaList=info_manga,
        chapters=chapters,
    )


# =========================
def chapter3asq(soup: BeautifulSoup, url: str) -> Chapter:
    img_tag = soup.select('.page-break img.wp-manga-chapter-img')
    image_urls = [img['src'].strip() for img in img_tag] 

    if not image_urls:
        logging.error("No images found in the chapter.")

    activeLi = soup.find('li', class_='active')
    if activeLi:
        title = activeLi.text.strip()
    else:
        title = None 
        logging.error("Active chapter title not found.")

    navLinks = soup.find('div', class_='nav-links')

    if navLinks:
        try:
            prevLinkTag = soup.find('a', class_="btn prev_page")
            prev_chapter_link = prevLinkTag['href'] if prevLinkTag else None

        except (TypeError, KeyError):
            prev_chapter_link = None

        try:
            nextLinkTag = soup.find('a', class_='btn next_page')
            next_chapter_link = nextLinkTag['href'] if nextLinkTag else None

        except (TypeError, KeyError):
            next_chapter_link = None

    else:
        prev_chapter_link = None
        next_chapter_link = None
        logging.error("Navigation links container not found.")

    return Chapter(
        title=title,
        imageUrls=image_urls,
        nextLink=next_chapter_link,
        prevLink=prev_chapter_link
    )
