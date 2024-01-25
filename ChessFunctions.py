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

games_df = pd.read_csv("games.csv")

#return percentage of time that r1 is higher than r2 and winner wins the match
def getwinners(r1, r2, winner):
    # Filter the DataFrame to the matches where r1 is greater than r2
    filtered_games = games_df[games_df[r1] > games_df[r2]]

    # Calculate the percentage of games won by 'winner' in the filtered DataFrame
    percentage_won = (filtered_games['winner'] == winner).mean() * 100
    return percentage_won

#create new avrating column that takes the average of the black rating and white rating in the match
games_df['avrating'] = (games_df['white_rating']+games_df['black_rating'])/2


# Define function to calculate win rate for a color within a rating group
def win_rate_for_color(group, color):
    # Define the rating groups
    bins = [0, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600]
    labels = ['0-1200', '1200-1400', '1400-1600', '1600-1800', 
              '1800-2000', '2000-2200', '2200-2400', '2400-2600']

    #add new column to dataframe that places each match within its respective rating group using pd.cut() function
    games_df['rating_group'] = pd.cut(games_df['avrating'], bins = bins, labels = labels, right = False)

    #filter dataframe to get desired rating group and winner
    games_in_group = games_df[games_df['rating_group'] == group]
    wins = games_in_group[games_in_group['winner'] == color]
    #calculate win percentage while avoiding a ZeroDivisionError
    if len(games_in_group) > 0:
        return len(wins) / len(games_in_group) * 100 
    else:
        return 0

# Define function to calculate the number of matches in each rating group
def count_matches_in_group(group):
    return len(games_df[games_df['rating_group'] == group])

# Calculate win rates and total matches played for each group and color using a for loop
win_rates = {}
labels = ['0-1200', '1200-1400', '1400-1600', '1600-1800', 
              '1800-2000', '2000-2200', '2200-2400', '2400-2600']
for group in labels:
    win_rates[group] = {
        'white_win_rate': win_rate_for_color(group, 'white'),
        'black_win_rate': win_rate_for_color(group, 'black'),
        'total_matches': count_matches_in_group(group)
    }
# Convert the results to a pandas DataFrame for better visualization
win_rates_df = pd.DataFrame(win_rates).T
#Create win_rate_diff column to show difference between white win rate and black win rate
win_rates_df['win_rate_diff'] = win_rates_df['white_win_rate'] - win_rates_df['black_win_rate']
#reorder columns so win_rate_diff is before total_matches
win_rates_df = win_rates_df[['white_win_rate', 'black_win_rate', 'win_rate_diff', 'total_matches']]


#Filter games_df dataframe to gamesrated (with rated games) and gamesnotrated (with unrated games)
gamesrated = games_df[games_df['rated']]
gamesnotrated = games_df[~games_df['rated']]

#neha fix
#define rating_win_pie_chart() function to draw pie chart for win percentages 
#in rated and unrated matches
def rating_win_pie_chart(rating_df, string_rated):
    #label the three segments of the pie chart
    labels = 'White', 'Black', 'Stalemate'

    #determine percentages for each segment by filtering dataframe. For example,
    #win percentage for white is found by multiplying the number of matches that
    #white won in the dataframe by 100 and then dividing by the total number of 
    #matches in the datframe
    sizes = [len(rating_df.query("winner == 'white'"))*100/len(rating_df), 
            len(rating_df.query("winner == 'black'"))*100/len(rating_df), 
            len(rating_df.query("winner == 'draw'"))*100/len(rating_df)]
    fig1, ax1 = plt.subplots()

    #define visual specs and title, then display the plot
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal') 
    plt.title(f'Win percentages for {string_rated} matches')
    plt.show()

