import requests
from bs4 import BeautifulSoup
import json

def scrape():
    # Scrapes data to dictionary in the form: Year => Week = > Player => Stats, 
    # and outputs the data to dictionaries in the directory
    years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
    positions = ['QB', 'RB', 'WR', 'TE']
    weeks = range(1, 18)

    print('Scraping NFL player game stats ...')

    for position in positions:
        player_data_dict = {}

        for year in years:
            year_dict = {}

            for week in weeks:
                week_dict = {}

                url = 'https://www.footballdb.com/fantasy-football/index.html?pos='
                url = url + position + '&yr=' + year + '&wk=' + str(week) + '&rules=2'
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
                results = requests.get(url, headers=headers)
                soup = BeautifulSoup(results.text, 'html.parser')

                name_table = soup.find_all('table', attrs={'class': ['statistics', 'scrollable', 'tablesorter']})
                name_tbody = name_table[0].find('tbody')
                name_trs = name_tbody.find_all('tr')

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
                        'fumbles_lost': int(stats[16])                    }

                    week_dict[name] = player_dict

                year_dict['week_' + str(week)] = week_dict

            player_data_dict[year] = year_dict

        with open(position + "_data.json", "w") as outfile: 
            json.dump(player_data_dict, outfile)

        print('Completed scraping ' + position + ' stats...')

    print('Completed scraping all NFL player game stats!')

if __name__ == '__main__':
    scrape()





