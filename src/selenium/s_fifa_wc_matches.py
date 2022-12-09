import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import os
import datetime
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import constants as Constants
from py_log import log

FOLDER_DATA = Constants.FOLDER_DATA
WC_URL = Constants.WC_URL
FIFA_WORLDCUP = Constants.FIFA_WORLDCUP + '_selenium'
WC_2022 = 2022


class CrawlFifaWorldCupMatches:

    def __init__(self, years) -> None:
        options = Options()
        # Runs Chrome in headless mode. (~ options.headless = True)
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-gpu')  # applicable to windows os only
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")

        # https://stackoverflow.com/questions/66997942/error-with-permissions-policy-header-when-using-chromedriver-to-a-headless-br
        # Fix issue "Error with Permissions-Policy header: Unrecognized origin: 'intake-analytics.wikimedia.org'."
        options.add_argument('--log-level=1')

        service = Service(executable_path=r'C:\path\to\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.years = years

    def __repr__(self):
        return f'driver: {self.driver}, years: {self.years}'

    def crawl_matches(self, year):
        log.info('{year} start'.format(year=year))
        web = WC_URL.format(year=year)

        self.driver.get(web)

        home = []
        score = []
        away = []

        _matches = self.driver.find_elements(
            by='xpath', value='//td[@align="right"]/.. | //td[@style="text-align:right;"]/..')
        _tag = 'td'
        _count_table = 0
        log.info("{year} table {count_table}: tag '{tag}' len: {len}".format(
            year=year, count_table=_count_table, tag=_tag, len=len(_matches)))
        
        for _match in _matches:
            # Ignore some tables
            if self.ignore_match(year, _match):
                break

            _home = _match.find_element(
                by='xpath', value='./{tag}[1]'.format(tag=_tag)).text.strip()
            _score = _match.find_element(
                by='xpath', value='./{tag}[2]'.format(tag=_tag)).text.strip()
            _away = _match.find_element(
                by='xpath', value='./{tag}[3]'.format(tag=_tag)).text.strip()

            if (_home != '' and _score != '' and _away != ''):
                home.append(_home)
                score.append(_score)
                away.append(_away)

        _matches = self.driver.find_elements(
            by='xpath', value='//th[@class="fhome"]/..')
        _tag = 'th'
        _count_table = 0
        log.info("{year} table {count_table}: tag '{tag}' len: {len}".format(
            year=year, count_table=_count_table, tag=_tag, len=len(_matches)))

        for _match in _matches:
            _home = _match.find_element(
                by='xpath', value='./{tag}[1]'.format(tag=_tag)).text.strip()
            _score = _match.find_element(
                by='xpath', value='./{tag}[2]'.format(tag=_tag)).text.strip()
            _away = _match.find_element(
                by='xpath', value='./{tag}[3]'.format(tag=_tag)).text.strip()

            if (_home != '' and _score != '' and _away != ''):
                home.append(_home)
                score.append(_score)
                away.append(_away)

        dict_football = {'home': home, 'score': score, 'away': away}
        df_football = pd.DataFrame(dict_football)
        df_football['year'] = year
        return df_football

    def ignore_match(self, year, match):

        # Ignore table 'Top 10 highest attendances' in 2022
        if year == 2022 and match.find_element(by='xpath', value='./td[1]') is not None:
            home = match.find_element(by='xpath', value='./td[1]').text.strip()
            if '1' == home:
                _t = 'Top 10 highest attendances'
                log.warning('{year} ignore table has text: {text}'.format(
                    year=year, text=_t))
                return True
        return False

    def get_results_one_year(self, year):
        log.info('{year} start'.format(year=year))
        df_fifa = self.crawl_matches(year)
        df_fifa.to_csv(FOLDER_DATA + '/' + FIFA_WORLDCUP +
                       f'_{year}.csv', index=False)
        log.info('{year} end'.format(year=year))

    def get_results_history(self):
        time_start = datetime.datetime.now()
        log.info('{years} start {time}'.format(
            years=self.years, time=time_start))

        fifa = [self.crawl_matches(year) for year in self.years]

        time_end = datetime.datetime.now()
        log.info('{years} end {time} ~ time crawl: {time_crawl}'.format(
            years=self.years, time=time_end, time_crawl=time_end-time_start))

        df_fifa = pd.concat(fifa, ignore_index=True)
        file_save = FOLDER_DATA + '/' + FIFA_WORLDCUP + '_history.csv'

        df_fifa.to_csv(file_save, index=False)
        log.info('end {len} years, done write file: {file}'.format(
            len=len(self.years), file=file_save))


# Time crawl slower with BeautifulSoup
wc = CrawlFifaWorldCupMatches(Constants.WC_YEARS_BEFORE)
log.info(wc)
# wc.get_results_one_year(WC_2022)
# wc.get_results_history()