import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
from utils import appropriate_title
import sys
import log as Logger

DEFAULT_PREFIX_URL = 'http://www.rbc.ru/filter/ajax?type=short_news%7Carticle&dateFrom={start_date}}&dateTo={end_date}&offset={offset}&limit=50'
DEFAULT_OFFSET = 50
log = Logger.get_logger(__name__)


def start_request(params, start_date, end_date):
    sys.stdout.write('rbc_parser start')
    start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
    end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y')
    exit_node = []
    offset_step = 50
    with codecs.open("rbk_news.txt", "w", "utf-8") as jsonfile:
        # while DEFAULT_OFFSET == offset_step:
        url = DEFAULT_PREFIX_URL.format(datentime=end_date)
        print url
        response_json = requests.get(url).json()
        parsed_node, offset_step = _parse_json(response_json, params)
        print datetime.datetime.fromtimestamp(end_date).strftime('%d-%m-%y %H:%M')
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    sys.stdout.write('rbc_parser finished')


def _parse_json(response_json, params):
    appropriate_link = []
    time_art = None
    count = 0

    offset_step = response_json.get('count')
    try:
        beatiful_soup = BeautifulSoup(response_json.get('html'), 'lxml')
        for item in beatiful_soup.find_all('href'):
            count += 1
            print count
            if count == 5:
                print item

            bs = BeautifulSoup(item.get('html'), 'lxml')
            url = bs.find('a').get('href')
            title = bs.find(attrs={"class": 'news-feed__item__title'})
            if title:
                title = title.find(text=True)
            if not title or not appropriate_title(title.lower().encode('utf8'), params):
                continue

            date_n_time_art = datetime.datetime.fromtimestamp(float(item.get('time_t')))
            time_art = date_n_time_art.strftime('%H:%M')
            date = date_n_time_art.strftime('%d.%m.%y')
            dictionary = {}
            dictionary['date'] = date
            dictionary['time'] = time_art
            dictionary['title'] = title
            dictionary['url'] = url
            dictionary['text'] = _parse_article_url(url)
            appropriate_link.append(dictionary)
    except:
        log.exception('rbc_parser: url = ' + url)

    return appropriate_link, offset_step


def _parse_article_url(url):
    try:
        response_json = requests.get(url)
        bs = BeautifulSoup(response_json.content[response_json.content.index('\n'):], 'lxml')
        result = bs.find(attrs={"class": "article__text"})
        res = []
        for tag in result.find_all('p'):
            _res_p = tag.find(text=True)
            if _res_p:
                res.append(_res_p)
        return reduce(lambda x, y: x + y, res)
    except:
        log.exception('rbc_parser: url = ' + url)
    return None
# http://www.rbc.ru/filter/ajax?type=short_news%7Carticle&dateFrom=28.11.2015&dateTo=27.11.2016&offset=0&limit=50

if __name__ == "__main__":
    start_request(sys.argv[1], sys.argv[2], sys.argv[3])
