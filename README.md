# Football-REST-API
An API for retrieving information about NFL players. 

## Endpoints
The base URL for all endpoints is 127.0.0.1:5000/api.

#### /players : Returns the list of all players in the database.
<ul>
  <li>Parameters : None</li>
</ul>

#### /stats/\<name>/\<year>/\<week> : Returns the game stats of a specific player.
<ul>
  <li>Parameters : Name, Year, Week</li>
    <ul>
      <li>Name (Required) : The name of the player whose stats will be returned. Format as Firstname_Lastname.</li>
      <li>Year (Required) : The year from which to return stats.</li>
      <li>Week (Optional) : The week of the season from which to return stats. If week is not specified, the season total stats of the specified year will be returned.</li>
    </ul>
</ul>

#### /top/\<year>/\<week>/\<pos> : Returns the stats of players ordered by fantasy points finish.
<ul>
  <li>Parameters : Year, Week, Pos</li>
  <ul>
    <li>Year (Required) : The year from which to return stats</li>
    <li>Week (Required) : The week from which to return stats</li>
    <li>Pos (Optional) : The position to filter players by. The options are QB, RB, WR, and TE. If the position is not specified, the stats from all players will be returned.</li>
  </ul>
</ul>

## Database
The database is constructed by running scrape_stats.py, which scrapes the stats for every player between 2013 and 2020 into JSON files, then running
build_database.py, which creates the database using these JSON files. Only statistics for QBs, RBs, WRs, and TEs are available through this API.
