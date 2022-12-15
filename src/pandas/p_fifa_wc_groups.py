import pandas as pd
import pickle
from string import ascii_uppercase as alphabet

import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from py_log import log
import constants as Constants

FOLDER_DATA = Constants.FOLDER_DATA
FOLDER_DATA_BIN = Constants.FOLDER_DATA_BIN
FOLDER_DATA_GROUPS = Constants.FOLDER_DATA_GROUPS
FOLDER_DATA_RANK = Constants.FOLDER_DATA_RANK

WC_URL = Constants.WC_URL


class PFifaWcGroups():

    def __init__(self) -> None:
        log.info('init')
        self._create_path_(FOLDER_DATA + '/' + FOLDER_DATA_GROUPS)
        self._create_path_(FOLDER_DATA + '/' + FOLDER_DATA_RANK)
        self._create_path_(FOLDER_DATA_BIN + '/' + FOLDER_DATA_GROUPS)
        self._create_path_(FOLDER_DATA_BIN + '/' + FOLDER_DATA_RANK)

    def _create_path_(self, directory) -> None:
        if not os.path.exists(directory):
            os.makedirs(directory)
            log.info(f'create directory: {directory}')

    def get_groups_year(self, year) -> None:
        url = WC_URL.format(year=year)
        log.info('start crawl groups of {year} ~ {url}'.format(
            year=year, url=url))
        all_tables = pd.read_html(url)
        dict_groups = {}
        rank = pd.DataFrame()
        g_index = 0

        for table in all_tables:
            # Groups
            if 'Pos' == table.columns[0]:
                df = table
                df.rename(columns={df.columns[1]: 'Team'}, inplace=True)
                if 'Qualification' in df.columns:
                    df.pop('Qualification')
                dict_groups[f'{alphabet[g_index]}'] = df
                g_index += 1

            # Rank
            if 'R' == table.columns[0]:
                df = table

                if 'Unnamed: 10' in df.columns:
                    df.pop('Unnamed: 10')

                for r_index in range(df[df.columns[0]].count()):
                    if 'Eliminated' in str(table.iloc[r_index][0]):
                        df = df.drop(r_index)
                rank = df

        # Save groups
        if dict_groups:
            # To file csv
            for i in dict_groups:
                df_group = pd.DataFrame(dict_groups[i])
                df_group.to_csv(FOLDER_DATA + '/' + FOLDER_DATA_GROUPS +
                                '/' + f'{year}_group_{i}.csv', index=False)

            # To binary file
            with open(FOLDER_DATA_BIN + '/' + FOLDER_DATA_GROUPS + '/' + f'{year}_dict_groups', 'wb') as output:
                pickle.dump(dict_groups, output)

        # Save rank
        if not rank.empty:
            # To file csv
            df_rank = pd.DataFrame(rank)
            df_rank.to_csv(FOLDER_DATA + '/' + FOLDER_DATA_RANK +
                           '/' + f'{year}_rank.csv', index=False)

            # To binary file
            with open(FOLDER_DATA_BIN + '/' + FOLDER_DATA_RANK + '/' + f'{year}_rank', 'wb') as output:
                pickle.dump(df_rank, output)

    def get_groups_2022(self):
        year = 2022
        url = WC_URL.format(year=year)
        log.info('start get groups of {year} ~ {url}'.format(
            year=year, url=url))

        GROUP_NUMBER = 8
        TABLE_INDEX_FIRST = 10
        TABLE_NEXT_STEP = 7

        all_tables = pd.read_html(url)
        dict_groups = {}
        for letter, i in zip(alphabet, range(TABLE_INDEX_FIRST, TABLE_INDEX_FIRST + GROUP_NUMBER * TABLE_NEXT_STEP, TABLE_NEXT_STEP)):
            df = all_tables[i]
            df.rename(columns={df.columns[1]: 'Team'}, inplace=True)
            if 'Qualification' in df.columns:
                df.pop('Qualification')
            dict_groups[f'{letter}'] = df

        if dict_groups:
            # Save groups to file csv
            for i in dict_groups:
                df_group = pd.DataFrame(dict_groups[i])
                df_group.to_csv(FOLDER_DATA + '/' + FOLDER_DATA_GROUPS +
                                '/' + f'{year}_group_{i}.csv', index=False)

            # Save groups to binary file
            with open(FOLDER_DATA_BIN + '/' + FOLDER_DATA_GROUPS + '/' + f'{year}_dict_groups', 'wb') as output:
                pickle.dump(dict_groups, output)

    def read_groups_from_binary_file(self, year):
        dict_tables = pickle.load(
            open(FOLDER_DATA_BIN + '/' + FOLDER_DATA_GROUPS + '/' + f'{year}_dict_groups', 'rb'))
        print(dict_tables)

    def read_rank_from_binary_file(self, year):
        rank = pickle.load(
            open(FOLDER_DATA_BIN + '/' + FOLDER_DATA_GROUPS + '/' + f'{year}_rank', 'rb'))
        print(rank)

    def get_groups(self):
        [self.get_groups_year(year) for year in Constants.WC_YEARS]


gWc = PFifaWcGroups()
gWc.get_groups()
# gWc.get_groups_year(1978)
