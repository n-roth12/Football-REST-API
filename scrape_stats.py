import requests
from bs4 import BeautifulSoup
import json

def scrape():
    positions = ['QB', 'RB', 'WR', 'TE']
    print('Scraping NFL player game stats ...')

    for position in positions:
        print("Scraping " + position + " data...")

        data = pos_scrape(position)
        with open(position + "_data.json", "w") as outfile: 
            json.dump(data, outfile)

        print('Completed scraping ' + position + ' stats.')

    print('Completed scraping all NFL player game stats.')

def pos_scrape(pos):
    years = range(2012, 2022)
    player_data_dict = {}

    for year in years:
        data = year_scrape(pos, year)
        if len(data) > 0:
            player_data_dict[str(year)] = data
        else:
            return player_data_dict

    return player_data_dict

def year_scrape(pos, year):
    weeks = range(1, 19)
    year_dict = {}

    for week in weeks:
        data = week_scrape(pos, year, week)
        if len(data) > 0:
            year_dict['week_' + str(week)] = data
        else:
            return year_dict

    return year_dict

def week_scrape(pos, year, week):
    week_dict = {}
    base_url = 'https://www.footballdb.com/fantasy-football/index.html?pos='
    url = base_url + pos + '&yr=' + str(year) + '&wk=' + str(week) + '&rules=2'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    results = requests.get(url, headers=headers)
    soup = BeautifulSoup(results.text, 'html.parser')

    name_table = soup.find_all('table', attrs={'class': ['statistics', 'scrollable', 'tablesorter']})
    name_tbody = name_table[0].find('tbody')
    name_trs = name_tbody.find_all('tr')

    if len(name_trs) < 1:
        return week_dict
    else:
        for name_tr in name_trs:
            name_div = name_tr.find('span', attrs={'class': 'hidden-xs'})
            name = name_div.text
            stats = []
            stats_tds = name_tr.find_all('td')[1:-1]
            for stat_td in stats_tds:
                stats.append(stat_td.text)

            player_dict = {
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

    return week_dict

if __name__ == '__main__':
    scrape()





