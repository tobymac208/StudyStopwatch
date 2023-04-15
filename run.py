'''
	Runs a timer for a specified amount of time, for a specified number
	of minutes. For instance, 3,30 would run a timer 3 times for a duration
	of 30 minutes.

	Author: Nik F.
	Date created: 04.15.2023
'''
import time

user_input = input('Repititions,minutes: ')
repititions = None
minutes = None
BREAK_TIME = 1  # in minutes

try: # Attempt to split the input into repitions and minutes.
	parts = user_input.split(',')
	
	#remove and whitespace and then convert the values to numbers.
	repititions = int(parts[0])
	minutes = int(parts[1])
except Exception as e: # Naked exception
	print(e)
	print('Something occurred. Cannot process input.\nDefaulting to 3,30.')
	repititions = 3
	minutes = 30

# Run the loop for the amount of repititions specified.
for i in range(repititions):
	print(f'Beginning timer #{i + 1}')
	time.sleep(minutes * 60) # The user will pass in a value in minutes. A conversion is needed.
	
	print(f'Done! Taking a breaking for {BREAK_TIME} minutes.')
	time.sleep(BREAK_TIME * 60)
	
	print('\n\n\n\n') # Print some spacing.

print('Done! Your study period has completed. Please go enjoy your day now.')
