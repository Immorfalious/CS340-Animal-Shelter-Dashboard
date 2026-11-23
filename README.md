# CS 340 Animal Shelter Dashboard

This is my Animal Shelter project from CS 340 Client/Server Development at SNHU. I used Python and MongoDB to work with the animal records and Dash to put together a dashboard that makes the data easier to look through. The project focuses on finding dogs that meet the different rescue requirements for Grazioso Salvare.

## What it does

The dashboard reads animal records from the `aac` database and puts them into a table. You can search and sort through the records, pick an animal to see its location on the map, and filter the list by rescue type. There's also a pie chart that shows the different breeds in the results. It updates when you change the filter.

The filter options are Water Rescue, Mountain/Wilderness Rescue, Disaster/Individual Tracking, and Reset. Each rescue option checks the breed, sex, and age ranges from the assignment. Reset shows all the records again.

## Project files

- `CRUD_Python_Module.py`: the MongoDB code for creating, reading, updating, and deleting records.
- `dashboard.py`: the dashboard itself, including the filters, table, chart, and map.
- `notebooks/AnimalShelterDashboard.ipynb`: lets me run the dashboard through Jupyter.
- `notebooks/ProjectOneTestScript.ipynb`: tests the CRUD methods. It adds and deletes a test record, so I wouldn't run it on a database where I need to keep everything unchanged.
- `assets/grazioso-salvare.svg`: the logo used in the dashboard, linked to the SNHU website.
- `tests/test_dashboard_logic.py`: tests for the filter rules and some of the dashboard data handling.

## How to run it

You'll need Python, MongoDB, and the Austin Animal Center data loaded into the `aac.animals` collection. I didn't include the dataset in the project files.

1. Open the project folder and run `pip install -r requirements.txt`.
2. Make a copy of `.env.example` and name it `.env`. Fill in your MongoDB settings there. Don't upload your real passwords to GitHub.
3. Start MongoDB and make sure the `aac` database has an `animals` collection.
4. Run `python dashboard.py`, then open `http://127.0.0.1:8050` in your browser. You can also start Jupyter and open `notebooks/AnimalShelterDashboard.ipynb`.

The dashboard picks up the settings from `.env` if the file is there. If it can't connect to MongoDB, it'll show a connection message instead of the animal data.

## A few notes

The data needs fields like `breed`, `sex_upon_outcome`, `age_upon_outcome_in_weeks`, `location_lat`, and `location_long`. Animals without map coordinates can still show up in the table and pie chart.

I kept the MongoDB connection separate from the dashboard so I could test the CRUD functions without having to run everything together. I also left out installed packages and my local settings since those don't need to be on GitHub.

I checked that the Python code compiles and checked the filter logic with tests. I haven't run the dashboard against my original Codio database yet, so I still need to check how everything behaves with the actual records and grab screenshots.

I'm also using this project for CS 499. I plan to improve the database queries, filtering, and indexing for that class, but those changes are separate from this version.
