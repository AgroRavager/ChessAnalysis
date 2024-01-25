# Shaurya Jeloka
# 1/23/2024

# This program creates the command-line interface for the sudoku game using 
# the argparse package and defines the code for running the game. This program 
# imports the sudoku_funcs module and relies heavily on the functions defined 
# in sudoku_funcs.py to run the sudoku game. This program uses while loops, 
# conditional statements, user inputs, lists, and parsers to perform its objectives. 

import argparse
import sudoku_funcs as funcs
import copy

# Define play_sudoku() function for main sudoku game
def play_sudoku(puzzle):
    # Create a deepcopy of the puzzle and solve it so the original remains 
    # unchanged but a copy of the solution is saved
    solution = copy.deepcopy(puzzle)
    funcs.solve_puzzle(solution)

    # Begin infinite loop for game
    while True:

        # Print current puzzle using print_puzzle function and give user options
        # at the beginning of each turn
        print()
        funcs.print_puzzle(puzzle)
        user_input = input("Enter your guess as 'row col num' or type 'hint' or 'solve': ")

        # Enter this conditional if user asks for a hint
        if user_input.lower() == 'hint':
            # Ask for the row and column to reveal the solution for
            row, col = map(int, input("Enter the row and column you would like the value for: ")
                      .split())

            # Subtract one from each user value because list uses zero-based indexing
            row -= 1
            col -= 1
            sol_num = solution[row][col]

            # Print solution and modify puzzle in place
            print(f"the number at ({row}, {col}) is {sol_num}")
            puzzle[row][col] = sol_num

        # Enter this conditional if user asks for the solution
        elif user_input.lower() == 'solve':
            # Print solution, end game
            funcs.print_puzzle(solution)
            break
        
        # Enter this conditional if user tries to guess a value
        else:
            # Split input into separate variables and subtract one to align with 
            # zero-based indexing
            row, col, num = map(int, user_input.split())
            row -= 1
            col -= 1
            
            # If solution is correct, inform user and modify puzzle
            if solution[row][col] == num:
                print("Correct! Great job!")
                puzzle[row][col] = solution[row][col]

            # If solution is incorrect, inform user and leave puzzle unchanged
            else: 
                print("Sorry, your guess is incorrect. Please try again")
        
        # If the puzzle has been filled, end the game
        if puzzle == solution:
            break
    print('The game has ended. Thank you for playing!')

# Only run this block of code if this script is the main program and not imported 
if __name__ == "__main__":
    # Create new parser and add --play argument to start the game
    parser = argparse.ArgumentParser(description="Sudoku Game")

    # If user specfies --play, 'action=store_true' will set 'args.play' to True
    parser.add_argument('--play', action='store_true', help='Play the Sudoku game')

    # Parse the command line arguments and store them in 'args'
    args = parser.parse_args()

    # If the '--play' argument is provided, scrape a puzzle from the web and 
    # begin the sudoku game 
    if args.play:
        puzzle = funcs.get_puzzle()
        play_sudoku(puzzle)

    # If '--play' is not provided, display the help message
    else:
        parser.print_help()