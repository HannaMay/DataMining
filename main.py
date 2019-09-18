from urllib.parse import urlsplit, urljoin

import requests
from bs4 import BeautifulSoup


URLS = set()


def get_page(url):
    return requests.get(url).content


def get_soup(page):
    return BeautifulSoup(page, 'lxml')


def get_urls(soup):
    return [url['href'] for url in soup.find_all(href=True)]


def get_urls_with_base(base, current_url, urls):
    full_urls = [urljoin(current_url, relative_url) for relative_url in urls]
    return [url for url in full_urls if base in url]


def parse(url, depth, base):
    print(url)
    URLS.add(url)
    page = get_page(url)
    soup = get_soup(page)
    urls = get_urls(soup)
    if depth:
        target_urls = get_urls_with_base(base, url, urls)
        for url in target_urls:
            if url not in URLS:
                parse(url, depth-1, base)


def main():
    url = ('https://google.com')
    base = urlsplit(url).hostname
    parse(url, depth=2, base=base)


if __name__ == '__main__':
    main()
