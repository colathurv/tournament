-- Table definitions for the tournament project.

-- Author :: Colathur Vijayan [VJN]
-- Note :: In all DDLs, the drop is added to start on a clean slate and also avoid nuisance errors, if in case
-- these tables exist already.

-- DDL for tournaments table
DROP TABLE IF EXISTS tournaments CASCADE;
CREATE TABLE tournaments (
      tournament_id SERIAL PRIMARY KEY,
      tournament_name VARCHAR(32) NOT NULL UNIQUE
       );

-- DDL for players table
DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players (
      player_id SERIAL PRIMARY KEY,
      player_name VARCHAR(32) NOT NULL
       );


-- DDL for tournament roster table
DROP TABLE IF EXISTS tournament_roster;
CREATE TABLE tournament_roster (
      tournament_id integer references tournaments,
      player_id integer references players
       );

-- DDL for matches  table
DROP TABLE IF EXISTS matches;
CREATE TABLE matches (
      match_id SERIAL PRIMARY KEY,
      tournament_id integer references tournaments,
      winner_id integer references players(player_id),
      loser_id integer references players(player_id),
      match_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
       );
