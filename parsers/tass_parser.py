import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
from utils import appropriate_title
import time
from concurrent import futures

DEFAULT_PREFIX = 'http://tass.ru'
DEFAULT_PREFIX_URL = 'http://tass.ru/api/news/lenta?limit=50&before={date_end}'


def start_request(params, start_date, end_date):
    print('tass_parser start')
    start_time = time.time()
    start_date = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    end_date = int(time.mktime(datetime.datetime.strptime(end_date, '%d/%m/%Y').replace(hour=23, minute=59).timetuple()))
    exit_node = []
    with codecs.open("tass_news.txt", "w", "utf-8") as jsonfile:
        while (end_date - start_date) >= -1:
            url = DEFAULT_PREFIX_URL.format(date_end=end_date)
            response_json = requests.get(url).json()
            parsed_node, end_date = _parse_json(response_json, params)
            exit_node += parsed_node
            print(datetime.datetime.fromtimestamp(end_date).strftime('%d-%m-%y %H:%M'))
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    print("tass_parser finished --- %s seconds ---" % (time.time() - start_time))


def _parse_json(response_json, params):
    appropriate_link = []
    articles = response_json.get('articles')
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        appropriate_link = list(executor.map(lambda p: _parse_article_body(p, params), articles))
    appropriate_link = filter(lambda x: x, appropriate_link)
    date_n_time_art = datetime.datetime.fromtimestamp(float(articles[len(articles) - 1].get('time')))
    return appropriate_link, time.mktime(date_n_time_art.timetuple())


def _parse_article_body(article, params):
    title = article.get('title')
    url = DEFAULT_PREFIX + article.get('url')
    date_n_time_art = datetime.datetime.fromtimestamp(float(article.get('time')))
    # ignoring interviews
    if not appropriate_title(title.lower().encode('utf8'), params) or 'interviews' in url:
        return None

    time_art = date_n_time_art.strftime('%H:%M')
    date = date_n_time_art.strftime('%d.%m.%y')
    dictionary = {}
    dictionary['date'] = date
    dictionary['time'] = time_art
    dictionary['title'] = title
    dictionary['url'] = url
    dictionary['text'] = _parse_article_url(url)

    return dictionary


def _parse_article_url(url):
    response_json = requests.get(url)
    bs = BeautifulSoup(response_json.content[response_json.content.index('\n'):], 'lxml')
    result = bs.find(attrs={"class": "b-material-text__l js-mediator-article"})
    paragraphs = result.find_all('p')
    map_result = list(map(lambda element: element.find(text=True), paragraphs))
    res = reduce(lambda x, y: x + y, list(filter(lambda x: x is not None, map_result)))
    return res
