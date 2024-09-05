# Path Pulse

## Author: James Brooks

## Description

Path Pulse is designed to be a simple and easy to use website that allows a user to view a basic overview of a trip they are planning by providing a city name with start and end dates. The website currently provides weather data with the framework to add more information in the future like local restaurants and other activities.

The website will return information regardless of being logged in or not. However, by logging in the user's trips will be saved and will be returned as a list they can access on subsequent logins, until the user decides they no longer wish to view that trip and can remove it at will.

### The project is primarily a remake and expansion upon a project I previously worked on with a group during my education called Trip Bool, the link to the GitHub Repo for the organization can be found here: [Link](https://github.com/Trip-Bool)

## Links and Resources

- [Front End Application Link](https://path-pulse.vercel.app)
- APIs
  - [Geocoding API - LocationIQ](https://locationiq.com)
  - [Weather API - OpenMetro](https://open-meteo.com)

## Setup

- ENV Requirements
  - Database
    - The application is set to use a PostgreSQL Database, so if you intend to use a different type, you will need to made the necessary adjustments for usage.
    - DB_NAME - The name of the production database for the application.
    - DB_USER - The user for the production database.
    - DB_PASSWORD - The password for the production database.
    - DB_HOST - The host address for the production database.
    - DB_PORT - The port that the production database uses.
  - Auth0
    - AUTH0_CLIENT_ID - The client id for your Auth0 Integration
    - AUTH0_CLIENT_SECRET - The client secret for your Auth0 Integration
    - AUTH0_DOMAIN -  The domain for your Auth0 Integration
  - App Specific  
    - SECRET_KEY - The secret key for your app to act as authorization for various purposes. The recommended method to generate a secret key is to run the command `openssl rand -hex 32` in your terminal and copy/paste the result as the env value.
    - LOCATION_API - Your API key for LocationIQ.
  - Test Database
    - The code is set to use a local PostgreSQL database for testing so as not to interfere with the production data.
    - TEST_DB_USER - The user for the testing database.
    - TEST_DB_PASSWORD - The password for the testing database.
- To run the application locally, you use the command `python manage.py runserver` from the root directory.
  - To make it work, you first need to create a virtual environment and use `pip install -r requirements.txt` to get all the packages.
  - Then you need to run the migrations to set the database up.
    - `python manage.py makemigrations path_pulse` to get Django to find the model.
    - `python manage.py migrate` to commit the changes and push them to the database.
  - If you ever change the models in the future, you will need to run the migration commands again to commit them to the database.

## Tests

- To run the tests, the basic way is to use `./manage.py test`.
  - However, the code is set up to use coverage.py to ensure proper test coverage, in which case the steps would be as follows;
    - `coverage run manage.py test` to run the tests as normal while compiling a report of what code is run by the tests.
    - `coverage report` to print out a console message for each file and how much of the code is covered.
    - `coverage html` to create an HTML document so you can examine exactly which lines of code are or are not covered in greater detail.

- There are currently 22 tests split into two files, one for the models and one for the views in views.py.

- The tests, according to coverage.py, achieve 98% coverage overall with the few misses being parts of the code that don't need testing like the manage.py "Django couldn't be imported" error message.
  - To avoid this, I created a .coveragerc file to tell it to ignore the files that don't need testing like the database migrations, manage.py and settings.py.
