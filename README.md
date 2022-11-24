# NERecs

## Description
This code prints out ranked recommended places given location name, distance, current location (latitude, longitude), and desired place description by the user.

The two main files used are NERecs.py which is the main file that calls Google Places API, and currently only browses the first page token for each call. The second file is recsgui.py which is the user interface file that should be run in order to use this app. 

## To Run
Obtain a personal API key from Google Places API and add it to a file called `secret.py` as so: `API_KEY = '<your API key>'`. Then run `recsgui.py` and enter the required inputs.