#!/usr/bin/env python
#
# Test cases for tournament.py
# Author :: Colathur Vijayan ["VJN"]
#

# Note - These unit tests are written with the following goals
# 1. Each tests will test a functional unit of work, with the understanding 
#    that a unit may call more than one function.
# 2. The union of all tests will make sure all atomic functions are tested.
# 3. Each test is self-sufficient and can be executed independent of other
#    tests.


from tournament import *

def testRegistration():
    """Tests the function registerPlayer"""
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate players cascade; 
    truncate tournaments cascade; 
    """
    cur.execute(query_str)
    conn.commit()
    
    # These players are AS IS from udacity test template that are added  
    # and will be re-used in the test suite 
    i1 = registerPlayer("Markov Chaney")
    i2 = registerPlayer("Joe Malik")
    i3 = registerPlayer("Mao Tsu-hsi")
    i4 = registerPlayer("Atlanta Hope")
    i5 = registerPlayer("Melpomene Murray")
    i6 = registerPlayer("Randy Schwartz")
    i7 = registerPlayer("Bruno Walton")
    i8 = registerPlayer("Boots O'Neal")
    i9 = registerPlayer("Cathy Burton")
    i10 = registerPlayer("Diane Grant")
    i11 = registerPlayer("Twilight Sparkle")
    i12 = registerPlayer("Fluttershy")
    i13 = registerPlayer("Applejack")
    i14 = registerPlayer("Pinkie Pie")
    query_str = """select count(player_id) from players""" 
    cur.execute(query_str)
    row = cur.fetchone()
    conn.close()
    if row[0] == 14:
        print "testRegistration passed.."
    else:
        raise ValueError(
        "testRegistration failed ...")
    player_ids = [i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,i13,i14]
    return player_ids
        
        
def testTournament():
    """Tests the functions createTournament and deleteTournament"""
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
    
    # Create a new Tournament
    id = createTournament("Swiss Open 2015")
    conn = connect()
    cur = conn.cursor()
    query_str = """select tournament_name from tournaments  
    where tournament_id = %s"""
    cur.execute(query_str, [id])
    row = cur.fetchone()
    conn.close()
    
    # Testing Starts
    if row[0] != 'Swiss Open 2015':
        raise ValueError("testTournament failed..")
    deleteTournament(id)
    conn = connect()
    cur = conn.cursor()
    query_str = """select tournament_name from tournaments  
    where tournament_id = %s"""
    cur.execute(query_str, [id])
    row = cur.fetchone()
    conn.close()
    if row is not None:
        raise ValueError("testTournament failed..")        
    print "testTournament passed.." 

def testTournamentPlayers(ids):
    """Tests the functions addPlayers2Tournament, countPlayers, 
    deleteMatches and delPlayersfromTournament"""   
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
   
    # Create a new tournament, add players and matches
    tid = createTournament("Swiss Open 2015")
    addPlayer2Tournament(ids[0],tid)
    addPlayer2Tournament(ids[1],tid)
    addPlayer2Tournament(ids[2],tid)
    addPlayer2Tournament(ids[3],tid)
    mid1 = reportMatch(tid,ids[0],ids[1])
    mid2 = reportMatch(tid,ids[2],ids[3])
   
    # Delete Matches
    deleteMatches(tid)
   
    # Testing for deleteMatches
    conn = connect()
    cur = conn.cursor()
    query_str = """select count(1) from matches  
    where tournament_id = %s"""
    cur.execute(query_str,[tid])
    row = cur.fetchone() 
    conn.close()
    if row[0] != 0:
        raise ValueError("testTournamentPlayers failed ...")
   
    # Testing for countPlayers, addPlayers2Tournament and 
    # delPlayersfromTournament
    c = countPlayers(tid)
    if c != 4:
        raise ValueError(
          "After adding 4 players to Tournament, countPlayers should return 4.")
    delPlayersfromTournament(tid)
    c = countPlayers(tid)
    if c != 0:
            raise ValueError("After deleting, countPlayers should return 0.")
    print "testTournamentPlayers passed .."

# Note - I have retrofitted this udacity provided test to my design 
def testStandingsBeforeMatches(ids):
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
   
    # Create a new tournament, add players and matches
    tid = createTournament("Swiss Open 2015")
    addPlayer2Tournament(ids[4],tid)
    addPlayer2Tournament(ids[5],tid)
    standings = playerStandings(tid)
   
    # Testing Starts
    if len(standings) < 2:
        raise ValueError("testStandingsBeforeMatches failed ..."
                         "Players should appear in playerStandings even before"
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("testStandingsBeforeMatches failed ..."
                         "Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("testStandingsBeforeMatches failed ..."
                         "Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "testStandingsBeforeMatches failed ..."
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("testStandingsBeforeMatches failed ..." 
                         "Registered players' names should appear in standings,"
                         "even if they have no matches played.")
    print "testStandingsBeforeMatches passed ..."

# Note - I have retrofitted this udacity provided test to my design 
def testReportMatches(ids):
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
   
    # Create a new tournament, add players and matches
    tid = createTournament("Swiss Open 2015")
    addPlayer2Tournament(ids[6],tid)
    addPlayer2Tournament(ids[7],tid)
    addPlayer2Tournament(ids[8],tid)
    addPlayer2Tournament(ids[9],tid)
    
    # Testing starts
    standings = playerStandings(tid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tid,id1,id2)
    reportMatch(tid,id3,id4)
    standings = playerStandings(tid)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("testReportMatches failed ..."
                             "Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("testReportMatches failed ..."
                             "Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("testReportMatches failed ..."
                            "Each match loser should have zero wins recorded.")
    print "testReportMatches passed ..."

# Note - I have retrofitted this udacity provided test to my design
# Test Pairings when number of players is EVEN
def testPairingsEven(ids):
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
   
    # Create a new tournament, add an EVEN number of players and matches
    tid = createTournament("Swiss Open 2015")
    addPlayer2Tournament(ids[10],tid)
    addPlayer2Tournament(ids[11],tid)
    addPlayer2Tournament(ids[12],tid)
    addPlayer2Tournament(ids[13],tid)
    
    # Testing Starts
    standings = playerStandings(tid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tid,id1, id2)
    reportMatch(tid,id3, id4)
    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "testPairingsEven failed ...."
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "testPairingsEven failed ...."
            "After one match, players with one win should be paired.")
    print "testPairingsEven passed ...."

# Note - I have retrofitted this udacity provided test to my design
# Test Pairings when number of players is ODD
def testPairingsOdd(ids):
    # Start on a clean slate
    conn = connect()
    cur = conn.cursor()
    query_str = """truncate tournaments cascade"""
    cur.execute(query_str)
    conn.commit()
    conn.close()
   
    # Create a new tournament, add an ODD number of players and matches
    tid = createTournament("Swiss Open 2015")
    addPlayer2Tournament(ids[9],tid)
    addPlayer2Tournament(ids[10],tid)
    addPlayer2Tournament(ids[11],tid)
    addPlayer2Tournament(ids[12],tid)
    addPlayer2Tournament(ids[13],tid)
    
    # Testing before matches are played
    standings = playerStandings(tid)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "testPairingsOdd failed ...."
            "For five players, swissPairings should return two pairs.")
    
    # Testing after matches have been played
    reportMatch(tid,id1, id2)
    reportMatch(tid,id3, id4)
    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "testPairingsOdd failed ...."
            "For five players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id4, id5]), frozenset([id1, id3])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "testPairingsOdd failed ...."
            "After one round, the player that did not play in it " 
            "should be paired .")
    print "testPairingsOdd passed ...."
     
if __name__ == '__main__':
    ids = testRegistration()
    testTournament()
    testTournamentPlayers(ids)
    testStandingsBeforeMatches(ids)
    testReportMatches(ids)
    testPairingsEven(ids)
    testPairingsOdd(ids)
    print "All unit tests passed ...."