#neha add
#turns vs rating chart
def turnsvrating():
    games300 = games_df.sample(300)
    
    intercept, slope = np.polynomial.polynomial.polyfit(
        games300.avrating,
        games300.turns,
        1)
    ratings = np.array([min(games300.avrating), max(games300.avrating)])
    turns = intercept + slope * ratings
    
    plt.scatter("avrating", "turns", data=games300)
    plt.plot(ratings, turns, color="magenta")
    plt.title("Rating vs Number of Turns")
    plt.xlabel("Average rating of the players")
    plt.ylabel("Number of turns played in the match")
    plt.show()

#neha replace
# Analysis 1: Time Control Analysis (Inferred from Number of Turns)
# Categorize games based on the number of turns
bins = [0, 30, 60, 90, 120, 150, float('inf')]
labels = ['0-30', '31-60', '61-90', '91-120', '121-150', '150+']
games_df['turns_category'] = pd.cut(games_df['turns'], bins=bins, labels=labels, right=False)

# Calculate win rates for each turns category
turns_win_rates = (games_df.groupby('turns_category')['winner']
                          .value_counts(normalize=True)
                          .unstack()
                          .fillna(0))



def opening_win_percentage(opening, winner):
    # Filter the DataFrame once where r1 is greater than r2
    filtered_games = games_df[games_df['opening_name'] == opening]
    # Calculate the percentage of games won by 'winner' in the filtered DataFrame
    percentage_won = (filtered_games['winner'] == winner).mean() * 100
    return percentage_won
#neha comment
def opening_stats(color):
    freq_color = games_df[games_df['winner']==color]['opening_name'].value_counts()
    color_openings = {}

    for opening in freq_color.head(10).index:
        color_openings[opening] = opening_win_percentage(opening, color)

    color_openings = dict(sorted(color_openings.items(), key=lambda item: item[1], 
                     reverse = True))
    
    other_openings = ~games_df['opening_name'].isin(list(color_openings.keys()))
    proportion = round((len(games_df[other_openings & (games_df['winner'] == color)])
                         * 100 / len(games_df[other_openings])), 2)
    color_openings['Other openings'] = proportion

    return freq_color, color_openings

freq_black, black_openings = opening_stats('black')
freq_white, white_openings = opening_stats('white')

def openings_dict_bar_chart(openings_dict):
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    openings = [i for i in openings_dict.keys()]
    percentages = [openings_dict[i] for i in openings]
    ax.bar(openings, percentages)
    plt.xticks(rotation=90)
    plt.figure(figsize=(10, 6))
    plt.show()



#define plotting functions for interactive visualizer
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

#neha
def win_percentage_plot(games):
    labels = 'White', 'Black', 'Stalemate'
    sizes = [len(games.query("winner == 'white'"))*100/len(games), 
        len(games.query("winner == 'black'"))*100/len(games), 
        len(games.query("winner == 'draw'"))*100/len(games)]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax1.axis('equal') 
    plt.title(f'Win percentages')
    plt.show()
    
def rating_difference_impact(games):
    # Calculate the rating difference for each game
    games['rating_difference'] = games['white_rating'] - games['black_rating']

    # Create bins and labels for rating differences
    bins = [-400, -200, -100, 0, 100, 200, 400]
    labels = ['<-200', '-200 to -100', '-100 to 0', '0 to 100', '100 to 200', '200+']
    #use pd.cut() function to place each game into its respective bin
    games['rating_difference_group'] = pd.cut(games['rating_difference'], bins=bins, labels=labels, right=False)

    # Calculate win percentages for each rating difference group
    win_percentages = games.groupby('rating_difference_group')['winner'].value_counts(normalize=True).unstack().fillna(0)
    
    # Plot the win percentages using a stacked bar chart
    win_percentages.plot(kind='bar', stacked=True, colormap='coolwarm_r')
    plt.title('Win Percentage Based on Rating Difference')
    plt.xlabel('Rating Difference')
    plt.ylabel('Win Percentage')
    plt.legend(title='Winner', loc='upper right')
    plt.show()

