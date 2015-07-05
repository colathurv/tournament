AUTHOR ::  Colathur Vijayan ["VJN" in short] 

###### 1. What does this project contain ?
This project contains the following python modules, database setup files, CSV files and HTML/CSS files that together
help create a simple "Bookstore Application" that runs on SQLLITE and FLASK, using the SQL ALCHEMY ORM.

###### application.py
###### category_database_setup.py
###### category_styles.css
###### login.html
###### categories.html
###### itemsforcategory.html
###### itemdesc.html
###### newitem.html
###### edititem.html
###### deleteitem.html
###### items.csv

###### 2. How to run this project ?
1. Do the following to create the DB objects and initial set data
python category_database_setup.py 
2. Copy all html files above to a directory called templates. Modify login.html as below 
data-clientid="<Populate the client secrets from your Google Developer Account>"
3. Store your clients secret file from google as clients_json in thesame directory where the python files are in your
file system.
4. python application.py 
5. After step 4 go to the following URL in your web browser and logging using your googleplus account 
http://localhost:5000/login
6. If you want to access this application with out a login, you could invoke 
http://localhost:5000/categories
7. For API endpoints you could use any one of these
http://localhost:5000/categories/1/items/JSON
http://localhost:5000/categories/1/1/itemdetail/JSON
