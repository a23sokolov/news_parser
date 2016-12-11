import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
import log as Logger
from utils import appropriate_title
import time
from concurrent import futures

log = Logger.get_logger(__name__)
DEFAULT_PREFIX = 'https://ria.ru/'
DEFAULT_PREFIX_URL = 'https://ria.ru/world/more.html?date={datentime}&onedayonly=1'


def start_request(params, start_date, end_date):
    print('ria_parser start')
    start_time = time.time()
    start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y').replace(hour=23, minute=59)
    end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y').replace(hour=23, minute=59)
    exit_node = []
    with codecs.open("ria_news.txt", "w", "utf-8") as jsonfile:
        while (end_date - start_date).days >= -1:
            url = DEFAULT_PREFIX_URL.format(datentime=end_date.strftime('%Y%m%dT%H%M%S'))
            response = requests.get(url)
            bs = BeautifulSoup(response.content[response.content.index('\n'):], 'lxml')
            parsed_node, end_date = _parse_html(bs, params)
            exit_node += parsed_node
            print(end_date.strftime('%d-%m-%y %H:%M'))
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    print("ria_parser finished --- %s seconds ---" % (time.time() - start_time))


def _parse_html(beatifulSoup, params):
    appropriate_link = []
    try:
        start_res = beatifulSoup.find_all(attrs={"class": "b-list__item"})
        # can has only 2 active connections.
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            appropriate_link = list(executor.map(lambda p: _parse_article_body(p, params), start_res))
        appropriate_link = filter(lambda x: x, appropriate_link)
        splitted_time = start_res[len(start_res) - 1].find(attrs={"class": "b-list__item-time"}).span.text
        date = start_res[len(start_res) - 1].find(attrs={"class": "b-list__item-date"}).span.text
        hour = int(splitted_time[0])
        minute = int(splitted_time[1])
        date_ret = datetime.datetime.strptime(str(date), '%d.%m.%Y').replace(hour=hour, minute=minute)
    except:
        log.exception('ria_parser: _parse_html')
    return appropriate_link, date_ret


def _parse_article_body(article, params):
    title = article.find(attrs={"class": "b-list__item-title"}).span.text
    time = article.find(attrs={"class": "b-list__item-time"}).span.text
    date = article.find(attrs={"class": "b-list__item-date"}).span.text
    if not appropriate_title(title.lower().encode('utf8'), params):
        return None
    url = DEFAULT_PREFIX + article.find('a').get('href')
    dictionary = {}
    dictionary['date'] = date
    dictionary['time'] = time
    dictionary['title'] = title
    dictionary['url'] = url
    dictionary['text'] = _parse_article_url(url)
    return dictionary


def _parse_article_url(url):
    response = requests.get(url)
    bs = BeautifulSoup(response.content[response.content.index('\n'):], 'lxml')
    result = bs.find(attrs={"class": "b-article__body js-mediator-article"})
    res = []
    for tag in result.find_all('p'):
        _res_p = tag.find(text=True)
        if _res_p:
            res.append(_res_p)
    return reduce(lambda x, y: x + y, res)
