'''
	Runs a timer for a specified amount of time, for a specified number
	of minutes. For instance, 3,30 would run a timer 3 times for a duration
	of 30 minutes.

	Author: Nik F.
	Date created: 04.15.2023
'''
import time
import config


def validate_input():
    '''
		Returns A list of items. 
  				The items are either what the user entered or default values if the user entered invalid items.
    '''
    repetitions = None
    minutes = None
    subject = None
    
    user_input = input('Enter the number of reps, the length for each rep, and the subject you are studying.\nRepetitions,minutes,subject: ')
    
    try: # Attempt to split the input into repetitions and minutes.
        parts = user_input.split(',') 
        
        repetitions = int(parts[0])
        minutes = int(parts[1])
        subject = parts[2]
    
    except Exception as e:
        print(e) # print the exception
        print('Something occurred. Cannot process input.\nDefaulting to 3,30.')
        repetitions = 3
        minutes = 30
        subject = "Unspecified"
    
    return (repetitions, minutes, subject)


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

repetitions = None
minutes = None
subject = None # The subject the user is studying.
BREAK_TIME = config.DESIRED_BREAK_TIME  # in minutes

repetitions, minutes, subject = validate_input() # Returns a tuple of required information.

# Run the loop for the amount of repetitions specified.
for i in range(repetitions):
	print(f'Beginning repetition #{i + 1}')

	for i in range(minutes): # Run for the duration of each study period.
		time.sleep(1 * 60) # Pause for one minute.
		# Notify the user whenever one minute has passed.
		print(i+1)

	print('''
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
	time.sleep(BREAK_TIME * 60) # waits for the break time
    
    # Notify the user that the break is done.
	print('The break is over. Type any phrase and hit ENTER to continue!')
	while len(input().strip()) < 1: continue # validate that the input is not empty
 
	print('Continuing...\n\n\n\n') # Print some spacing.

print(f'Done! Your study period for {subject} has completed. Please go enjoy your day now.')
