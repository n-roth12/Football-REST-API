import requests
import json
import time
import threading
from bs4 import BeautifulSoup

def scrape():
    #chrome_options = webdriver.ChromeOptions()
    #chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--no-sandbox")

    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    #driver = webdriver.Chrome('/Users/NolanRoth/Desktop/FFBRestApi/chromedriver', chrome_options=chrome_options)

    positions = ['QB', 'RB', 'WR', 'TE']
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

def pos_helper(pos, player_data_dict):
    print(f'Scraping {pos} data...')
    pos_scrape(pos, player_data_dict)
    print(f'Completed scraping {pos} data.')
    with open(pos + "_data.json", "w") as outfile:
        json.dump(player_data_dict, outfile)

def pos_scrape(pos, player_data_dict):
    years = range(2012, 2022)
    thread_list = []
    for year in years:
        year_dict = {}
        t = threading.Thread(target=year_helper, args=[pos, year, year_dict, player_data_dict])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

def year_helper(pos, year, year_dict, player_data_dict):
    print(f'Scraping {year} {pos} stats...')
    year_scrape(pos, year, year_dict)
    print(f'Completed scraping {year} {pos} stats.')
    if len(year_dict) > 0:
        player_data_dict[str(year)] = year_dict

def year_scrape(pos, year, year_dict):
    weeks = range(1, 19)
    thread_list = []

    for week in weeks:
        week_dict = {}
        t = threading.Thread(target=week_helper, args=[pos, year, week, week_dict, year_dict])
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

def week_helper(pos, year, week, week_dict, year_dict):
    week_scrape(pos, year, week, week_dict)
    if len(week_dict) > 0:
        year_dict['week_' + str(week)] = week_dict

def week_scrape(pos, year, week, week_dict):
    #base_url = 'https://www.footballdb.com/fantasy-football/index.html?pos='
    #url = base_url + pos + '&yr=' + str(year) + '&wk=' + str(week) + '&rules=2'
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    #results = requests.get(url, headers=headers)
    #soup = BeautifulSoup(results.text, 'html.parser')

    #driver.get(f'https://www.footballdb.com/fantasy-football/index.html?pos={pos}&yr={year}&wk={week}&rules=2')
    #javaScript = "window.scrollBy(0,1000);"
    #driver.execute_script(javaScript)

    #name_table = driver.element_by_xpath("//*[@class='statistics' and @class='scrollable' and @class='tablesorter']")
    #name_tbody = name_table.find_element_by_tag_name('tbody')
    #name_trs = name_tbody.find_elements_by_tag_name('tr')

    base_url = 'https://www.footballdb.com/fantasy-football/index.html?pos='
    url = base_url + pos + '&yr=' + str(year) + '&wk=' + str(week) + '&rules=2'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    for i in range(100):
        try:
            results = requests.get(url, headers=headers)
        except:
            pass
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

if __name__ == '__main__':
    start = time.perf_counter()
    scrape()
    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
