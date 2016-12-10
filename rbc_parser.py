import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
from utils import appropriate_title
import log as Logger
import dateparser

DEFAULT_PREFIX_URL = 'http://www.rbc.ru/filter/ajax?type=short_news%7Carticle&dateFrom={start_date}&dateTo={end_date}&offset={offset}&limit=50'
DEFAULT_OFFSET = 50
log = Logger.get_logger(__name__)


def start_request(params, start_date, end_date):
    print 'rbc_parser start'
    start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y').strftime('%d.%m.%Y')
    end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y').strftime('%d.%m.%Y')
    exit_node = []
    offset_step = DEFAULT_OFFSET
    current_offset = 0
    with codecs.open("rbc_news.txt", "w", "utf-8") as jsonfile:
        while DEFAULT_OFFSET == offset_step:
            url = DEFAULT_PREFIX_URL.format(start_date=start_date, end_date=end_date, offset=current_offset)
            response_json = requests.get(url).json()
            parsed_node, offset_step, log_date = _parse_json(response_json, params)
            current_offset += offset_step
            exit_node += parsed_node
            print log_date.strftime('%d-%m-%y %H:%M')
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    print 'rbc_parser finished'


def _parse_json(response_json, params):
    appropriate_link = []
    time_art = None

    offset_step = response_json.get('count')
    try:
        beatiful_soup = BeautifulSoup(response_json.get('html'), 'lxml')
        for item in beatiful_soup.find_all('div'):

            url = item.find('a').get('href')
            title = item.find(attrs={"class": 'item_medium__title'})
            _date = item.find(attrs={"class": 'item_medium__time'})
            date_n_time_art = _date.find(text=True).strip() if _date else None

            if title and date_n_time_art:
                title = title.find(text=True).strip()
                date_n_time_art = dateparser.parse(date_n_time_art)

            if not title or not appropriate_title(title.lower().encode('utf8'), params):
                continue

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
        log.exception('rbc_parser: _parse_json')

    return appropriate_link, offset_step, date_n_time_art


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
