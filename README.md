# Football-REST-API
An API for retrieving information about NFL players. 

## Getting Started
<ul>
  <li>Clone the repository</li>
  <li>Run 
  ```
  pipenv shell
  ```
  inside /FFBApi to start python virtual environment.</li>
  <li>Run 
  ```
  pipenv install -r requirements.txt
  ```
  to install project packages.</li>
  <li>Run 
  ```
  python app.py
  ```
  to start the server.</li>
  <li>Navigate to 
  ```
  localhost:5000
  ```
  to view the frontend.</li>
</ul>

## Database
The database used for the API can be constructed from the JSON files present in this repository by running build_database.py. Alternatively, you can get the most recent stats by running scrape_stats.py, which will output the updated versions of these JSON files into the working directory, then running build_database.py to create the database. Only statistics for offensive skill-position players (QB, RB, WR, and TE) are available through this API.
