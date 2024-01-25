# Shaurya Jeloka
# 1/23/2024

# This program provides functions for multiple purposes related to my command-line interface sudoku game: 
# web scraping a sudoku puzzle from the internet using the Selenium package,validating the correctness of 
# a number in a specified cell, finding empty cells in the sudoku puzzle, solving the puzzle using a 
# recursive backtracking algorithm, and printing the puzzle in a formatted manner. Only the web scraping
# function relies on any external packages to perform its tasks. This program relies on for loops, conditional
# statements, one-dimensional and two-dimensional lists, recursion, and string manipulation to perform its tasks.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Define the function 'get_puzzle' to web scrape a Sudoku puzzle from sudoku-kingdom.com
def get_puzzle():

    # Initializing Selenium WebDriver in headless mode so there is no browser UI
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Navigate to Sudoku Kingdom website using the WebDriver
    url = "https://sudoku-kingdom.com/"
    driver.get(url)

    # Find the Sudoku puzzle grid element on the webpage
    puzzle_grid = driver.find_element(By.CLASS_NAME, "sudoku-board")

    # Retrieve all individual cell elements within the Sudoku grid
    cells = puzzle_grid.find_elements(By.CSS_SELECTOR, "div.sudoku-board-cell input")

    # Create a 2 dimensional list to store the entire puzzle and a 1 dimensional list
    # to temporarily store data for each row
    puzzle_data = []
    row_data = []

    # Iterate through each cell to extract the puzzle values
    for cell in cells:
        # Check to make sure cell doesn't contain an empty string and then 
        # convert string value to int
        if cell.get_attribute('value'):
                cell_value = int(cell.get_attribute('value'))

        # If value is an empty string, set cell value to 0
        else:
            cell_value = 0

        # Add cell value to current row
        row_data.append(cell_value)

    # If row is complete, add completed row to puzzle data and reset row_data list
        if len(row_data) == 9:
            puzzle_data.append(row_data)
            row_data = []
        
    # Close the WebDriver
    driver.quit()
    # Return 2d sudoku puzzle list
    return puzzle_data

# Define check_valid function to check if a given number can be placed at a 
# specified row and column in the Sudoku puzzle
def check_valid(puzzle, row, col, num):

    # Check for the number in the specified column
    for i in range(9):
        # If a duplicate value is found, return False
        if puzzle[i][col] == num:
            return False
        
    # # Check for the number in the specified row
    for i in range(9):
        # If a duplicate value is found, return False
        if puzzle[row][i] == num:
            return False

    # Check for the number in the 3x3 subgrid containing the specified cell
    for i in range((row // 3) * 3, ((row // 3) * 3) + 3):
        for k in range((col // 3) * 3, ((col // 3 ) * 3) + 3):
            if puzzle[i][k] == num:
                return False

    # Return True if no duplicate values are found and number is valid
    return True

# Define empty_finder function to find the first empty cell in the Sudoku puzzle
def empty_finder(puzzle):

    for row in range(9):
        for col in range(9):
            # Return location of first found cell with value of 0
            if puzzle[row][col] == 0:
                return (row, col)
            #By default, function returns None if no empty cells are found

# Define solve_puzzle function to solve the sudoku puzzle using a recursive
# backtracking algorithm
def solve_puzzle(puzzle):

    # Find the next empty cell
    empty = empty_finder(puzzle)
    if empty:
        row, col = empty

    # If no empty cells exist, puzzle is solved; exit function
    else:
        return True

    # If an empty space is found, try placing numbers 1-9 in the empty cell
    for num in range(1, 10):
        if check_valid(puzzle, row, col, num):
            
            # Plug in first valid number found 
            puzzle[row][col] = num

            # Recusrively call function again to solve remaining puzzle
            if solve_puzzle(puzzle):
                # If the puzzle is successfully solved with the current number, 
                # return True
                return True
                
            # If remaining puzzle is unsolvable with current number, reset cell 
            # to 0 and backtrack (try the next valid number)
            puzzle[row][col] = 0
                        
    # Return False in case the puzzle is unsolvable
    return False

# Define print_puzzle function to properly format and print sudoku puzzle
def print_puzzle(puzzle):

    # Print an opening horizontal divider
    print("-" * 25)

    for i, row in enumerate(puzzle):
        # Print a horizontal divider every three rows, except at the beginning
        if i % 3 == 0 and i != 0:
            print("-" * 25)

        for j, value in enumerate(row):
            # Print a vertical divider every three columns
            if j % 3 == 0:
                print("| ", end="")

            # Print the value followed by a space
            print(value if value != 0 else "0", end=" ")

            # Move to the next line after the last column
            if j == 8:
                print("|")

    # Print a closing horizontal divider
    print("-" * 25)
