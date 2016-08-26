import os
from random import randrange

guess_number = randrange(100)

try_number = -1

continue_game = True

while continue_game:

    try_number = -1

    while try_number < 0 or try_number > 100:

        try_number = input("Vous devinez un nombre entre 0 et 100, tapez un nombre : ")

        try:
            try_number = int(try_number)
        except ValueError:
            print("Vous n'avez pas saisi de nombre")
            try_number = -1
            continue
        if try_number < 0:
            print("Ce nombre est négatif")
        if try_number > 100:
            print("Ce nombre est supérieur à 49")

    if try_number < guess_number:
        print ("C'est plus !")
    elif try_number > guess_number:
        print ("C'est moins !")
    else:
        print("Bien joué !")
        choice = input("Voulez-vous continuer à jouer ? o/n : ")
        
        continue_game = False

os.system("pause")
        

