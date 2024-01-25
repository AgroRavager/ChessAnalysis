# Shaurya Jeloka, Ian Jeong, Akshay Vakharia 
# 1/25/2024

# In this project, we analyzed a dataset about chess matches with the help of
# numerous data analytics packages, widgets, and visualizations. Using pandas 
# and matplotlib, we generated numerous graphs that elucidated trends on win 
# percentages between white and black, the role of ratings in match 
# characteristics, and the correlation between rating and turn numbers. We also 
# used these packages to find and visualize interesting trends about popular 
# openings. Then, we also used ipywidgets, chess, and IPython display to create
# an interactive widget where players can choose an opening, and then be 
# presented with tons of matches and statistics on it. Then, they can choose a
# match and see it simulated on a chess board. This file is the back end necessary
# to perform all of these calculations, and is imported by the front end 
# visualizer in jupyter notebook. 

import pandas as pd
import chess
import chess.svg
import IPython
from IPython.display import display, SVG, clear_output, HTML
from ipywidgets import widgets
import time
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Read games.csv dataset into pandas dataframe
games_df = pd.read_csv("games.csv")

# Define getwinners function to return percentage of time that r1 is 
# higher than r2 and winner wins the match
def getwinners(r1, r2, winner):
    # Filter the DataFrame to the matches where r1 is greater than r2
    filtered_games = games_df[games_df[r1] > games_df[r2]]

    # Calculate the percentage of games won by 'winner' in the filtered DataFrame
    percentage_won = (filtered_games['winner'] == winner).mean() * 100
    return percentage_won

# Create new avrating column that takes the average of the black rating and 
# white rating in the match
games_df['avrating'] = (games_df['white_rating'] + games_df['black_rating']) / 2

# Define bins and labels for rating groups
rating_bins = [0, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600]
rating_labels = ['0-1200', '1200-1400', '1400-1600', '1600-1800', 
         '1800-2000', '2000-2200', '2200-2400', '2400-2600']

# Define win_rate_for_color_group function to calculate win rate for a color 
# within a specified rating group
def win_rate_for_color(group, color):
    # Add new column to dataframe that places each match within its respective 
    # rating group using pd.cut() function
    games_df['rating_group'] = pd.cut(games_df['avrating'], bins = rating_bins, 
    labels = rating_labels, right = False)

    # Filter dataframe to get desired rating group and winner
    games_in_group = games_df[games_df['rating_group'] == group]
    wins = games_in_group[games_in_group['winner'] == color]

    # Calculate win percentage while avoiding a ZeroDivisionError
    if len(games_in_group) > 0:
        return len(wins) / len(games_in_group) * 100 
    else:
        return 0

# Define count_matches_in_group function to calculate the number of matches 
# in each rating group
def count_matches_in_group(group):
    return len(games_df[games_df['rating_group'] == group])

# Calculate win rates and total matches played for each group and color using a 
# for loop
win_rates = {}
for group in rating_labels:
    win_rates[group] = {
        'white_win_rate': win_rate_for_color(group, 'white'),
        'black_win_rate': win_rate_for_color(group, 'black'),
        'total_matches': count_matches_in_group(group)
    }
    
# Convert the results to a pandas DataFrame for better visualization
win_rates_df = pd.DataFrame(win_rates).T

# Create win_rate_diff column to show difference between white win rate and 
# black win rate
win_rates_df['win_rate_diff'] = (win_rates_df['white_win_rate'] - 
                                 win_rates_df['black_win_rate'])

# Reorder columns so win_rate_diff is before total_matches
win_rates_df = win_rates_df[['white_win_rate', 'black_win_rate', 
                             'win_rate_diff', 'total_matches']]

#Filter games_df dataframe to gamesrated (with rated games) and gamesnotrated
# (with unrated games)
gamesrated = games_df[games_df['rated']]
gamesnotrated = games_df[~games_df['rated']]

