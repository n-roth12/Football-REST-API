import requests
import json
import time
from datetime import datetime
import threading
from bs4 import BeautifulSoup
from date_services import findWeek

"""
This script is responsible for scraping player statistics from the web and outputs
4 files into this directory that contains the scraped data. It scrapes the data
for QB, RB, WR, and TE positions only, and it does so by parsing html from footballdb.com.
The 4 json files that are output by this script can be used to create and/or update the
database being used by the API. 
"""
positions = ['QB', 'RB', 'WR', 'TE', 'DST']


def full_scrape() -> None:
    """
    Starting point for scraping all the player and dst data from all years 
    """
    print('Scraping NFL player game stats ...')
    thread_list = []

    for position in positions:
        player_data_dict = {}
        t = threading.Thread(target=pos_helper, args=[position, player_data_dict])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

    print('Completed scraping all NFL player game stats.')

def pos_helper(pos: str, player_data_dict: dict) -> None:
    """
    Helper function for threading with full_scrape
    """
    print(f'Scraping {pos} data...')
    pos_scrape(pos, player_data_dict)
    print(f'Completed scraping {pos} data.')
    with open(f'{pos}_data.json', "w") as outfile:
        json.dump(player_data_dict, outfile)

def pos_scrape(pos: str, player_data_dict: dict) -> None:
    """
    Helper function for threading with full_scrape
    """
    years = range(2012, 2022)
    thread_list = []
    for year in years:
        year_dict = {}
        t = threading.Thread(target=year_helper, args=[pos, year, year_dict, player_data_dict])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

def year_helper(pos: str, year: int, year_dict: dict, player_data_dict: dict) -> None:
    """
    Helper function for threading with full_scrape
    """
    print(f'Scraping {year} {pos} stats...')
    year_scrape(pos, year, year_dict)
    print(f'Completed scraping {year} {pos} stats.')
    if len(year_dict) > 0:
        player_data_dict[str(year)] = year_dict

def year_scrape(pos: str, year: int, year_dict: dict) -> None:
    """
    Helper function for threading with full_scrape
    """
    weeks = range(1, 19)
    thread_list = []

    for week in weeks:
        week_dict = {}
        t = threading.Thread(target=week_helper, args=[pos, year, week, week_dict, year_dict])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

def week_helper(pos: str, year: int, week: int, week_dict: dict, year_dict: dict) -> None:
    """
    Helper function for threading with full_scrape
    """
    if pos != 'DST':
        week_scrape(pos, year, week, week_dict)
    else:
        scrape_dst(year, week, week_dict)
    if len(week_dict) > 0:
        year_dict['week_' + str(week)] = week_dict

def week_scrape(pos: str, year: int, week: int, week_dict: dict) -> None:
    """
    Scrapes data for skill position players from a given week and adds it to the week_dict
    """
    base_url = 'https://www.footballdb.com/fantasy-football/index.html?pos='
    url = f'{base_url}{pos}&yr={str(year)}&wk={str(week)}&rules=2'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    for i in range(100):
        try:
            results = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            time.sleep(0.005)
        else:
            break
    else:
        print(f'Unable to scrape {pos} stats for {year} week {week}. Please try again.')

    soup = BeautifulSoup(results.text, 'html.parser')
    name_table = soup.find_all('table', attrs={'class': ['statistics', 'scrollable', 'tablesorter']})
    name_tbody = name_table[0].find('tbody')
    name_trs = name_tbody.find_all('tr')

    if len(name_trs) < 1:
        return
    else:
        for name_tr in name_trs:
            name_div = name_tr.find('span', attrs={'class': 'hidden-xs'})
            name = name_div.text
            stats = []
            stats_tds = name_tr.find_all('td')[1:-1]
            team = stats_tds[0].find('b').text
            for stat_td in stats_tds:
                stats.append(stat_td.text)

            player_dict = {
                'team': team,
                'game': stats[0],
                'points': stats[1],
                'pass_atts': int(stats[2]),
                'pass_cmps': int(stats[3]),
                'pass_yds': int(stats[4]),
                'pass_tds': int(stats[5]),
                'pass_ints': int(stats[6]),
                'pass_2pts': int(stats[7]),
                'rush_atts': int(stats[8]),
                'rush_yds': int(stats[9]),
                'rush_tds': int(stats[10]),
                'rush_2pts': int(stats[11]),
                'recs': int(stats[12]),
                'rec_yds': int(stats[13]),
                'rec_tds': int(stats[14]),
                'rec_2pts': int(stats[15]),
                'fumbles_lost': int(stats[16])
            }
            week_dict[name] = player_dict


def scrape_dst(year: int, week: int, week_dict: dict) -> None:
    """
    Scrapes DST data for a given week and year and adds it to the week_dict
    """
    base_url = 'https://www.footballdb.com/fantasy-football/index.html?pos=DST'
    url = f'{base_url}&yr={str(year)}&wk={str(week)}'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    for i in range(100):
        try:
            results = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            time.sleep(0.005)
        else:
            break
    else:
        print(f'Unable to scrape DEF stats for {year} week {week}. Please try again.')

    soup = BeautifulSoup(results.text, 'html.parser')
    name_table = soup.find_all('table', attrs={'class': ['statistics', 'scrollable', 'tablesorter']})
    name_tbody = name_table[0].find('tbody')
    name_trs = name_tbody.find_all('tr')

    if len(name_trs) < 1:
        return
    else:
        for name_tr in name_trs:
            name_div = name_tr.find('span', attrs={'class': 'hidden-xs'})
            name = name_div.text
            stats = []
            stats_tds = name_tr.find_all('td')[1:-1]
            team = stats_tds[0].find('b').text
            for stat_td in stats_tds:
                stats.append(stat_td.text)

            player_dict = {
                'full_name': name,
                'team': team,
                'game': stats[0],
                'points': stats[1],
                'sacks': stats[2],
                'interceptions': int(stats[3]),
                'safeties': int(stats[4]),
                'fumble_recoveries': int(stats[5]),
                'blocks': int(stats[6]),
                'touchdowns': int(stats[7]),
                'points_against': int(stats[8]),
                'passing_yards_against': int(stats[9]),
                'rushing_yards_against': int(stats[10]),
                'yards_against': int(stats[9]) + int(stats[10]),
            }
            week_dict[team] = player_dict


def scrape_week(year, week):
    """
    Starting point for scraping all data from a single week.
    """
    thread_list = []

    print(f'Scraping week {week}, {year} stats...')
    for position in positions:
        player_data_dict = {}
        t = threading.Thread(target=pos_helper_week, args=[position, player_data_dict, year, week])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

    print(f'Completed scraping all weeek {week}, {year} stats.')

def pos_helper_week(pos: str, player_data_dict: dict, year: int, week: int) -> None:
    """
    Helper function for threading with scrape_week
    """
    print(f'Scraping {pos} data...')
    pos_scrape_week(pos, player_data_dict, year, week)
    print(f'Completed scraping {pos} data.')
    with open(f'{pos}_update_data.json', "w") as outfile:
        result = {str(year): {f'week_{week}': player_data_dict}}
        json.dump(result, outfile)

def pos_scrape_week(pos: str, player_data_dict: dict, year: int, week: int) -> None:
    """
    Helper function for threading with scrape_week
    """
    year_dict = {}
    if pos != 'DST':
        week_scrape(pos, year, week, player_data_dict)
    else:
        scrape_dst(year, week, player_data_dict)

if __name__ == '__main__':
    start = time.perf_counter()
    scrape()
    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')


