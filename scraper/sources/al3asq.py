
from bs4 import BeautifulSoup
import re
import logging
from Hikoky.models import MangaFusion
from Hikoky.models import MangaFusion, Home,Manga, Chapter, MangaDetails, LatestChapters, MangaDetails,MangaInfo, ChapterDetails

def home3asq(soup : BeautifulSoup) -> Home:
    mangaItems = soup.find_all('div', class_='page-item-detail manga')
    
    data_mangas = []
    for mangaItem in mangaItems:
        mangaDiv = mangaItem.find('div', class_='item-thumb hover-details c-image-hover')
        
        translationTeamTag = mangaItem.find('span', class_='manga-title-badges')
        team = translationTeamTag.text.strip() if translationTeamTag else None
        
        name = mangaDiv.find('a')['title']
        link = mangaDiv.find('a')['href']

        imgTags = mangaDiv.find('img')['srcset']
        cover = [entry.split(" ")[0] for entry in imgTags.split(", ")][-1]
        
        chapters = mangaItem.find_all('div', class_='chapter-item')
        
        if len(chapters) > 0:
            latestChapter = chapters[0]
            latest_url = latestChapter.find('a')['href']
            latestChapterText = latestChapter.find('a').text.strip()
            latest_num = extractChapterNumber(latestChapterText)
        else:
            latest_num = None
            latest_url = None
        
        if len(chapters) > 1:
            penultimateChapter = chapters[1]
            penultimate_url = penultimateChapter.find('a')['href']
            penultimateChapterText = penultimateChapter.find('a').text.strip()
            penultimate_num = extractChapterNumber(penultimateChapterText)
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

def extract_next_page_url(soup):
    divTag = soup.find('div', class_='nav-previous float-left')
    aTag = divTag.find('a') if divTag else None
    return aTag['href'] if aTag else None

def extractChapterNumber(text):
    match = re.match(r'^\D*(\d+)', text)
    return match.group(1) if match else text

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
    image_urls = []
    for imgTag in soup.select('.page-break img.wp-manga-chapter-img'):
        imageUrl = imgTag['src'].strip()
        image_urls.append(imageUrl)
        
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
            if prev_chapter_link is None:
                logging.info("Previous chapter link not found.")
        except (TypeError, KeyError):
            prev_chapter_link = None
            logging.info("Previous chapter link not found.")
        try:
            nextLinkTag = soup.find('a', class_='btn next_page')
            next_chapter_link = nextLinkTag['href'] if nextLinkTag else None
            if next_chapter_link is None:
                logging.info("Next chapter link not found.")
        except (TypeError, KeyError):
            next_chapter_link = None
            logging.info("Next chapter link not found.")
            
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
    