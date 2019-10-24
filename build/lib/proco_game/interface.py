'''
this is the interface for game
'''

from collections import Counter
from .constants import *
from .simulation import *

print("Some games never finish.")

def menu():
    print("What would you like to do?")
    print("\t\tH : help and info\n\t\tC : create game")

    choice = input("[] Your response :\t")

    if choice.lower() == 'h':
        print("-------------------------------------------------------------------------------")
        print("\n* You have a choice to be a consumer or a spectator to a smart consumer (AI).")
        print("~ If you choose to be a consumer, you have to choose what kind of consumer you want to be.")
        print("* GREED determines how much you want to spend per round, higher greed higher spend.")
        print("~ FOCUS determines how much of your wealth you want to invest in your possessions, higher focus higher investment.")
        print("* SPEND determines how much you are willing to pay for some product, higher spend higher the expense.")
        print("~ INVEST determines the degree of wealth you want to put into each possession, higher invest more money sunk into possessions.\n")
        print("-------------------------------------------------------------------------------")
    elif choice.lower() == 'c':
        return

    else:
        menu()

def show_scoreboard(s):

    print("\t* {} : {}".format('CONSUMER', s['CONSUMER']))
    print("\t* {} : {}".format('PRODUCER', s['PRODUCER']))
    print("\t* {} : {}".format('NONE', s[None]))



# for smart consumer
SCOREBOARD = Counter({'CONSUMER' : 0, 'PRODUCER' : 0, None : 0})

# for you
SCOREBOARD2 = Counter({'CONSUMER' : 0, 'PRODUCER' : 0, None : 0})


'''
description :
- main method to program, runs games where you could be a Consumer or a spectator.

arguments :
- s1 : dict, scoreboard for smart consumer
- s2 : dict, scoreboard for you
'''
def play_game(s1 = SCOREBOARD, s2 = SCOREBOARD2):

    print("HELLO PLAYER")
    menu()

    c = None

    while True:
        choice = input("WHAT WOULD YOU LIKE TO BE??\nconsumer C spectator S quitter Q?\t[]\t")

        if choice.lower() == 'q':
            print('----------------------------------------------')
            print("YOUR PERFORMANCE\n")
            show_scoreboard(s2)
            print("\nSMART CONSUMER PERFORMANCE\n")
            show_scoreboard(s2)
            print('\n----------------------------------------------')
            return
        if choice.lower() == 'c':
            print("You chose to be a consumer!")
            print('\nChoose what kind of consumer you want to be!')

            G, F, S, I = 0, 0, 0, 0

            while True:
                G = input("* Enter your GREED (number between 0 and 1) :\t")
                try:
                    G = float(G)
                    if G < 0: continue
                    if G > 1: continue

                    break
                except:
                    pass

            while True:
                F = input("* Enter your FOCUS (number between 0 and 1) :\t")
                try:
                    F = float(F)
                    if F < 0: continue
                    if F > 1: continue

                    break
                except:
                    pass

            while True:
                S = input("* Enter your SPEND (number greater than 0) :\t")
                try:
                    S = float(S)
                    if S < 0: continue

                    break
                except:
                    pass

            while True:
                I = input("* Enter your INVEST (number greater than 0) :\t")
                try:
                    I = float(I)
                    if I < 0: continue

                    break
                except:
                    pass

            w = random.uniform(10** 3.5, 10 ** 6.5)
            print('\n----------------------------------------------')
            print("You have been assigned wealth of {}".format(w))
            c = Consumer(w)
            break

        elif choice.lower() == 's':
            c = 'SMART'
            break

    numRounds = None
    while True:
        numRounds = input("How many matches do you want ?\t")

        try :
            numRounds = int(numRounds)
            break
        except:
            pass

    print("------------------- LET'S PLAY -----------------")
    if c == 'SMART':
        score = test_smart_consumer(c = None, n = numRounds)
        s1['CONSUMER'] = s1['CONSUMER'] + score['CONSUMER']
        s1['PRODUCER'] = s1['PRODUCER'] + score['PRODUCER']
        s1[None] = s1[None] + score[None]

        print("\n------------- SMART CONSUMER RUNNING TOTAL-------------\n\n")
        show_scoreboard(s1)
        print("\n\n------------------- END PLAY -----------------")

    else:
        score = test_smart_consumer(c, n = numRounds)

        s2['CONSUMER'] = s2['CONSUMER'] + score['CONSUMER']
        s2['PRODUCER'] = s2['PRODUCER'] + score['PRODUCER']
        s2[None] = s2[None] + score[None]

        print("\n------------- YOUR RUNNING TOTAL-------------\n\n")
        show_scoreboard(s2)
        print("\n\n------------------- END PLAY -----------------")

    print("Play more?")
    while True:
        choice = input("Y or N :\t")
        if choice.lower() == 'y':
            print("------------------------------------\n\n")
            play_game(s1, s2)
            return
        elif choice.lower() == 'n':
            print('----------------------------------------------')
            print("YOUR PERFORMANCE\n")
            show_scoreboard(s2)
            print("\nSMART CONSUMER PERFORMANCE\n")
            show_scoreboard(s1)
            print('----------------------------------------------')
            return
