import re
import mimetypes
import operator
from collections import defaultdict
from urllib.parse import urlsplit, urljoin

import requests
from requests import ConnectionError
from tabulate import tabulate
import pandas as pd
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup, Tag, Comment

URLS = set()

EXCLUDE_EXTENSIONS = (
    '.doc', '.docx', '.xls', '.xlsx', '.ppt',
    '.pptx', '.zip', '.rar', '.svg', '.css',
    '.js', '.png', '.jpg', '.pdf', '.jpeg',
    '.bmp', '.gif', '.psd', '.exe', '.otf',
    '.ttf', '.ico', '.torrent'
)

DATA = []


def get_page(url):
    try:
        response = requests.get(url)
    except ConnectionError:
        return None

    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)

    if extension in EXCLUDE_EXTENSIONS:
        return None
    return response.content


def get_soup(page):
    return BeautifulSoup(page, 'lxml')


def get_urls(soup):
    return [url['href'] for url in soup.find('body').find_all(href=True)]


def get_images(soup):
    return soup.find_all('img', width=True, height=True)


def get_headers(soup):
    return soup.find_all(re.compile('^h[1-6]$'))


def get_urls_with_base(base, current_url, urls):
    full_urls = [urljoin(current_url, relative_url) for relative_url in urls]
    return [url for url in full_urls if base in url]


def get_full_statistics():
    data = {}

    data['urls'] = sum([item['urls'] for item in DATA])
    data['total_images_size'] = sum([item['total_images_size'] for item in DATA])
    data['average_images_size'] = sum([item['average_images_size'] for item in DATA]) / len(DATA)
    data['images'] = sum([item['images'] for item in DATA])
    data['headers'] = sum([item['headers'] for item in DATA])
    data['symbols_count'] = sum([item['symbols_count'] for item in DATA])
    data['words_count'] = sum([item['words_count'] for item in DATA])

    return data


def show_data(data, source='Full:'):
    print(source)
    print(tabulate(pd.DataFrame(data, index=[0]), headers='keys', tablefmt='psql'))
    print()


def get_text(soup):
    exclude_tags = ('[document]', 'noscript', 'input', 'script', 'style')

    texts = []

    body_text = soup.find('body').contents[0]
    if not isinstance(body_text, Tag):
        if body_text and body_text.strip():
            texts.append(body_text)

    for text in soup.find('body').find_all(text=True):
        if text.parent.name not in exclude_tags and text.strip():
            if not isinstance(text, Comment):
                texts.append(text.strip())

    return texts


def get_count_symbols(texts):
    return sum([len(text) for text in texts])


def get_words_list(texts):
    words = []
    for text in texts:
        words.extend([word.lower() for word in re.findall(r'[a-zA-zа-яА-Я]+', text) if word.strip()])

    return words


def get_words_frequency(words):
    frequency = defaultdict(int)
    for word in words:
        frequency[word] += 1
    return frequency


def get_words_length_frequency(words):
    frequency = defaultdict(int)
    for word in words:
        frequency[len(word)] += 1
    return frequency


def make_histogram(url, frequency):
    frequency = sorted(frequency.items(), key=operator.itemgetter(1))[-100:]
    keys = [str(item[0]) for item in frequency]
    values = [item[1] for item in frequency]
    if len(keys) > 35:
        plt.figure(figsize=(0.17 * len(keys), 4.8))
    plt.title(label=url)
    plt.xticks(rotation=-90)
    plt.bar(keys, values, color='darkgreen', alpha=0.85)
    plt.show()


def get_statistics(url, soup, urls):
    statistics = {'urls': len(urls)}
    imgs = get_images(soup)
    img_sizes = [int(img['width']) * int(img['height'])
                 for img in imgs if img['width'].isdigit() and img['height'].isdigit()]
    statistics['total_images_size'] = sum(img_sizes)
    statistics['average_images_size'] = sum(img_sizes) / len(img_sizes) if img_sizes else 0
    statistics['images'] = len(imgs)
    statistics['headers'] = len(get_headers(soup))
    texts = get_text(soup)

    symbols_count = get_count_symbols(texts)
    statistics['symbols_count'] = symbols_count

    words = get_words_list(texts)
    statistics['words_count'] = len(words)

    words_frequency = get_words_frequency(words)
    make_histogram(url, words_frequency)

    words_length_frequency = get_words_length_frequency(words)
    make_histogram(url, words_length_frequency)
    return statistics


def parse(url, depth, base):
    URLS.add(url)

    page = get_page(url)
    if not page:
        return None

    soup = get_soup(page)
    if not soup.contents:
        return None
    urls = get_urls(soup)
    statistics = get_statistics(url, soup, urls)
    show_data(statistics, url)
    DATA.append(statistics)
    if depth:
        target_urls = get_urls_with_base(base, url, urls)
        for url in target_urls:
            if url not in URLS:
                parse(url, depth - 1, base)


def main():
    url = ('https://google.com')
    base = urlsplit(url).hostname
    parse(url, depth=1, base=base)
    show_data(get_full_statistics())


if __name__ == '__main__':
    main()