# Define rating_win_pie_chart function to draw pie chart for win percentages 
# for each color in a rating_df passed in
def rating_win_pie_chart(rating_df, string_rated):
    # Label the three categories of the pie chart
    labels = 'White', 'Black', 'Draw'

    # Determine categorical percentages by dividing the number of matches each 
    # color wins by the total number of matches in the dataframe. To find the 
    # number of matches each color wins, we use a query and filter the dataframe, 
    # then find the length of the dataframe
    sizes = [len(rating_df.query("winner == 'white'")) * 100 / len(rating_df), 
            len(rating_df.query("winner == 'black'")) * 100 / len(rating_df), 
            len(rating_df.query("winner == 'draw'")) * 100 / len(rating_df)]
    fig1, ax1 = plt.subplots()

    # Define visual specifications and title, then display the plot
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal') 
    plt.title(f'Win percentages for {string_rated} matches')
    plt.show()

# Define turnsvrating function that plots a scatterplot to find correlation between 
# the ratings of players in a game and how many turns their games last
def turnsvrating():
    # Creates a random sample of 300 games
    games300 = games_df.sample(300)
    
    # Creates a line of best fit for a graph plotting user rating vs turns  
    # Calculates y-intercept and slope using numpy's polyfit function
    intercept, slope = np.polynomial.polynomial.polyfit(
                       games300.avrating, games300.turns, 1)
    ratings = np.array([min(games300.avrating), max(games300.avrating)])
    turns = intercept + slope * ratings
    
    # Creates scatterplot
    plt.scatter("avrating", "turns", data=games300)

    # Plots line and labels and displays graph 
    plt.plot(ratings, turns, color="magenta")
    plt.title("Rating vs Number of Turns")
    plt.xlabel("Average rating of the players")
    plt.ylabel("Number of turns played in the match")
    plt.show()

# Conduct time analysis by categorizing chess games into groups based on the total
# number of turns played to understand how the length of the game impacts the win 
# rates for different colors
# Define bins and labels for categorizing games by their turn count
turn_bins = [0, 30, 60, 90, 120, 150, float('inf')]
turn_labels = ['0-30', '31-60', '61-90', '91-120', '121-150', '150+']

# Add new 'turns_category' column to categorizes each game into one of the 
# predefined turn bins
games_df['turns_category'] = pd.cut(games_df['turns'], bins=turn_bins, 
                                    labels=turn_labels, right=False)

# Calculate win rates for each turn category by grouping the DataFrame by
# 'turns_category' and 'winner'
turns_win_rates = (games_df.groupby('turns_category')['winner']
                          .value_counts(normalize=True)
                          .unstack()
                          .fillna(0))

# Define opening_win_percentage function to calculate win percentage for 
# a given color and opening
def opening_win_percentage(opening, winner):
    # Filter the DataFrame to matches with the provided opening name
    filtered_games = games_df[games_df['opening_name'] == opening]

    # Calculate the percentage of games won by 'winner' in the filtered DataFrame
    percentage_won = (filtered_games['winner'] == winner).mean() * 100
    return percentage_won

# Define opening_stats function for finding openings with most wins for a specified  
# color. Returns frequency of each opening and sorted dictionary with win percentages 
def opening_stats(color):
    # Calculate the frequency of each opening when the specified color wins
    freq_color = games_df[games_df['winner'] == color]['opening_name'].value_counts()
    color_openings = {}

    # Calculate and store the win percentage for top 10 opennings
    for opening in freq_color.head(10).index:
        color_openings[opening] = opening_win_percentage(opening, color)

    # Sort the openings by their win percentage in descending order.
    color_openings = dict(sorted(color_openings.items(), key=lambda item: item[1], 
                     reverse=True))
    
    # Compute the combined win percentage for all openings not in the top 10 and 
    # add this information to the dictionary
    other_openings = ~games_df['opening_name'].isin(list(color_openings.keys()))
    proportion = round((len(games_df[other_openings & (games_df['winner'] == color)])
                         * 100 / len(games_df[other_openings])), 2)
    color_openings['Other openings'] = proportion

    return freq_color, color_openings

