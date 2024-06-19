
from bs4 import BeautifulSoup
import re
import logging

def home3asq(soup):
    mangaItems = soup.find_all('div', class_='page-item-detail manga')
    
    mangaData = []
    for mangaItem in mangaItems:
        mangaDiv = mangaItem.find('div', class_='item-thumb hover-details c-image-hover')
        
        translationTeamTag = mangaItem.find('span', class_='manga-title-badges')
        translationTeam = translationTeamTag.text.strip() if translationTeamTag else None
        
        mangaName = mangaDiv.find('a')['title']
        mangaLink = mangaDiv.find('a')['href']

        imgTags = mangaDiv.find('img')['srcset']
        mangaCover = [entry.split(" ")[0] for entry in imgTags.split(", ")][-1]
        
        chapters = mangaItem.find_all('div', class_='chapter-item')
        
        if len(chapters) > 0:
            latestChapter = chapters[0]
            latestChapterUrl = latestChapter.find('a')['href']
            latestChapterText = latestChapter.find('a').text.strip()
            latestChapterNumber = extractChapterNumber(latestChapterText)
        else:
            latestChapterNumber = None
            latestChapterUrl = None
        
        if len(chapters) > 1:
            penultimateChapter = chapters[1]
            penultimateChapterUrl = penultimateChapter.find('a')['href']
            penultimateChapterText = penultimateChapter.find('a').text.strip()
            penultimateChapterNumber = extractChapterNumber(penultimateChapterText)
        else:
            penultimateChapterNumber = None
            penultimateChapterUrl = None
            
        chaptersInfo = {
            "latestChapterNumber": latestChapterNumber,
            "penultimateChapterNumber": penultimateChapterNumber,
            "latestChapterUrl": latestChapterUrl,
            "penultimateChapterUrl": penultimateChapterUrl
        }
        
        mangaData.append({
            "mangaName": mangaName,
            "mangaLink": mangaLink,
            "mangaCover": mangaCover,
            "translationTeam": translationTeam,
            "chaptersInfo": chaptersInfo
        })
        
    nextPageUrl = extractNextPageUrl(soup)
    
    return {
            "mangaData": mangaData,
            "nextPageUrl": nextPageUrl
        }

def extractNextPageUrl(soup):
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
        chapterNumber = match.group(1)
        chapterTitle = match.group(3)
    else:
        chapterNumber = title.strip()
        chapterTitle = None
    
    return chapterNumber, chapterTitle

def manga3asq(soup):
    mangaName = soup.find("div", class_="post-title").find("h1").text.strip()
    reviewText = soup.find('div', class_='manga-excerpt')
    if reviewText:
        reviewText = reviewText.p.get_text(strip=True)
    else:
        reviewText = None
        
    genres = [a.get_text(strip=True) for a in soup.find('div', class_='genres-content').find_all('a')]
    coverManga = soup.find('div', class_='summary_image').find('img')['src']
    
    infoManga = {
        "mangaName": mangaName,
        "coverManga": coverManga,
        "genres": genres,
        "reviewText": reviewText,
        "totalChapters": None
    }

    chapters = []
    ul = soup.select_one('body > div.wrap > div > div.site-content > div > div.c-page-content.style-1 > div > div > div > div.main-col.col-md-8.col-sm-8 > div > div.c-page > div > div.page-content-listing.single-page > div > ul')
    for li in ul.find_all('li', class_='wp-manga-chapter'):
        aTag = li.find('a')
        chapterUrl = aTag['href']
        date = li.find("span", class_="chapter-release-date").get_text(strip=True)
        
        chapterTitleText = aTag.text.strip()
        chapterNumber, chapterTitle = extractChapterInfo(chapterTitleText)
        
        chapters.append({
            "number": chapterNumber,
            "title": chapterTitle,
            "url": chapterUrl,
            "date": date
        })
        
    return {
        "infoManga": infoManga,
        "chapters": chapters,
        "nextPageLink": None 
    }

# =========================
def chapter3asq(soup, url):
    imageUrls = []
    for imgTag in soup.select('.page-break img.wp-manga-chapter-img'):
        imageUrl = imgTag['src'].strip()
        imageUrls.append(imageUrl)
        
    if not imageUrls:
        logging.error("No images found in the chapter.")
        
    activeLi = soup.find('li', class_='active')
    if activeLi:
        fullTitle = activeLi.text.strip()
    else:
        fullTitle = None 
        logging.error("Active chapter title not found.")
        
    navLinks = soup.find('div', class_='nav-links')
    if navLinks:
        try:
            prevLinkTag = soup.find('a', class_="btn prev_page")
            prevChapterLink = prevLinkTag['href'] if prevLinkTag else None
            if prevChapterLink is None:
                logging.info("Previous chapter link not found.")
        except (TypeError, KeyError):
            prevChapterLink = None
            logging.error("Error extracting previous chapter link.")
        
        try:
            nextLinkTag = soup.find('a', class_='btn next_page')
            nextChapterLink = nextLinkTag['href'] if nextLinkTag else None
            if nextChapterLink is None:
                logging.info("Next chapter link not found.")
        except (TypeError, KeyError):
            nextChapterLink = None
            logging.error("Error extracting next chapter link.")
    else:
        prevChapterLink = None
        nextChapterLink = None
        logging.error("Navigation links container not found.")
        
    infoChapter = {
        "title": fullTitle,
        "imageUrls": imageUrls,
        "nextChapterLink": nextChapterLink,
        "prevChapterLink": prevChapterLink
    }
    return infoChapter
