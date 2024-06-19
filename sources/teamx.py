from bs4 import BeautifulSoup
import re
import logging

def homeTeamX(soup):
    boxes = soup.find_all("div", class_="box")
    
    mangaData = []
    for box in boxes:
        imgDiv = box.find("div", class_="imgu")
        mangaName = imgDiv.find("img")["alt"]
        mangaLink = imgDiv.find("a")["href"]
        mangaCover = imgDiv.find("img")["src"]
        
        infoDiv = box.find("div", class_="info")
        chapterList = infoDiv.find_all("a")
        
        latestChapterNumber = extractChapterNumber(chapterList, 1)
        latestChapterUrl = f"{mangaLink}/{latestChapterNumber}"
        
        penultimateChapterNumber = extractChapterNumber(chapterList, 2)
        penultimateChapterUrl = f"{mangaLink}/{penultimateChapterNumber}"

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
            "translationTeam": None,
            "chaptersInfo": chaptersInfo
        })

    nextPageUrl = extractNextPageUrl(soup)
    
    return {
        "mangaData": mangaData,
        "nextPageUrl": nextPageUrl
    }

def extractNextPageUrl(soup):
    nextPage = soup.find("a", rel="next")
    return nextPage["href"] if nextPage else None

def extractChapterNumber(chapterList, index):
    if len(chapterList) > index:
        return chapterList[index].text.strip().split()[-1]
    return None
    
# =========================
def mangaTeamX(soup):
    soup = soup.find('div', class_="container")
    
    coverManga = soup.find('img', class_="shadow-sm")['src']
    infoBox = soup.find_all("div", class_="whitebox")[1]
    mangaName = infoBox.find('div', class_="author-info-title").find("h1").text.strip()
    
    genres = infoBox.find('div', class_="review-author-info")
    genres = [a.get_text(strip=True) for a in genres.find_all('a', class_='subtitle')]
    
    reviewText = infoBox.find('div', class_='review-content').p.get_text(strip=True)
    chapterText = soup.find('a', class_='nav-link').text
    chapterNumber = ''.join(filter(str.isdigit, chapterText))
    
    infoManga = {
        "mangaName": mangaName,
        "coverManga": coverManga,
        "genres": genres,
        "reviewText": reviewText,
        "totalChapters": chapterNumber
    }
    
    chapters = []
    chapterUrls = soup.find('div', class_="eplister").find('ul')
    for chapterItem in chapterUrls.find_all('li'):
        allInfo = chapterItem.find('a')
        
        chapterUrl = allInfo['href']
        chapterNumber = allInfo.find_all('div', class_="epl-num")[1]
        chapterNumber = chapterNumber.text.strip().split()[1]
        
        chapterTitle = allInfo.find('div', class_="epl-title").get_text(strip=True)
        date = allInfo.find('div', class_="epl-date").get_text(strip=True)
        
        chapters.append({
            "number": chapterNumber,
            "url": chapterUrl,
            "title": chapterTitle,
            "date": date 
        })
        
    nextPageLink = getNextPageUrl(soup)
    
    return {
        "infoManga": infoManga,
        "chapters": chapters,
        "nextPageLink": nextPageLink
    }
    
def getNextPageUrl(soup):
    nextLink = soup.find('a', rel='next')
    if nextLink and nextLink.has_attr('href'):
        return nextLink['href']
    return None

# ========================
def getNum(url):
    match = re.search(r'(?<=\/)\d+(\.\d+)?', url)
    return match.group() if match else None

def chapterTeamX(soup, url):
    readerArea = soup.find_all('div', class_="page-break")
    imageUrls = [img.get("src") for div in readerArea for img in div.find_all("img") if img.get("src")]
    if not imageUrls:
        logging.error("Images not found.")

    titleElement = soup.find("h1", id="chapter-heading")
    
    title = titleElement.text.strip() if titleElement else None
    chapterNumber = getNum(url)
    fullTitle = f"{title} | الفصل {chapterNumber}"

    nextChapterLink, prevChapterLink = extractChapterLinks(soup)

    infoChapter = {
        "title": fullTitle,
        "imageUrls": imageUrls,
        "nextChapterLink": nextChapterLink,
        "prevChapterLink": prevChapterLink
    }
    
    return infoChapter

def extractChapterLinks(soup):
    nextChapterLink = None
    prevChapterLink = None
    container = soup.find('div', class_="container")
    if container:
        nextChapterElement = container.find('a', id='next-chapter')
        if nextChapterElement and nextChapterElement['href'] != "#":
            nextChapterLink = getNum(nextChapterElement['href'])
        else:
            logging.info("Next chapter link is not available")

        prevChapterElement = container.find('a', id='prev-chapter')
        if prevChapterElement and prevChapterElement['href'] != "#":
            prevChapterLink = getNum(prevChapterElement['href'])
        else:
            logging.info("Previous chapter link is not available")
    
    return nextChapterLink, prevChapterLink
