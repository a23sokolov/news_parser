## news_parser
Scrypt for parsing news by key with floating date period

### Supported Resources
* **[Ria News](https://ria.ru/)**
* **[Rbc News](https://rbc.ru/)**
* **[Tass News](https://tass.ru/)**

### How to start
0. For Windows users [Configure](https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation) Python and Environment

1. Start command "pip install requirements.txt" (install external libs to work with script)
2. After than start script with command like "python 'match_1 match_2' 'start_date' 'end_date'"
```
python app.py 'мэй' '14/07/2016' '14/07/2016'
```
will be executed three parsers: ria, rbc, tass.

```
python app.py 'мэй' '14/07/2016' '14/07/2016' x
```
where x is
```
    1: ria_parser,
    2: tass_parser,
    3: rbc_parser,
    0: ria_parser, tass_parser, rbc_parser
```

* Output will be in articles folder.

### Python
* Appropriate work with python 2.7.
