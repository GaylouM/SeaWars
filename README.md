SEAWARS
1.0 3/28/2018

HOW TO PLAY
-----------

Sea Wars is an extended version of the original two players game Battleship.

1. First player create a game in createTwoplayersGame endpoint
2. Second Player get the webSafeGameKey in getGamesCreated endpoint
3. Second Player register with the webSafeGameKey in registerForGame endpoint,
an active player is randomly picked
4. The active player must guess a row and column on the board to find a boat in
guess endpoint
5. If a boat is hit the player continue else active player changes.
6. The game continues until one of the two players get rid of all the adversary ship

## DETAILED DESCRIPTION

What makes Sea Wars different from Battleship?

- The first player decides the size of the board and the set of boats for the two players
Example: 10 for the board size will define a standard square board of 10x10,
[5,4,3,3,2] for the board setup will create 1 Aircraft Carrier,
1 Battleship, 2 Cruiser, and 1 Destroyer
- The first player can potentially set everything he wants
however, he must be careful of the amount of money available in his wallet.
- Even if it's not implemented yet, the second player could in a future version
set his own set of boats, this is why the wallet exists.
- The amount of money available in the wallet at the beginning of the game
is proportional to the size of the board (100€ for a 10x10 board, 121€ for 11x11 board and 625€ for a 25x25)

## INSTALLATION

First, you need to fork the API and clone it locally.

1. Open Google App Engine Launcher
2. Go in File --> Add existing application...
3. Browse the Sea Wars folder
4. Choose Port: 8080, Admin Port: 8000 and click Add
5. Create then a shortcut with this target
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
(Change the first part if it's necessary)
6. Execute the shortcut as administrator and browse this url:
http://localhost:8080/_ah/api/explorer to start using the API.
7. To use it on the internet deploy it in google app engine Launcher

## ENDPOINTS

- getProfile
	- Path: 'seawars/v2/getProfile'
	- Method: GET
	- Parameters: none
	- Returns: ProfileForm with current profile state.
	- Description: Return information about the current user

- saveProfile
	- Path: 'seawars/v2/saveProfile'
	- Method: POST
	- Parameters: displayName
	- Returns: ProfileForm with current profile state.
	- Description: Change user displayName, commit it in the datastore and return updated pieces of information about him.

- createTwoplayersGame
	- Path: 'seawars/v2/newGame'
	- Method: POST
	- Parameters: boardSetup, boardSize
	- Returns: GameForm with the current game state.
	- Description: Takes as input a board setup and a board size and add a game instance to the datastore with a set of ships for the first player. If no input data are provided default data are taken.

- getGamesCreated
	- Path: 'seawars/v2/gamesCreated'
	- Method: GET
	- Parameters: none
	- Returns: GameForms with current game state.
	- Description: Takes no input and return all the pieces of information about all games created.

- getGame
	- Path: 'seawars/v2/game/{websafeGameKey}'
	- Method: GET
	- Parameters: websafeGameKey
	- Returns: GameForm with the current game state.
	- Description: Takes as input a websafegamekey and return all the pieces of information about a game.

- getUserGames
	- Path: 'seawars/v2/userGames'
	- Method: GET
	- Parameters: none
	- Returns: GameForm with current user games state.
	- Description: Takes no input and return all the pieces of information about the user games.

- getGameHistory
	- Path: 'seawars/v2/gameHistory/{websafeGameKey}'
	- Method: GET
	- Parameters: websafeGameKey
	- Returns: GameForm with current game history.
	- Description: Takes as input a websafegamekey and return the history of the guess made by each player from the beginning of the game. firstPlayerC is a list of number designate one of the two coordinate needed to hit a ship (Column) and firstPlayerR designate the second one (row). The first guess can be represented as follow: [firstPlayerR[0],firstPlayerC[0]].

- getPlayersRanking
	- Path: 'seawars/v2/playersRanking'
	- Method: GET
	- Parameters: no
	- Returns: RankingForms with the rank of all players.
	- Description: Takes no input and return a list of all the players with their score. The ranking is a number going from 0 to 1000.
The rank is calculated as the winning percentage weighted by 0.9 and multiply by 1000 which is then divided by something close to the percentage of guesses to win but weighted by the total number of ship box of the game.

- guess
	- Path: 'seawars/v2/game/{websafeGameKey}/guess'
	- Method: PUT
	- Parameters: websafeGameKey, Column, Row
	- Returns: GuessEval with game state and history for both players.
	- Description: Takes as input the coordinates the active player wants to play. These coordinates are represented by a row and a column number. Return the evaluation of the attempt which is a string with value "Missed", "Hit", "Hit and sunk" or "Hit and sunk. You've won the game"

- registerForGame
	- Path: 'game/{websafeGameKey}/registration'
	- Method: PUT
	- Parameters: websafeGameKey
	- Returns: RegisteringForm with confirmation of registration and activePlayerId.
	- Description: Takes as input a websafegamekey and append this key to the current user profile. Add one to the numberOfGame argument. Return True if successful, False otherwise.

- cancelGame
	- Path: 'game/{websafeGameKey}/cancel'
	- Method: PUT
	- Parameters: websafeGameKey
	- Returns: RegisteringForm with confirmation of cancelling.
	- Description: Takes as input a websafegamekey and remove it in the current user profile. Add "Canceled" to the gameState argument Return True if successful, False otherwise.

## SCORE KEEPING

The profile object stores 4 useful data; the number of played games, the number of won games, the number of guesses for each victory and the number of ship boxes the player had to find for each game he won, for example: [5,4,3,3,2] give 17 boxes.

For each game, the player wins or lose the game.
If the player wins, +1 is added to the Profile.numberOfWonGames.
This allows us to calculate a first simple ratio by dividing the Profile.numberOfWonGames by Profile.numberOfGames.
This simple ranking can be improved if we consider the number of guesses to victory for each game. Because each game can be set differently with a different amount of ship of different sizes, the number of guesses to victory needs to be weighted by the number of ship boxes on the board.
To do so, we are dividing Profile.numberOfGuess by Profile.numberOfShipBox. The result can't be less than 1 as the number of guesses can't be less than the number of ship box. If the ratio is equal to 1 the previous simple ranking is divided by 0,9, equal 2 it is divided by 1, superior or equal to 3 divided by 1.1. To get all the intermediate values, we are using the following expression; y = 0.1x + 0.8

Reflection: We could imagine saving all the player's data in a unique model.
Indeed, with this data and some math, we could find the scalable expression of the function above. We could, for example, save the number of guess of all the winners with the number of boxes he had to hit to win the game. Whit this big table we could take the most significant ratio (ratio=number of guess/number of boxes), the smallest one and with all the sorted values calculate the median value.
Finally, we could take (x1=min(list), y1 = 0,9), (x2=median(list), y2 = 1), (x3=max(list), y3 = 1,1) and we this 3 couples of value determine thanks to a linear regression the expression of the curve crossing this points (ax²+bx+c) finding a, b and c in this example. To not solicit too much the datastore we could wait for 10 entries before refreshing the expression.

![Illustration 1](https://github.com/GaylouM/SeaWars/blob/master/image1.jpg)
![Illustration 2](https://github.com/GaylouM/SeaWars/blob/master/image2.jpg)
