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
The database used for the API can be constructed from the JSON files present in this repository by running build_database.py. Alternatively, you can get the most recent stats by running scrape_stats.py, which will output the updated versions of these JSON files into the working directory, then running build_database.py to create the database. Only statistics for offensive skill-position players (QB, RB, WR, and TE) are available through this API.
