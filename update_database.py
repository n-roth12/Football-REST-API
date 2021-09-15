import requests
from bs4 import BeautifulSoup
import json

from api.models import PlayerGameStats, Player, Week, Year
from api import db, ma
from collections import OrderedDict


## do scrape_stats.py and build_database.py in one step, and have it recognize
## the last week the database was updated and start from there. if it fails
## stop working