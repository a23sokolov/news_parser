# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
from utils import appropriate_title
import time
from concurrent import futures
import log as Logger

DEFAULT_PREFIX = 'http://tass.ru'
DEFAULT_PREFIX_URL = 'http://tass.ru/api/news/lenta?limit=50&before={date_end}'

log = Logger.get_logger(__name__)


def start_request(params, start_date, end_date):
    print('tass_parser start')
    start_time = time.time()
    start_date = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    end_date = int(time.mktime(datetime.datetime.strptime(end_date, '%d/%m/%Y').replace(hour=23, minute=59).timetuple()))
    exit_node = []
    with codecs.open("articles/tass_news.txt", "w", "utf-8") as jsonfile:
        while (end_date - start_date) >= -1:
            url = DEFAULT_PREFIX_URL.format(date_end=end_date)
            response_json = requests.get(url).json()
            parsed_node, end_date = _parse_json(response_json, params)
            exit_node += parsed_node
            print(datetime.datetime.fromtimestamp(end_date).strftime('%d-%m-%y %H:%M'))
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    print("tass_parser finished --- %d nodes, %s seconds ---" % (len(exit_node), (time.time() - start_time)))


def _parse_json(response_json, params):
    appropriate_link = []
    articles = response_json.get('articles')
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        appropriate_link = list(executor.map(lambda p: _parse_article_body(p, params), articles))
    appropriate_link = filter(lambda x: x, appropriate_link)
    date_n_time_art = _find_article_with_date(articles)
    date_n_time_art = datetime.datetime.fromtimestamp(float(date_n_time_art))
    return appropriate_link, time.mktime(date_n_time_art.timetuple())


def _find_article_with_date(articles):
    position = len(articles) - 1
    while (articles[position].get('time') is None and position > 0):
        position = position - 1
    return articles[position].get('time')


def _parse_article_body(article, params):
    try:
        date_n_time_art = title = url = None
        title = article.get('title')
        url = DEFAULT_PREFIX + article.get('url')
        if article.get('time') is None:
            print(article.get('time'))
        date_n_time_art = datetime.datetime.fromtimestamp(float(article.get('time'))) if article.get('time') is not None else None
        # ignoring interviews
        if date_n_time_art is None or not appropriate_title(title.lower().encode('utf8'), params) or 'interviews' in url:
            return

        if title and url:
            time_art = date_n_time_art.strftime('%H:%M')
            date = date_n_time_art.strftime('%d.%m.%y')
            dictionary = {}
            dictionary['date'] = date
            dictionary['time'] = time_art
            dictionary['title'] = title
            dictionary['url'] = url
            dictionary['text'] = _parse_article_url(url)
            return dictionary
        else:
            return
    except:
        log.exception('tass_parser: _parse_article_body')
        return


def _parse_article_url(url):
    response_json = requests.get(url)
    bs = BeautifulSoup(response_json.content[response_json.content.index('\n'):], 'lxml')
    result = bs.find(attrs={"class": "b-material-text__l js-mediator-article"})
    paragraphs = result.find_all('p')
    map_result = list(map(lambda element: element.find(text=True), paragraphs))
    res = reduce(lambda x, y: x + y, list(filter(lambda x: x is not None, map_result)))
    return res
