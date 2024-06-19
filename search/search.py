import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
import time

def make_request(method, url, headers=None, params=None, data=None):
    """Send an HTTP request and return the response."""
    try:
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=params)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, data=data)
        else:
            raise ValueError("Invalid HTTP method specified.")
        
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None
        
def searchTeamX(keyword: str, source: str):
    url = "https://www.teamxnovel.com/ajax/search"
    headers = {
        'user-agent': UserAgent().random,
        'authority': 'www.teamxnovel.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8'
    }
    
    params = {'keyword': keyword}
    
    response = make_request('get', url, headers=headers, params=params, data=None)
    if response and response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        list_group = soup.find('ol', class_='list-group')
        if bool(list_group.find_all()):
            results = soup.find_all('li', class_='list-group-item')
            data = []

            for result in results:
                title = result.find('a', class_='fw-bold').text.strip()
                link = result.find('a', class_='fw-bold')['href']
                cover = result.find('img')['src'] if result.find('img') else None
                badge = result.find('span', class_='badge').text.strip() if result.find('span', 'badge') else None
                
                data.append({'title': title, 'link': link, 'cover': cover, 'type': None, 'badge': badge})
                
            return {'success': True, "source": source, 'data': data}
        else:
            return {'success': False, "source": source, 'error': 'not found', "message": 'لا توجد مانجا'}
    else:
        logging.error(f"Failed to retrieve data in: {url}")
        return {'success': False, 'error': 'Failed to retrieve data'}    

def search3asq(keyword: str, source: str):
    url = 'https://3asq.org/wp-admin/admin-ajax.php'
    
    headers = {
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
      "Sec-Ch-Ua-Mobile": "?1",
      "Sec-Ch-Ua-Platform": "\"Android\"",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "X-Requested-With": "XMLHttpRequest"
    }
    
    data = {"action": "wp-manga-search-manga", "title": keyword}

    response = make_request('post', url, headers=headers, params=None, data=data)

    if response and response.status_code == 200:
        response_data = response.json()
        result = response_data.get("success")
        if result:
            results = response_data.get('data', [])

            data = []
            for result in results:
                title = result.get('title')
                link = result.get('url')
                type_ = result.get('type')

                data.append({'title': title, 'link': link, 'cover': None, 'type': type_, 'badge': None})
            return {'success': True, "source": source, 'data': data}
        else:
            return {'success': False, "source": source, 'error': 'not found', "message": 'لا توجد مانجا'}
    else:
        logging.error(f"Failed to retrieve data in: {url}")
        return {'success': False, 'error': 'Failed to retrieve data'}
