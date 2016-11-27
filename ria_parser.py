import requests
from bs4 import BeautifulSoup
import json
import codecs
import datetime
from utils import appropriate_title

DEFAULT_PREFIX = 'https://ria.ru/'
DEFAULT_PREFIX_URL = 'https://ria.ru/world/more.html?date={datentime}&onedayonly=1'


def start_request(params, start_date, end_date):
    print('ria_parser start')
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
            print end_date.strftime('%d-%m-%y %H:%M')
        json.dump(exit_node, jsonfile, ensure_ascii=False)
    print('ria_parser finished')


def _parse_html(beatifulSoup, params):
    appropriate_link = []
    time = None
    count = 0
    for tag in beatifulSoup.find_all(attrs={"class": "b-list__item"}):
        count += 1
        title = tag.find(attrs={"class": "b-list__item-title"}).span.text
        time = tag.find(attrs={"class": "b-list__item-time"}).span.text
        date = tag.find(attrs={"class": "b-list__item-date"}).span.text
        if not appropriate_title(title.lower().encode('utf8'), params):
            continue
        url = DEFAULT_PREFIX + tag.find('a').get('href')
        dictionary = {}
        dictionary['date'] = date
        dictionary['time'] = time
        dictionary['title'] = title
        dictionary['url'] = url
        dictionary['text'] = _parse_article_url(url)
        appropriate_link.append(dictionary)
    splitted_time = time.split(':')
    hour = int(splitted_time[0])
    minute = int(splitted_time[1])
    date_ret = datetime.datetime.strptime(str(date), '%d.%m.%Y').replace(hour=hour, minute=minute)
    return appropriate_link, date_ret


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
