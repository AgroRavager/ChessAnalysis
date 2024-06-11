# Shaurya Jeloka, Ian Jeong, Akshay Vakharia
# 6/9/2024

# This program is a script that runs the update_prices() function defined in price_tracker_functions.py
# every ten minutes to get the prices of all items being tracked from the internet and update
# the databse. This program is meant to run continuously in the background to collect data 
# at a frequent yet reasonable rate.

import schedule
import time
import price_tracker_functions as functions

# Schedule the update_prices function to run every ten minutes
schedule.every(10).minutes.do(functions.update_prices)

# Define the function to run the scheduled loop
def run_schedule():

    #run a continuous loop
    while True:
        
        # Check and run pending tasks
        schedule.run_pending() 

        #briefly pause the loop to avoid busy waiting
        time.sleep(1)

#execute run_schedule function
if __name__ == "__main__":
    run_schedule()
