'''
	Runs a timer for a specified amount of time, for a specified number
	of minutes. For instance, 3,30 would run a timer 3 times for a duration
	of 30 minutes.

	Author: Nik F.
	Date created: 04.15.2023
'''
import time
import config

print(
	'''
   .----.
   |C>_ |
 __|____|__         Study Time!
|  ______--|
`-/.::::.\-'a
 `--------'
	'''
)

user_input = input('Repetitions,minutes: ')
repetitions = None
minutes = None
BREAK_TIME = config.DESIRED_BREAK_TIME  # in minutes

try: # Attempt to split the input into repetitions and minutes.
	parts = user_input.split(',')
	
	#remove and white space and then convert the values to numbers.
	repetitions = int(parts[0])
	minutes = int(parts[1])
except Exception as e: # Naked exception
	print(e)
	print('Something occurred. Cannot process input.\nDefaulting to 3,30.')
	repetitions = 3
	minutes = 30

# Run the loop for the amount of repetitions specified.
for i in range(repetitions):
	print(f'Beginning repetition #{i + 1}')

	for i in range(minutes): # Run for the duration of each study period.
		time.sleep(1 * 60) # Pause for one minute.
		# Notify the user whenever one minute has passed.
		print(i+1)

	print('''
				   *
		   	  $$ $$$$$ $$
              $$ $$$$$ $$
             .$$ $$$$$ $$.
             :$$ $$$$$ $$:
             $$$ $$$$$ $$$
             $$$ $$$$$ $$$
            ,$$$ $$$$$ $$$.                          Break Time. Play some games!
           ,$$$$ $$$$$ $$$$.
          ,$$$$; $$$$$ :$$$$.
         ,$$$$$  $$$$$  $$$$$.
       ,$$$$$$'  $$$$$  `$$$$$$.
     ,$$$$$$$'   $$$$$   `$$$$$$$.
  ,s$$$$$$$'     $$$$$     `$$$$$$$s.
$$$$$$$$$'       $$$$$       `$$$$$$$$$
$$$$$Y'          $$$$$          `Y$$$$$
		'''
	)
	time.sleep(BREAK_TIME * 60)
    
    # Notify the user that the break is done.
	print('The break is over. Type any phrase and hit ENTER to continue!')
	while len(input().strip()) < 1:
		# Make sure the user actually typed something. Otherwise, don't continue studying.
		continue
	print('Continuing...\n\n\n\n') # Print some spacing.

print('Done! Your study period has completed. Please go enjoy your day now.')
