# Project Title: Heros-Derby
#### Video Demo: 
#### Description:
This project is a web application built on the following technologies:
- Javascript
- Flask
- Python
- CSS
- HTML
- SQL


The overall aim of the project is to promote local sporting activities and related charity work. The target users of the platform include football fanatics, players, coaches and sponsors. Through the platform football clubs can grow their fanbase and access funds. Users can get also to know more about players in their locality.

The project follows Flask application design structure i.e. Static folder for images, CSS files and JS scripts, Templates folder for HTML files, app.py file a database file and a README.md file. 

## Static Folder
### images
This folder contains different images used through out the program. i.e the landing page image, teams logo and a few users images.
### scripts.js
To enhance user experience on the platform several functionalities are hundled in this file. These include showing and hidding the login form, displaying more or less teams in the teams template.
### styles.css
All template styles are handled here. They include page fonts, size among others.

## Templates
### landingpage.html
This page says what the platform is all about and lists a few past games under the featured games section and future games on the upcoming games section. The games are fetched from derby.db database through the recent_matches function and upcoming_games function in the root route at the app.py file.
Through the "Get in the Game" button the user is redirected to the results page.
A landing page image showing a guy playing football on the shores is positioned on top of other items to enhance aesthetics.

### login.html
Contains the login form and is rendered through the /login route at app.py. Four login options are available for normal users, players, coaches and sponsors.
Some featured are automatically hidden or added depending on the user type.
### register.html
Contains the login form and is rendered through the /login route at app.py.
### layout.html
Contains the boilerplate on top of which other templates are rendered.
### player.html
When rendered it lists a featured player information
### index.html
### teams.html
This page is rendered through /index route at app.py. It contains:
Recent Matches table that lists three most recent matches the score and date played. Below the table is a "Add Match" button only availabe verified players and coaches.
Results table which which lists top 10 teams in the league and an analysis of points gunnered,
total wins, draws and losses.

Through the 'Show More' button the user is able to see a full list of all teams and their standings.


### Portfolio
I have a profound interest in football and I would like to see people in my neighborhood make it in the international football space. Though am not a player myself, I enjoy watching display of football talent and skills especially by the youth.

This page gives them a space to showcase their talents and for the recruiters, sponsors, managers to spot their talent and accord them the resources, mentorship and even an opportunity to play in international arena. 

This page is layedout as a  3-column grid. The logged in user is able to see images they have uploaded on various sporting activities.

## app.py
This file contans user session configurations and the function userSession to handle user data as the user navigates around the page.
The program connects to the database using the sqlite3 library to facilitate fetching of data from the database.

Functions to be used by different routes are defined (e.g display_recent_matches, display_teams, rank_teams, show_results, fixtures, featuredPlayer) to reduce code redundancy. 
Several routes are also defined in this file.

## derby.db
This is a sqlite database with the following tables
- Teams
- Matches
- Fixtures
- Players
- Users
- Types (e.g, player, coach, sponsor)
- Counties
- Leagues

### Conclusion
Locals will be able to see football happenings in their area and support and discuss issues to grow talent in their locality.

### Contribution
This is a solo project. 

The project is hosted on a public respository here https://github.com/samuelmwangimbuthia/Heros-Derby at the github.com.