freq_black, black_openings = opening_stats('black')
freq_white, white_openings = opening_stats('white')

# Define opening_dict_bar_chart function to plot a bar chart showing the ten 
# most common openings leading to victories for a specific color accompanied
# by their win percentages. Pass in the dictionary returned by opening_stats() 
# function as argument
def openings_dict_bar_chart(openings_dict):
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])

    # Creates list of top openings from the dictionary keys
    openings = [i for i in openings_dict.keys()]

    # Creates percentage correspondents from dictionary values
    percentages = [openings_dict[i] for i in openings]

    # Plots and shows graph
    ax.bar(openings, percentages)
    plt.xticks(rotation=90)
    plt.figure(figsize=(10, 6))
    plt.show()

# Define move_freq_plot function for interactive visualizer
def move_freq_plot(games):
    # Split moves into individual moves
    all_moves = ' '.join(games['moves']).split()

    # Count the occurrences of each move
    move_counts = pd.Series(all_moves).value_counts()

    # Plot the top 10 opening moves
    move_counts.head(10).plot(kind='bar', color='skyblue')
    plt.title('Most Frequent Moves')
    plt.xlabel('Move')
    plt.ylabel('Frequency')
    plt.show()

# Define win_percentage_plot function for interactive visualizer
# Plots a pie chart of the win percentages for each color in a filtered dataframe
def win_percentage_plot(games):
    # Creates tuple of three labels
    labels = 'White', 'Black', 'Draw'

    # Calculates percentages for how often each game is won
    sizes = [len(games.query("winner == 'white'")) * 100 / len(games), 
        len(games.query("winner == 'black'")) * 100 / len(games), 
        len(games.query("winner == 'draw'")) * 100 / len(games)]

    # Constructs pie chart with labels from above
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax1.axis('equal') 
    plt.title(f'Win percentages')

    # Display graph
    plt.show()

# Define rating_difference_impact function for interactive visualizer
def rating_difference_impact(games):
    # Calculate the rating difference for each game
    games['rating_difference'] = games['white_rating'] - games['black_rating']

    # Create bins and labels for rating differences
    bins = [-400, -200, -100, 0, 100, 200, 400]
    labels = ['<-200', '-200 to -100', '-100 to 0', '0 to 100', '100 to 200', '200+']
    
    #use pd.cut() function to place each game into its respective bin
    games['rating_difference_group'] = pd.cut(games['rating_difference'], bins=bins, 
                                              labels=labels, right=False)

    # Calculate win percentages for each rating difference group
    win_percentages = (games.groupby('rating_difference_group')['winner']
                           .value_counts(normalize=True)
                           .unstack()
                           .fillna(0))
    
    # Plot the win percentages using a stacked bar chart
    win_percentages.plot(kind='bar', stacked=True, colormap='coolwarm_r')
    plt.title('Win Percentage Based on Rating Difference')
    plt.xlabel('Rating Difference')
    plt.ylabel('Win Percentage')
    plt.legend(title='Winner', loc='upper right')
    plt.show()

# Change pandas display settings for better visualization
pd.set_option('display.max_rows', 999)
pd.set_option('display.max_colwidth', None)

