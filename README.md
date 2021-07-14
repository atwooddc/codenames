# 'Codenames' clue generator prototype

## Background
Based off of the popular boardgame _'Codenames'_, this program constructs a database of 'relatednesses' between words and 
plays a rudimentary, one-team version of Codenames. 

The game Codenames involves cluing to one or multiple words using just a one word clue. There are two teams, each 
assigned 8 or 9 unqiue words that they have to guess to win the game. Each team has a codemaster, who take turns 
cluing their respective teams to guess their words using just one word clues. The key is to give clues that relate
strongly to many of your team's words and that don't relate strongly to the words on the board that aren't yours. 
At its core, it is a word association game. 

## Overview
Using the [ConceptNet API](https://github.com/commonsense/conceptnet5/wiki/API) and the sqlite3 package, I built a database of related words and their 'relatednesses' for 25 words from the Codenames wordset (the minimum 
number you need to play a game). The database I built can be found in the file 'codenames.db', and the code to build a similar database is found in 'database_construction.py'

From this database, I developed a simplified version of Codenames, where there is one team, and the computer prompts 
the user with a clue to one single word -- in the real Codenames, there are two competing teams, each with their own codemaster, and each one word clue is given with a number that corresponds how many words it is cluing to. 

## Issues/Shortcomings
###OOP
The use of global variables and the lack of defined classes makes scaling up this program as is difficult. This project was 
more about the backend side of things and getting my feet wet with SQL than anything else. If I come back to this project, 
my first step will be to make the game its own class, with the global variables turned into member variables. 

###Database injection
Because this is my first exposure to SQL, there is some sketchy syntax in the SQL calls that are vulnerable to injection
attacks. This isn't a safety critical system and none of the strings that go into the SQL calls are entered by the user, 
so I decided to let that aspect of the project take a backseat. 

## Future Directions
### More codenames
It was clear to me pretty early on that this database was going to have to be massive to capture every single 
relationship between the 400 words in the Codenames wordset and however many related words I wanted to keep track of for each. Every codename added to the database grows the database in both 
the X and Y directions, which gets unwieldy really fast. Because the rate limit of the ConceptNet API is relatively slow, 
I decided to just stick with 25 words. But a future iteration of this project could add more codenames to vary the 
relations each game. Even just 10 more names would make playing multiple games less repetitive. 

### Multi-word clues
The most fun part of Codenames to me is coming up with clues that connect to multiple words -- plus, it's pretty hard to win 
a game of codenames only giving clues that relate to one word. I would have to develop some weighting for multiword clues 
that balances the risk/reward that comes with giving one. And then the issue becomes keeping track of the 'history' of 
which words have contributed to each words score as words are guessed and removed from the board, and should no longer 
penalize/boost each possible clue's score. 

### Computer guesser
A much easier addition would be a computer guesser mode, where the player acts as codemaster. This would potentially 
take much longer to play, because it would require a considerable number of calls to the ConceptNet API during each 
turn as the computer compares the 25 relatednesses. 

## Wrap-up
This project was rewarding, and it definitely made me reflect on and appreciate the innate ability of the human 
brain to draw quick connections between seemingly unrelated things. The human-computer interaction in this program is also interesting. 
The computer is drawing from a graph of words [developed from thousands and thousands of datapoints](https://conceptnet.io/#:~:text=Our%20data%20comes%20from%20many%20different%20sources%2C%20some%20of%20which%20you%20can%20contribute%20to%20and%20improve%20not%20just%20the%20state%20of%20computational%20knowledge%2C%20but%20of%20human%20knowledge.)
that are so different from a human's frame of reference. This is obvious from the obscure and outdated(?) clues that 
the computer sometimes gives ("usurer" for shark, "micropachycephalosaurus" for dinosaur, "calumet" for pipe, etc.). But for 
the most part, the computer's clues are straightforward and strongly linked to the intended word. 

##

by David Atwood

This work includes data from ConceptNet 5, which was compiled by the Commonsense Computing Initiative. ConceptNet 5 is freely available under the Creative Commons Attribution-ShareAlike license (CC BY SA 4.0) from http://conceptnet.io. The included data was created by contributors to Commonsense Computing projects, contributors to Wikimedia projects, Games with a Purpose, Princeton University's WordNet, DBPedia, OpenCyc, and Umbel.

