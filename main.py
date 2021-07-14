import sqlite3
from sqlite3 import Error
import random

import numpy as np
import time

# methods for interacting with SQLite database
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        # print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# list of codenames words, in order of position in database
names = ['soul', 'shark', 'knife', 'trip', 'watch', 'hospital', 'green', 'smuggler', 'ice', 'racket', 'band',
         'millionaire', 'pitch', 'bow', 'lock', 'dinosaur', 'car', 'pole', 'horseshoe', 'fire', 'cliff', 'pipe',
         'leprechaun', 'knight', 'drill']

# global variables that hold game information
PLAYER_TEAM = []
COMP_TEAM = []
BYSTANDERS = []
ASSASSIN = ""

NUM_BOARD = []
WORD_BOARD = []

SCORE_LIST = []

# main play method
def play():
    welcome()
    setBoard()
    startGame()
    setWeights()
    while PLAYER_TEAM and ASSASSIN:
        turn()
    print("YOU WIN!") if not PLAYER_TEAM else print("YOU LOSE :(")


# intro
def welcome():
    ans = str(input("Welcome to Codenames!\nTo play, press \"p\"\n"))
    while ans != "p":
        ans = str(input("Sorry, I don't know what you mean.\nTo play, press \"p\"\n"))
    print("Currently, you can only play as the guesser. The computer will be the codemaster for your team.")

# create board, split up words randomly between teams
def setBoard():
    print("Shuffling cards...")
    numList = list(range(1, 26))
    random.shuffle(numList)
    nList = numList.copy()
    npArray = np.array(nList)
    global NUM_BOARD
    NUM_BOARD = npArray.reshape((5,5))

    # baord stored in numpy array
    global WORD_BOARD
    WORD_BOARD = np.array([names[nList[i] - 1] for i in range(25)]).reshape((5, 5))

    # select indexes of words to be on first team (9 words), second team (8 words), assassin, remainder are bystanders
    global PLAYER_TEAM
    PLAYER_TEAM = []
    p = 9
    for i in range(p):
        ind = random.randint(0, len(numList) - 1)
        PLAYER_TEAM.append(numList.pop(ind))
    PLAYER_TEAM.sort()

    global COMP_TEAM
    COMP_TEAM = []
    c = 8
    for i in range(c):
        ind = random.randint(0, len(numList) - 1)
        COMP_TEAM.append(numList.pop(ind))
    COMP_TEAM.sort()

    global ASSASSIN
    ASSASSIN = numList.pop(random.randint(0, len(numList) - 1))

    global BYSTANDERS
    BYSTANDERS = numList
    # need a quick way to switch between numbers (indexes in SQL table) and words themselves
    # correspWords = [names[i-1] for i in correspNums]
    # correspNums = [(names.index(n)+1) for n in correspWords]

# starts game
def startGame():
    print("The board for this game:\n\n", WORD_BOARD, "\n\nThe computer will prompt you with a one-word clue that "
                                                      "corresponds to one word on the board.\nEnter your guess when prompted.")
    ans = str(input("Enter \"p\" when you're ready to start playing!\n"))
    while ans.lower() != "p":
        ans = str(input("Enter \"p\" when you're ready to start playing!\n"))

# calculates "scores" for each possible clue stored in the database related to the codenames on the player's team.
# score gets a slight penalty when the word is related to a bystander, a moderate penalty when related to a codename
# belonging to the other team, and a large penalty when related to the assassin.
def setWeights():
    global PLAYER_TEAM
    global COMP_TEAM
    global BYSTANDERS

    con = create_connection("/Users/davidatwood/Documents/compsci/petprojects/codenames2.db")
    cur = con.cursor()

    global SCORE_LIST
    SCORE_LIST = {}
    for ind in PLAYER_TEAM:
        i = str(ind)
        cur.execute("SELECT * FROM related WHERE name_id = '%s'" % i)
        rows = cur.fetchall()
        for row in rows:
            word = row[0]
            score = row[ind + 1]
            a_rel = row[ASSASSIN + 1]
            if a_rel < 0.3:

                # assassin
                score = score - 2 * a_rel

                # other team
                for i in COMP_TEAM:
                    score = score - row[i+1]

                # bystanders
                for i in BYSTANDERS:
                    score = score - 0.5 * row[i+1]

                SCORE_LIST[word] = score

# method repeated as player guesses
def turn():
    # finds best possible clue from SCORE_LIST
    maximum = max(SCORE_LIST.values())
    result = list(filter(lambda x: x[1] == maximum, SCORE_LIST.items()))

    # prompts user for guess
    print("The current board is :\n", WORD_BOARD)
    guess = str(input("\nThe clue is " + str(result[0]).upper() + " for 1 codename. What is your guess?\n")).lower()
    while guess not in names or (names.index(guess)+1 not in PLAYER_TEAM and names.index(guess)+1 not in COMP_TEAM and names.index(guess)+1 not in BYSTANDERS and guess != ASSASSIN):
        guess = str(input("Unfortunately that word is not currently on the board. Please enter a valid codename.\n"))
    removeCard(guess)

# removes guessed words from lists and boards and updates SCORE_LIST to undo the penalty of the just-guessed words.
def removeCard(guess):

    guess_ind = names.index(guess)+1

    global ASSASSIN
    if guess_ind == ASSASSIN:
        print("Oh no! That was the assassin.\nG A M E  O V E R")
        ASSASSIN = ''

    else:
        con = create_connection("/Users/davidatwood/Documents/compsci/petprojects/codenames2.db")
        cur = con.cursor()

        l = [str(i) for i in PLAYER_TEAM]
        s = "SELECT * FROM related WHERE name_id IN (" + ",".join(l) + ")"
        cur.execute(s)
        rows = cur.fetchall()

        if guess_ind in PLAYER_TEAM:
            # congrats, correct guess
            print("Strong work! You got it right.")
            # subtract relation with elements of table with name_id = guess_ind + 1
            for row in rows:
                if row[1] == guess_ind :
                    del SCORE_LIST[row[0]]
                else :
                    SCORE_LIST[row[0]] = SCORE_LIST[row[0]] - row[guess_ind]
            # remove from PLAYER_TEAM
            PLAYER_TEAM.remove(guess_ind)

        elif guess_ind in BYSTANDERS:
            # nice try, that's a bystander
            print("Nice try! That is a bystander.")
            # add relation*0.5
            for row in rows:
                SCORE_LIST[row[0]] = SCORE_LIST[row[0]] + 0.5*row[guess_ind]
            # remove from BYSTANDERS
            BYSTANDERS.remove(guess_ind)

        elif guess_ind in COMP_TEAM: # in COMP_TEAM
            # ah, you messed up, that's the other team's
            print("Oops! That was the other team's word.")
            # add relation
            for row in rows:
                SCORE_LIST[row[0]] = SCORE_LIST[row[0]] + row[guess_ind]
            # remove from COMP_TEAM
            COMP_TEAM.remove(guess_ind)

        # updates board and teams
        global WORD_BOARD
        c = np.where(WORD_BOARD == guess)
        r = c[0][0]
        c = c[1][0]
        WORD_BOARD[r][c] = 'X'
        NUM_BOARD[r][c] = 0

play()
