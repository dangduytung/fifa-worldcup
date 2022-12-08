from bs4 import BeautifulSoup
import pandas as pd

import requests
import os
import datetime
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import constants
from py_log import log


FOLDER_SAVE_lOG = constants.FOLDER_SAVE_lOG

WC_URL = constants.WC_URL
FIFA_WORLDCUP = constants.FIFA_WORLDCUP
WC_2022 = 2022


def init():
    print('init')
    if not os.path.exists(FOLDER_SAVE_lOG):
        os.mkdir(FOLDER_SAVE_lOG)


"""
Crawl matches fifa-worldcup
"""

def crawl_matches(year):
    log.info('{year} start'.format(
        year=year))
    web = WC_URL.format(year=year)
    response = requests.get(web)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    matches = soup.find_all('table')
    # matches = soup.find_all('div', class_='footballbox')
    _len = len(matches)
    log.info("{year} ~ length matches: {len}".format(
        year=year, len=_len))

    home = []
    score = []
    away = []

    for match in matches:

        # Ignore table 'Match summary' in 2010
        if match.find('td', attrs={"align": "center"}) is not None:
            if match.find(attrs={"align": "center"}).get_text().rstrip()  == 'Preliminary events':
                continue

        if match.find('th', class_='fhome') is not None:
            home.append(match.find('th', class_='fhome').get_text().rstrip())
            score.append(match.find('th', class_='fscore').get_text().rstrip())
            away.append(match.find('th', class_='faway').get_text().rstrip())

        if match.find(attrs={"align": "right"}) is not None:
            _m_tr = match.find_all(attrs={"align": "right"})
            for _m in _m_tr:
                home.append(_m.parent.find_all('td')[0].get_text().rstrip())
                score.append(_m.parent.find_all('td')[1].get_text().rstrip())
                away.append(_m.parent.find_all('td')[2].get_text().rstrip())

    dict_football = {'home': home, 'score': score, 'away': away}
    df_football = pd.DataFrame(dict_football)
    df_football['year'] = year

    log.info('{year} end'.format(
        year=year))
    return df_football


"""
Get result matches by one year
"""


def get_results_one_year(year):

    log.info('{year} start'.format(year=year))
    df_fifa = crawl_matches(year)
    df_fifa.to_csv(FOLDER_SAVE_lOG + '/' + FIFA_WORLDCUP +
                   f'_{year}.csv', index=False)
    log.info('{year} end'.format(year=year))


"""
Get result matches wc historical matches
Just run one
"""


def get_results_history(years):

    _time_start = datetime.datetime.now()
    log.info('{years} start {time}'.format(
        years=years, time=_time_start))
    fifa = [crawl_matches(year) for year in years]

    _time_end = datetime.datetime.now()
    log.info('{years} end {time} ~ time crawl: {time_crawl}'.format(
        years=years, time=_time_end, time_crawl=_time_end-_time_start))

    df_fifa = pd.concat(fifa, ignore_index=True)
    file_save = FOLDER_SAVE_lOG + '/' + FIFA_WORLDCUP + '_history.csv'

    df_fifa.to_csv(file_save, index=False)
    log.info('end {len} years, done write file: {file}'.format(
        len=len(years), file=file_save))


if __name__ == "__main__":
    init()

    # get_results_one_year(WC_2022)

    # get_results_history(constants.WC_YEARS_BEFORE)