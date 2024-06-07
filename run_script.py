import schedule
import time
import price_tracker_functions as functions

def job():
    print("Task is running")

# Schedule the task to run every 30 minutes
schedule.every(10).minutes.do(functions.update_prices)

# Function to run the schedule loop
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for a short time to avoid busy-waiting

if __name__ == "__main__":
    run_schedule()
