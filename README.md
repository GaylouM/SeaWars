Sea Wars verion 1.0 25/08/2016

# HOW TO PLAY

Sea Wars is an extended version of the original two players game Battleship.

- First player create a game in createTwoplayersGame endpoint
- Second Player get the webSafeGameKey in getGamesCreated endpoint
- Second Player register with the webSafeGameKey in registerForGame endpoint,
an active player is randomly picked
- The active player must guess a row and column on the board to find a boat in
guess endpoint
- If a boat is hit the player continue else active player changes.
- The game continues until one of the two players get rid of all the adversary ship

## DETAILED DESCRIPTION

What does Sea Wars different from Battleship ?

- The first player decide the size of the board and the set of boats for the two players
Exemple: 10 for the board size will define a standard square board of 10x10,
[5,4,3,3,2] for the board setup will create 1 Aircraft Carrier,
1 Battleship, 2 Cruiser and 1 Destroyer
- The first player can potentially set everything he wants 
but he must be carefull of the amount of money available in his wallet.
- Even if it's not implemented yet the second player could in a future version
set his own set of boat, this is why the wallet exists.
- The amount of money available in the wallet at the beginnig of the game
is proportionnal to the size of the board (100€ for a 10x10 board, 121€ for 11x11 board and 625€ for a 25x25)

## GENERAL USAGE NOTES

- For the process of random generation of board, I decided to define a recursive function.
The function as I designed it work pretty much the same way than the flood fill algorithm
with the difference that the flood fill stops when the condition are reached (straight size of the boat essentially).
It does the job for a little amount of boat of short size (less than 25 box).
Given that the first player should be reasonnable during the setting step.
Indeed, I decided to not prevent the creation of a large amount of big boat,
assuming it could eventually raise an Exception RuntimeError: 'maximum recursion depth exceeded'. So please be carefull.

- In a future reflexion I'd like to implement a push queue in order to always have a set of board instantly available
to shorten the setting step. The board won't be generated anymore but just got in the datastore.

- If you decide to execute createTwoplayersGame endpoints without insert any board size or board setup, default values will be token.

## INSTALLATION

First you need to fork the API and clone it locally

- Open Google App Engine Launcher
- Go in File --> Add existing application...
- Browse the Sea Wars folder
- Choose Port: 8080, Admin Port: 8000 and click Add
- Create then a shortcut with this target
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080 - automatic!
(Change the first part if it's necessary)
- Execute the shortcut as administrator and browse this url:
http://localhost:8080/_ah/api/explorer to start using the api - automatic!
- To use it on internet just deploy it in google app engine Launcher
