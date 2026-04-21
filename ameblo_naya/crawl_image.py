import codecs
import datetime
import os
import re
import time
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

import param
from crawl_url import download_page, extract_init_data
# get all passage urls from blog_link.txt
from param import blog_link_txt_name

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def get_run_timestamp():
    return os.getenv('CRAWL_RUN_TS') or datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def get_link_file_path():
    file_name = os.path.basename(blog_link_txt_name)
    file_stem, file_ext = os.path.splitext(file_name)
    if not file_ext:
        file_ext = '.txt'
    timestamped_name = '{0}_{1}{2}'.format(file_stem, get_run_timestamp(), file_ext)
    return os.path.join(os.path.dirname(__file__), timestamped_name)


def get_result_dir_path():
    return os.path.join(os.path.dirname(__file__), 'result_{0}'.format(get_run_timestamp()))


def get_url():
    links = {}
    link_file_path = get_link_file_path()
    if not os.path.exists(link_file_path):
        raise FileNotFoundError('missing link file: ' + link_file_path)
    with codecs.open(link_file_path, 'rb', 'utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue

            # line format: url,title,date
            left_part, sep, date_part = line.rpartition(',')
            if not sep:
                continue

            try:
                item_time = datetime.date.fromisoformat(date_part.strip())
            except ValueError:
                continue

            # second guard: skip old entries even if link file contains them
            if item_time <= param.latest_date:
                continue

            url, sep2, title = left_part.partition(',')
            if not sep2:
                continue
            url = url.strip()
            title = title.strip()
            links[url] = title

    return links


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def to_high_quality_image_url(img_link):
    if not img_link:
        return None
    if img_link.startswith('//'):
        img_link = 'https:' + img_link
    if 'stat.ameba.jp/user_images/' not in img_link:
        return None

    # Ameblo often serves resized images via query params like ?caw=800.
    # Removing query/fragment keeps the original image path (higher quality).
    parsed = urlsplit(img_link)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))


def get_entry_date(html, url):
    init_data = extract_init_data(html)
    entry_map = init_data.get('entryState', {}).get('entryMap', {})
    entry_id_match = re.search(r'entry-(\d+)\.html', url)
    if not entry_id_match:
        return 'unknown_date'

    entry_id = entry_id_match.group(1)
    entry = entry_map.get(entry_id) or entry_map.get(int(entry_id), {})
    created_datetime = entry.get('entry_created_datetime', '')
    if created_datetime:
        return created_datetime[:10]
    return 'unknown_date'


def get_entry_images(soup):
    body = soup.find(id='entryBody') or soup.find('div', attrs={'data-uranus-component': 'entryBody'})
    if body is None:
        return []

    links = []
    seen = set()
    for img in body.find_all('img'):
        img_link = img.get('data-src') or img.get('src')
        high_quality_url = to_high_quality_image_url(img_link)
        if not high_quality_url:
            continue
        if high_quality_url in seen:
            continue
        seen.add(high_quality_url)
        links.append(high_quality_url)
    return links


def crawl(url, prefix, result_dir_path):
    html = download_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    # date is used as file name prefix instead of folder name
    entry_date = get_entry_date(html, url)
    print('time = ' + entry_date)

    image_links = get_entry_images(soup)
    if not image_links:
        print('no images in entryBody')
        return

    # named image with title and index
    safe_prefix = sanitize_filename(prefix)
    for index, img_link in enumerate(image_links, start=1):
        ext = os.path.splitext(urlsplit(img_link).path)[1] or '.jpg'
        file_name = '{0}_{1}-{2}{3}'.format(entry_date, safe_prefix, index, ext)
        img_path = os.path.join(result_dir_path, file_name)
        print('img_name = ' + img_path)
        print('img_link = ' + img_link)
        try:
            img_r = requests.get(img_link, stream=True, timeout=20, headers=REQUEST_HEADERS)
            if img_r.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in img_r.iter_content(1024):
                        f.write(chunk)
            else:
                print('download failed status=' + str(img_r.status_code))
        except requests.RequestException as ex:
            print('download failed error=' + str(ex))


if __name__ == '__main__':

    s_time = time.time()

    result_dir_path = get_result_dir_path()
    if not os.path.exists(result_dir_path):
        os.mkdir(result_dir_path)
    print('result dir = ' + result_dir_path)
    print('link file = ' + get_link_file_path())

    all_blog_link = get_url()
    for ame_link in all_blog_link:
        print(ame_link + ', ' + all_blog_link[ame_link])
        crawl(ame_link, all_blog_link[ame_link], result_dir_path)

    e_time = time.time()
    cost = e_time - s_time
    print('cost = ' + time.strftime('%M:%S', time.gmtime(cost)))
