from datetime import datetime
import pytz

# Get the current time in IST
ist = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

# Write the current time to a file
with open('current_time_ist.txt', 'w') as file:
    file.write(f"Current IST time: {current_time_ist}")

print("The current IST time has been written to 'current_time_ist.txt'.")
