# Football-REST-API
An API for retrieving information about NFL players. 

## Getting Started
Run ``` pipenv shell ``` to start python virtual environment.

Run ``` pipenv install -r requirements.txt ``` to install project packages.

Run ``` python app.py ``` to start the server.

Navigate to ``` localhost:5000 ``` to view the frontend.


## Database
The database used for the API can be constructed from the JSON files present in this repository by running:
``` build_database.py ```
However, the JSON files may not contain the most recent stats.
Alternatively, you can get the most recent stats by running:
``` scrape_stats.py ```
This will output the updated versions of these JSON files into the working directory, then you can use build_database.py to create the database.
