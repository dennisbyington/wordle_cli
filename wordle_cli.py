#!/usr/bin/env python3
"""
Dennis Byington
dennisbyington@mac.com
12 May 2022
Wordle CLI clone
"""

import argparse
import sys
import json
from datetime import datetime


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(description='wordle clone',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    return parser.parse_args()


# --------------------------------------------------
class Guess():
    """class to hold guess guess & letter colors"""

    def __init__(self, guess):
        self.guess = guess
        self.colors = ['', '', '', '', '']


# --------------------------------------------------
def main():
    """main fuction"""

    # get command line args
    args = get_args()

    # game setup / settings
    num_guesses = 6         
    guesses = []            # list of Guess classes
    keyboard = dict.fromkeys(list('abcdefghijklmnopqrstuvwxyxz'))
    
    # load stats
    try:
        with open('data_files/stats.txt', 'r') as f:
            stats = json.load(f)
    # if no-file and/or invalid-json error
    except (FileNotFoundError, json.decoder.JSONDecodeError) as error:
        # log error and re-init stats
        with open('data_files/error-log.txt', "a") as f:  
            date = datetime.now().strftime("%d-%b-%Y")  
            f.write(f'{date}\nstats error: {str(error)}\n\n')
            stats = {"tot_games_played": 0, 
                     "tot_games_won": 0, 
                     "win_percent": 0, 
                     "current_streak": 0, 
                     "max_streak": 0, 
                     "guess_distro": [0, 0, 0, 0, 0, 0], 
                     "word_tracker": 0}

    # load answers and allowed words
    all_answers = []
    with open('data_files/all_answers.txt', 'r') as f:
        for line in f:
            all_answers.append(line.rstrip())

    allowed_words = []
    with open('data_files/allowed_words.txt', 'r') as f:
        for line in f:
            allowed_words.append(line.rstrip())

    # pick answer from all_answers (word_tracker is index)
    answer = all_answers[stats['word_tracker']]
    
    # inc tracker# if > 2315, reset tracker      
    stats['word_tracker'] += 1
    if stats['word_tracker'] > 2314:
        stats['word_tracker'] = 0       

    # run game
    while (True):   
        # display current game board & keyboard
        display_board(guesses, keyboard)   

        # get guess & decrement turns left
        guess, num_guesses = get_guess(guesses, num_guesses, all_answers, allowed_words)

        # get colors for letters
        update_letters(guesses, keyboard, answer)

        # check for winning guess
        check_win(guess, answer, guesses, keyboard, stats)

        # check turns remaining
        check_turns(num_guesses, guesses, keyboard, answer, stats)


# --------------------------------------------------
def display_board(guesses, keyboard):
    """displays game board and keyboard to terminal"""
    
    qwerty = 'q w e r t y u i o p\n a s d f g h j k l\n  z x c v b n m\n'
    ansi_canx = '\033[0;0m'             # ansi code to stop color printing
    ansi_clear = '\033c'                # ansi code to clear terminal

    # display game board with guesses and/or blank lines
    print(ansi_clear, end="")           # clear terminal           
    print(f'\n    *********')
    # loop 6 times
    #   if guess (1, 2...) available: print letters with color
    #   else: print filler lines
    for i in range(0, 6):
        if i < len(guesses):
            print('    * ', end='')
            # for each letter in current guess:
            # get ansi code from guess.colors[] and print in color
            for j, letter in enumerate(guesses[i].guess):
                print(f'{guesses[i].colors[j]}{letter}{ansi_canx}', end='')
            print(f' *')
        else:
            print(f'    * ----- *')
    print(f'    *********')

    # display keyboard
    for char in qwerty:
        # if alpha and color set: print with color; else: print default color
        if (char in keyboard) and (keyboard[char]):
            print(f'{keyboard[char]}{char}{ansi_canx}', end='')
        else: 
            print(f'{char}', end='')


# --------------------------------------------------
def get_guess(guesses, num_guesses, all_answers, allowed_words):
    """accept guess, save it, decrement turns left / returns guess"""

    # get & validate guess
    while(True):
        
        guess = input('Enter your guess: ').lower() 

        # if not 5 alpha-chars: get new word
        if (not guess.isalpha()) or (len(guess) != 5):
            print(f'Enter only 5 letter words')
            # break
            continue

        # if not in either list: get new word
        elif (guess not in all_answers) and (guess not in allowed_words):
            print('Error: unrecognized word')
            continue
        
        # if here, have god work: break loop
        else:
            break

    # save guess, decrement turns remaining
    new_guess = Guess(guess)
    guesses.append(new_guess)
    num_guesses -= 1

    return guess, num_guesses
    

# --------------------------------------------------
def update_letters(guesses, keyboard, answer_in):
    """colors letters (green, yellow, black)
    -------------------------------------------------------
    Dupe detection example: 
    
    1) 1st loop through guess:
        if in correct spot
            color green
            replace with * in both guess and answer

    2) 2nd loop through guess:
        if *, skip
        elif in word (this means it is in wrong spot b/c not green already)
            color yellow
            remove from answer (no need to alter guess at this point)
        else
            color black
    """

    # ansi color codes (backgrounds)
    green = '\033[48;5;22m'
    yellow = '\033[48;5;100m'
    black = '\033[48;5;232m'    

    # for indexing (0 -> 6 guesses)
    num_guess = len(guesses) - 1

    # retrive current guess & colors (list for mutability)
    # guess = guesses[num_guess].guess       
    guess = list(guesses[num_guess].guess)               
    colors = guesses[num_guess].colors      
    answer = list(answer_in)
    
    # dupe detection (1st pass: green)
    # if same letter in position: color letters green & remove 
    # for letter in guess:
    for i, letter in enumerate(guess):
        # if letter in right spot
        if guess[i] == answer[i]:
            # color green
            colors[i] = green
            # remove letter (from both)
            answer[i] = '*'
            guess[i] = '*'
            
    # dupe detection (2nd pass: yellow & black)
    # if letter in wrong position: color letter yellow & remove from answer
    # for letter in guess:
    for i, letter in enumerate(guess):
        # if already green, skip
        if letter == '*': 
            continue
        # elif letter in answer (but in worng spot):
        elif letter in answer:
            # color yellow
            colors[i] = yellow
            # remove letter (from answer)
            answer.remove(letter)
        # else: # color black
        else:
            colors[i] = black

    # re-init vars for keyboard update
    guess = list(guesses[num_guess].guess)
    answer = list(answer_in)

    # update the keyboard colors
    # note: never downgrades (g->y or y->b), but can upgrade (y->g)
    for i, letter in enumerate(guess):
        # if not set and not in answer -> black
        if letter not in answer:
            keyboard[letter] = black
        # if not set and in right spot -> green
        elif letter == answer[i]:
            keyboard[letter] = green
        # if in answer and 'green' -> yellow
        elif (letter in answer) and (keyboard[letter] != green):
            keyboard[letter] = yellow


# --------------------------------------------------
def check_win(guess, answer, guesses, keyboard, stats):
    """checks for winning word"""

    if guess == answer:
        
        display_board(guesses, keyboard)
        print('*******************')                         
        print('*You are a winner!*')                         
        print('*******************')  
        
        # update & display stats 
        update_stats_win(stats, guesses)
        print(f'Games played: \t{stats["tot_games_played"]}')
        print(f'Win %: \t\t{stats["win_percent"]}')
        print(f'Current streak: {stats["current_streak"]}')
        print(f'Max streak: \t{stats["max_streak"]}')
        print(f'Guess distribution:')
        print(f'1\t2\t3\t4\t5\t6')
        for value in (stats["guess_distro"]):
            print(f'{value}\t', end="")
        print('')
        
        sys.exit()


# --------------------------------------------------
def check_turns(num_guesses, guesses, keyboard, answer, stats):
    """checks turns remaining"""

    if num_guesses <= 0: 
        display_board(guesses, keyboard)
        print('*******************')
        print('* No guesses left *')
        print('*  Correct word:  *')
        print(f'****   {answer}   ****')
        print('*******************')

        # update & display stats 
        update_stats_lose(stats, guesses)
        print(f'Games played: \t{stats["tot_games_played"]}')
        print(f'Win %: \t\t{stats["win_percent"]}')
        print(f'Current streak: {stats["current_streak"]}')
        print(f'Max streak: \t{stats["max_streak"]}')
        print(f'Guess distribution:')
        print(f'1\t2\t3\t4\t5\t6')
        for value in (stats["guess_distro"]):
            print(f'{value}\t', end="")
        print('')
        
        sys.exit()


# --------------------------------------------------
def update_stats_win(stats, guesses):
    """update stats after win"""

    # stats = {'tot_games_played': 242, 
        # 'tot_games_won': 101,
        # 'win_percent': 98,
        # 'current_streak': 22,
        # 'max_streak': 22,
        # 'guess_distro': [0, 2, 6, 6, 4, 4],
        # 'word_tracker': 5}

    # increment games played
    stats['tot_games_played'] += 1
    
    # increment games won
    stats['tot_games_won'] += 1

    # update win %: (tot_won/tot_played * 100) rounded
    stats['win_percent'] = round(stats['tot_games_won'] / stats['tot_games_played'] * 100)
    
    # check max streak and inc
    if stats['max_streak'] == stats['current_streak']:
        stats['max_streak'] += 1

    # inc current streak
    stats['current_streak'] += 1

    # update guess distro (guess index: len(guesses) - 1)
    stats['guess_distro'][len(guesses) - 1] += 1

    # save stats
    with open('data_files/stats.txt', 'w') as f:
        json.dump(stats, f)

    return(stats)


# --------------------------------------------------
def update_stats_lose(stats, guesses):
    """update stats after lose"""

    # stats = {'tot_games_played': 242, 
        # 'tot_games_won': 101,
        # 'win_percent': 98,
        # 'current_streak': 22,
        # 'max_streak': 22,
        # 'guess_distro': [0, 2, 6, 6, 4, 4],
        # 'word_tracker': 5}

    # increment games played
    stats['tot_games_played'] += 1
    
    # update win %: (tot_won/tot_played * 100) rounded
    stats['win_percent'] = round(stats['tot_games_won'] / stats['tot_games_played'] * 100)
    
    # reset current streak
    stats['current_streak'] = 0

    # save stats
    with open('data_files/stats.txt', 'w') as f:
        json.dump(stats, f)

    return(stats)


# --------------------------------------------------
def _reset_stats(stats):
    """reset stats (debugging method)"""

    # stats = {'tot_games_played': 242, 
        # 'tot_games_won': 101,
        # 'win_percent': 98,
        # 'current_streak': 22,
        # 'max_streak': 22,
        # 'guess_distro': [0, 2, 6, 6, 4, 4],
        # 'word_tracker': 5}

    # reset games played
    stats['tot_games_played'] = 0
    
    # reset games won
    stats['tot_games_won'] = 0

    # reset win %: 
    stats['win_percent'] = 0
    
    # reset current streak
    stats['current_streak'] = 0

    # reset max streak
    stats['max_streak'] = 0

    # reset current streak
    stats['current_streak'] = 0

    # reset guess distro 
    stats['guess_distro'] = [0, 0, 0, 0, 0, 0]

    # reset word tracker
    stats['word_tracker'] = 0    


# --------------------------------------------------
if __name__ == '__main__':
    main()
