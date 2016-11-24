import requests
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import codecs
import datetime

xmldata = '''
<row name="abc" age="40" body="blalalala..." creationdate="03/10/10" />
<row name="bcd" age="50" body="blalalala..." creationdate="03/10/09" />
'''
DEFAULT_PREFIX = 'https://ria.ru/'
DEFAULT_PREFIX_URL = 'https://ria.ru/world/more.html?date={datentime}&onedayonly=1'


def start_request(argv):
    params = argv[0]
    start_date = datetime.datetime.strptime(argv[1], '%d/%m/%Y').replace(hour=23, minute=59)
    end_date = datetime.datetime.strptime(argv[2], '%d/%m/%Y').replace(hour=23, minute=59)
    exit_node = []
    with codecs.open("parsed_url.txt", "w", "utf-8") as jsonfile:
        while (end_date - start_date).days >= -1:
            url = DEFAULT_PREFIX_URL.format(datentime=end_date.strftime('%Y%m%dT%H%M%S'))
            response_json = requests.get(url)
            bs = BeautifulSoup(response_json.content[response_json.content.index('\n'):], 'lxml')
            parsed_node, end_date = parse_html(bs, params)
            exit_node += parsed_node
            print end_date.strftime('%d-%m-%y %H:%M')
        json.dump(exit_node, jsonfile, ensure_ascii=False)


def parse_html(beatifulSoup, params):
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
        # print title
        dictionary['url'] = url
        dictionary['text'] = parse_article_url(url)
        appropriate_link.append(dictionary)
    splitted_time = time.split(':')
    hour = int(splitted_time[0])
    minute = int(splitted_time[1])
    date_ret = datetime.datetime.strptime(str(date), '%d.%m.%Y').replace(hour=hour, minute=minute)
    return appropriate_link, date_ret


def appropriate_title(title, params):
    for param in params.split(' '):
        if params not in title:
            return False
    return True


def parse_article_url(url):
    response_json = requests.get(url)
    bs = BeautifulSoup(response_json.content[response_json.content.index('\n'):], 'lxml')
    result = bs.find(attrs={"class": "b-article__body js-mediator-article"})
    # print result
    res = []
    for tag in result.find_all('p'):
        _res_p = tag.find(text=True)
        if _res_p:
            res.append(_res_p)
    return res


def create_tree():
    rows = ET.fromstring('<rows>' + xmldata + '</rows>')
    print len(rows)


if __name__ == "__main__":
    start_request(sys.argv[1:])
    # parse_article_url(sys.argv[1])