#change pandas display settings for better visualization
pd.set_option('display.max_rows', 999)
pd.set_option('display.max_colwidth', None)
def show_data(opening_name):
    #filter dataframe to matches with user chosen opening name
    games = games_df[games_df['opening_name'] == opening_name]
    
    #get dataframe with calculated mean values for each column
    games_describe = games.describe().loc['mean']
    
    #neha
    #display statistics and plots about chosen opening in first output window
    with out:
        print(f"Games in dataset with this opening: {len(games)}")
        print(f"Mean turns per game: {round(games_describe['turns'])}")
        print(f"Mean overall rating: {round(games_describe['avrating'])}")
        print(f"Mean white rating: {round(games_describe['white_rating'])}")
        print(f"Mean black rating: {round(games_describe['black_rating'])}")
        win_percentage_plot(games)
        move_freq_plot(games)
        rating_difference_impact(games.copy())
    
    #display dataframe of matches with chosen opening
    with out2:
        #convert avrating column to integer type so the dataframe can be sorted by it
        display(games.assign(avrating = lambda x: x['avrating'].astype(int))
                     .sort_values(by = 'avrating', ascending = False)
                     #copy victory_status column's data into new victory column to shorten dataframe width
                     .assign(victory = lambda df: df['victory_status'])
                     #display relevant columns to user
                     [['avrating', 'white_rating', 'black_rating', 'winner', 'victory', 'turns', 'id']]
                     #hide index column
                     .style.hide())
    
#create output windows
out = widgets.Output(layout={'border': '1px solid black'})
out2 = widgets.Output(layout={'border': '1px solid black', 'width': '65%'})
out3 = widgets.Output(layout={'border': '1px solid black'})

#create button to clear output windows
clear_button = widgets.Button(description = 'clear output')
#define method that runs when button is clicked
def clear_print(button=None):
    out.clear_output()
    out2.clear_output()
    out3.clear_output()
#link clear_button to clear_print function
clear_button.on_click(clear_print)


#get all opening names used over 25 times in dataset
options = games_df.opening_name.value_counts().loc[lambda x: x > 25].index.sort_values()
# Create a Dropdown widget with list of selected opening names
dropdown = widgets.Dropdown(options = options,
    value=None,  # Default selected option
    description='Select an opening:',
    style={'description_width': 'initial'})
# Function to handle the dropdown value change event
def on_dropdown_change(change):
    selected_option = change['new']
    show_data(selected_option)   
# Attach the event handler to the dropdown widget
dropdown.observe(on_dropdown_change, names='value')


#create text box to take in game id input
text_box_id = widgets.Textarea(
    value='',
    description='Enter the game id to simulate:',
    layout={'width': '350px', 'height': '25px'},
    style={'description_width': 'initial'})

#create text box to take in number of seconds input
text_box_seconds = widgets.Textarea(
    value='1',
    description='Enter seconds between each turn:',
    layout={'width': '350px', 'height': '25px'},
    style={'description_width': 'initial'})


#neha
simulate_button = widgets.Button(description = 'simulate')
def simulate(button = None):
    with out3:
        # Function to draw the chess board
        board_svg = chess.svg.board(board=chess.Board())
        display(SVG(board_svg))

        # Replace this with your actual chess moves
        descriptive_moves = games_df.loc[games_df['id'] == text_box_id.value, 'moves'].values[0]

        # Convert descriptive moves to UCI format
        uci_moves = []
        board = chess.Board()

        for move_str in descriptive_moves.split():
            move = board.parse_san(move_str)
            uci_moves.append(move.uci())
            board.push(move)

        # Function to animate the moves
        board = chess.Board()
        for move in uci_moves:
            board.push_uci(move)
            clear_output(wait=True)
            board_svg = chess.svg.board(board=board)
            display(SVG(board_svg))
            time.sleep(float(text_box_seconds.value))  # Adjust the speed of the animation
simulate_button.on_click(simulate)    
    
