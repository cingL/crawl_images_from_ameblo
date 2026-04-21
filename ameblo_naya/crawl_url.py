import codecs
import datetime
import json
import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import param


REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def get_run_timestamp():
    return os.getenv('CRAWL_RUN_TS') or datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def get_link_file_path():
    file_name = os.path.basename(param.blog_link_txt_name)
    file_stem, file_ext = os.path.splitext(file_name)
    if not file_ext:
        file_ext = '.txt'
    timestamped_name = '{0}_{1}{2}'.format(file_stem, get_run_timestamp(), file_ext)
    return os.path.join(os.path.dirname(__file__), timestamped_name)


def download_page(url):
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def extract_init_data(html):
    marker = 'window.INIT_DATA='
    marker_index = html.find(marker)
    if marker_index < 0:
        return {}

    start = html.find('{', marker_index)
    if start < 0:
        return {}

    depth = 0
    for index in range(start, len(html)):
        if html[index] == '{':
            depth += 1
        elif html[index] == '}':
            depth -= 1
            if depth == 0:
                return json.loads(html[start:index + 1])
    return {}


def parse_html(html):
    blog_list_urls = []

    # get url and title
    soup = BeautifulSoup(html, 'html.parser')
    blog_list_soup = soup.find('ul', attrs={'class': 'seachResult'})
    for blog_li in blog_list_soup.find_all('li'):
        update_array = re.split('\D', blog_li.find('span', attrs={'class': 'updateTime'}).getText())
        update_time = datetime.date(int(update_array[1]), int(update_array[2]), int(update_array[3]))
        if update_time > param.latest_date:
            a = blog_li.find('a', attrs={'class': 'areaClick'})
            link = a['href']
            title = a.find('h3').getText()
            blog_list_urls.append(link + "," + title + " ," + update_time.__str__())
        else:
            return blog_list_urls, None

    # get next page
    next_page = soup.find('div', attrs={'class': 'cmnPaging'}).find('a', attrs={'class': 'fwd'})
    if next_page:
        return blog_list_urls, 'https:' + next_page['href']
    return blog_list_urls, None


def get_time(time):
    date = []
    time_array = re.split('\D', time)
    for i in time_array:
        if i.isdigit():
            date.append(i)
        if date.__len__() == 3:
            return datetime.date(int(date[0]), int(date[1]), int(date[2]))


def parse_html_from_list(html):
    """
    記事一覧
   """
    list_urls = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', attrs={'class': 'skin-borderQuiet'})
    init_data = extract_init_data(html)
    entry_map = init_data.get('entryState', {}).get('entryMap', {})
    for item in items:
        link_node = item.find('h2').find('a')
        if link_node is None:
            continue
        title = link_node.getText().strip()
        entry_href = link_node.get('href', '').strip()
        entry_id_match = re.search(r'entry-(\d+)\.html', entry_href)
        if not entry_id_match:
            continue

        entry_id = entry_id_match.group(1)
        entry_info = entry_map.get(entry_id) or entry_map.get(int(entry_id), {})
        entry_created_datetime = entry_info.get('entry_created_datetime', '')
        item_time = datetime.date.fromisoformat(entry_created_datetime[:10]) if entry_created_datetime else None

        if item_time is None:
            continue

        if item_time > param.latest_date:
            link = urljoin(param.site_prefix, entry_href)
            list_urls.append(link + ',' + title + ',' + item_time.__str__())
        else:
            return list_urls, None

    next_page = soup.find('a', attrs={'data-uranus-component': 'paginationNext'}) or \
        soup.find('a', attrs={'class': 'js-paginationNext'})
    if next_page:
        return list_urls, urljoin(param.site_prefix, next_page['href'])
    return list_urls, None


if __name__ == '__main__':
    current_url = param.URL
    visited_urls = set()
    link_file_path = get_link_file_path()
    print('link file = ' + link_file_path)
    with codecs.open(link_file_path, 'wb', encoding='utf-8') as fp:
        while current_url:
            if current_url in visited_urls:
                break
            visited_urls.add(current_url)
            current_html = download_page(current_url)
            # urls, current_url = parse_html(current_html)
            urls, current_url = parse_html_from_list(current_html)
            fp.write('{urls}\n'.format(urls='\n'.join(urls)))
            # print('{urls}\n'.format(urls='\n'.join(urls)))
