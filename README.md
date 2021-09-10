# Football-REST-API
An API for retrieving information about NFL players. 

## Endpoints
- /players : Returns the list of all players in the database.
- /stats/\<name>/\<year>/\<week> : Returns the game stats of a specific player from a specific week.
- /stats/\<name>/\<year> : Returns the season total stats of a specific player from a specific year.
- /top/\<year>/\<week> : Returns the top fantasy player for a specific year and week including their stats.

## Database
The database is constructed by running scrape_stats.py, which scrapes the stats for every player between 2013 and 2020 into JSON files, then running
build_database.py, which creates the database using these JSON files. Only statistics for QBs, RBs, WRs, and TEs are scraped.
