AUTHOR ::  Colathur Vijayan ["VJN" in short] 

###### 1. What does this project contain ?
This project contains the following python modules and a sql file that contains DDLs
[tested against a postgreSQL database] which implement stateless APIs that can be used to simulate a tournament that uses the swiss type of competition where in players are not eliminated, rather the best scoring player wins, with each round pairing all players [with the only exception where in the total number of players is ODD] with each pair consisting of players that have the closest scores.

###### tournament.py
###### tournament_test.py
###### tournament.sql

###### 2. How to run this project ?
To run it create a database called tournament in a postgreSQL database, create the schema by running the tournament.sql against the tournament database, copy all the python file in a directory of your choice, which your python interpeter can see and just run tournament_test.py.