import re
import operator
from collections import defaultdict
from urllib.parse import urlsplit, urljoin

import requests
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup, Tag

URLS = set()

DATA = []


def get_page(url):
    return requests.get(url).content


def get_soup(page):
    return BeautifulSoup(page, 'lxml')


def get_urls(soup):
    return [url['href'] for url in soup.find_all(href=True)]


def get_images(soup):
    return soup.find_all('img', width=True, height=True)


def get_urls_with_base(base, current_url, urls):
    full_urls = [urljoin(current_url, relative_url) for relative_url in urls]
    return [url for url in full_urls if base in url]


def get_text(soup):
    exclude_tags = ('[document]', 'noscript', 'input', 'script', 'style')

    texts = []

    body_text = soup.find('body').contents[0]
    if not isinstance(body_text, Tag):
        if body_text and body_text.strip():
            texts.append(body_text)

    for text in soup.find('body').find_all(text=True):
        if text.parent.name not in exclude_tags and text.strip():
            texts.append(text.strip())

    return texts


def get_count_symbols(texts):
    return sum([len(text) for text in texts])


def get_words_list(texts):
    words = []
    for text in texts:
        words.extend([word for word in re.split(r'!|"|\'|:|;|\?|,|\.|\n|\t| |-|\(|\)|\|', text) if word.strip()])

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


def make_histogram(frequency):
    frequency = sorted(frequency.items(), key=operator.itemgetter(1))
    keys = [item[0] for item in frequency]
    values = [item[1] for item in frequency]
    plt.xticks(rotation=-90)
    plt.bar(keys, values, color='darkgreen', alpha=0.85)
    plt.show()


def get_statistics(soup, urls):
    statistics = {'urls': len(urls)}
    imgs = get_images(soup)
    img_sizes = [int(img['width']) * int(img['height']) for img in imgs]
    statistics['total_images_size'] = sum(img_sizes)
    statistics['average_images_size'] = sum(img_sizes) / len(img_sizes) if img_sizes else 0
    statistics['images'] = len(imgs)

    texts = get_text(soup)

    symbols_count = get_count_symbols(texts)
    statistics['symbols_count'] = symbols_count

    words = get_words_list(texts)
    statistics['words_count'] = len(words)

    words_frequency = get_words_frequency(words)
    make_histogram(words_frequency)

    words_length_frequency = get_words_length_frequency(words)
    make_histogram(words_length_frequency)
    return statistics


def parse(url, depth, base):
    URLS.add(url)
    page = get_page(url)
    soup = get_soup(page)
    urls = get_urls(soup)
    statistics = get_statistics(soup, urls)
    DATA.append(statistics)
    print(statistics)

    if depth:
        target_urls = get_urls_with_base(base, url, urls)
        for url in target_urls:
            if url not in URLS:
                parse(url, depth - 1, base)


def main():
    url = ('https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0')
    base = urlsplit(url).hostname
    parse(url, depth=1, base=base)


if __name__ == '__main__':
    main()
