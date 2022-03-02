# Football-REST-API
An API for retrieving information about NFL players. 

## Getting Started
Run ``` pipenv shell ``` to start python virtual environment.

Run ``` pipenv install -r requirements.txt ``` to install project packages.

Run ``` python app.py ``` to start the server.

Navigate to ``` localhost:5000 ``` to view the frontend.


## Database
The database used for the API can be constructed from the JSON files present in this repository by running build_database.py. Alternatively, you can get the most recent stats by running scrape_stats.py, which will output the updated versions of these JSON files into the working directory, then running build_database.py to create the database. Only statistics for offensive skill-position players (QB, RB, WR, and TE) are available through this API.
