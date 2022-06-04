import requests
import json
import time
import threading
from bs4 import BeautifulSoup

teams = ["buf/buffalo-bills", "mia/miami-dolphins", "ne/new-england-patriots", 
        "nyj/new-york-jets", "dal/dallas-cowboys", "nyg/new-york-giants",
        "phi/philadelphia-eagles"]

def week_scrape(pos: str, year: int, week: int, week_dict: dict) -> None:
    """
    Scrapes data for skill position players from a given week and adds it to the week_dict
    """
    base_url = 'https://www.espn.com/nfl/team/roster/_/name/buf/buffalo-bills'
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