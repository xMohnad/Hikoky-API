from bs4 import BeautifulSoup
import logging

async def search3asq(response, source):
    if response.get('success', False):
        result = response.get("data", [])
        if result:
            data = []
            for manga in result:
                title = manga.get('title')
                link = manga.get('url')
                type_ = manga.get('type')
                type_ = manga.get('type')
                data.append({'title': title, 'link': link, 'cover': None, 'type': type_, 'badge': None})
            return {'success': True, "source": source, 'data': data}
        else:
            return {'success': False, "source": source, 'error': 'not found', "message": 'لا توجد مانجا'}
    else:
        error_data = response.get('data', [{}])[0]
        error_type = error_data.get('error', 'Failed to retrieve data')
        if error_type == 'not found':
            return {'success': False, "source": source, 'error': 'not found', "message": 'لا توجد مانجا'}
        else:
            logging.error(f"Failed to retrieve data in: {source}")
            return {'success': False, 'error': 'Failed to retrieve data'}

async def search_teamx(response, source):
    if response:
        list_group = response.find('ol', class_='list-group')
        if list_group and list_group.find_all():
            results = response.find_all('li', class_='list-group-item')
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
        logging.error(f"Failed to retrieve data in: {source}")
        return {'success': False, 'error': 'Failed to retrieve data'}    



 