#define show_data function for interactive visualizer
def show_data(opening_name):
    # Filter dataframe to matches with user chosen opening name
    games = games_df[games_df['opening_name'] == opening_name]
    
    # Get dataframe with calculated mean values for each column
    games_describe = games.describe().loc['mean']
    
    # Display statistics and plots about chosen opening in first output window
    with out:
        # Print descriptions and descriptive statistics
        print(f"Games in dataset with this opening: {len(games)}")
        print(f"Mean turns per game: {round(games_describe['turns'])}")
        print(f"Mean overall rating: {round(games_describe['avrating'])}")
        print(f"Mean white rating: {round(games_describe['white_rating'])}")
        print(f"Mean black rating: {round(games_describe['black_rating'])}")

        # Call functions to create plots
        win_percentage_plot(games)
        move_freq_plot(games)
        rating_difference_impact(games.copy())
    
    # Display dataframe of matches with chosen opening
    with out2:
        # Convert avrating column to int so the dataframe can be sorted by it
        display(games.assign(avrating = lambda x: x['avrating'].astype(int))
                     .sort_values(by = 'avrating', ascending = False)
                     # Copy victory_status column's data into new victory column 
                     # to shorten dataframe width
                     .assign(victory = lambda df: df['victory_status'])
                     # Display relevant columns to user
                     [['avrating', 'white_rating', 'black_rating', 'winner', 
                     'victory', 'turns', 'id']]
                     # Hide index column
                     .style.hide())
    
# Create output windows
out = widgets.Output(layout={'border': '1px solid black'})
out2 = widgets.Output(layout={'border': '1px solid black', 'width': '65%'})
out3 = widgets.Output(layout={'border': '1px solid black'})

# Create button to clear output windows
clear_button = widgets.Button(description = 'clear output')

# Define clear_print method that runs when button is clicked
def clear_print(button=None):
    # Clear all outputs
    out.clear_output()
    out2.clear_output()
    out3.clear_output()

# Link clear_button to clear_print function
clear_button.on_click(clear_print)

# Get all opening names used over 25 times in dataset as options for dropdown menu
options = (games_df.opening_name.value_counts()
                               .loc[lambda x: x > 25]
                               .index.sort_values())

# Create a Dropdown widget with list of selected opening names
dropdown = widgets.Dropdown(options = options,
    value=None, 
    description='Select an opening:',
    style={'description_width': 'initial'})

# Define on_dropdown_change function to handle the dropdown value change event
def on_dropdown_change(change):
    selected_option = change['new']
    show_data(selected_option)   

# Attach the event handler to the dropdown widget
dropdown.observe(on_dropdown_change, names='value')

# Create text box to take in game id input
text_box_id = widgets.Textarea(
    value='',
    description='Enter the game id to simulate:',
    layout={'width': '350px', 'height': '25px'},
    style={'description_width': 'initial'})

# Create text box to take in number of seconds input
text_box_seconds = widgets.Textarea(
    value='1',
    description='Enter seconds between each turn:',
    layout={'width': '350px', 'height': '25px'},
    style={'description_width': 'initial'})

# Create button to simulate moves
simulate_button = widgets.Button(description = 'simulate')

# Define simulate function to to visually simulate the moves of a chess game 
def simulate(button = None):
    # Display output in a separate column
    with out3:
        # Draw and display the initial state of the chess board
        board_svg = chess.svg.board(board=chess.Board())
        display(SVG(board_svg))

        # Retrieve list of moves from chess match with given 'id' value
        descriptive_moves = games_df.loc[games_df['id'] == text_box_id.value, 
                                         'moves'].values[0]

        # Initialize an empty list to store moves in UCI (Universal Chess 
        # Interface) format
        uci_moves = []

        # Create a new chess board object
        board = chess.Board()

        # Convert each descriptive move to UCI format and make the move 
        # on the board
        for move_str in descriptive_moves.split():
            move = board.parse_san(move_str)
            uci_moves.append(move.uci())
            board.push(move)

        # Reset the board to the initial state for animation
        board = chess.Board()

        # Animate each move on the chess board.
        for move in uci_moves:
            board.push_uci(move)

            # Clear the previous board state before displaying the new one
            clear_output(wait=True)

            # Draw the current state of the board
            board_svg = chess.svg.board(board=board)

            # Display the updated board and pause for the specified number 
            # of seconds
            display(SVG(board_svg))
            time.sleep(float(text_box_seconds.value)) 

# Link simulate_button to simulate function
simulate_button.on_click(simulate)    