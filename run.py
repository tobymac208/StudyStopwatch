'''
	Runs a timer for a specified amount of time, for a specified number
	of minutes. For instance, 3,30 would run a timer 3 times for a duration
	of 30 minutes.

	Author: Nik F.
	Date created: 04.15.2023
'''
import time
import config

import json
from uuid import uuid4

import traceback

from os.path import exists
from os import remove

from datetime import date
from random import choice


LOGGING_FILE = "logfile.json"
TEST_LOGGING_FILE = "test_logfile.json"


def ask_user_for_control_variables():
    '''
                Returns A list of items. 
                                The items are either what the user entered or default values if the user entered invalid items.
    '''
    repetitions = None
    minutes = None
    subject = None

    user_input = input(
        'Enter the number of reps, the length for each rep, and the subject you are studying.\nRepetitions,minutes,subject: ')

    try:  # Attempt to split the input into repetitions and minutes.
        parts = user_input.split(',')

        repetitions = int(parts[0])
        minutes = int(parts[1])
        subject = parts[2]

    except Exception as e:
        print(e)  # print the exception
        print('Something occurred. Cannot process input.\nDefaulting to 3,30.')
        repetitions = 3
        minutes = 30
        subject = "Unspecified"

    return (repetitions, minutes, subject)


def format_user_input_to_json(data_structure, filename):
    '''
                Description: Ensure that the provided data structure properly formats to a dictionary.

                Returns: dictionary representation of the provided data structure.
    '''
    unique_id = uuid4()
    current_logs = {}

    # If the file exists, then
    if exists(filename):
        try:
            with open(filename) as file:
                current_logs = json.load(file)
        except json.decoder.JSONDecodeError as e:
            remove(filename)  # the file is empty. Remove the file.
        except Exception as e:
            traceback.print_exc(e)

    current_logs[str(unique_id)] = {
        "name": data_structure[2],
        "repetitions": data_structure[0],
        "minutes": data_structure[1],
        "date": str(date.today())
    }

    # Return the JSON object to the caller.
    return current_logs


def log_info(information_tuple, filename):
    '''
                Regardless of the amount of information, log it to a text file for later parsing.
    '''
    # Convert the dictionary into a json object.
    dictionaryObj = format_user_input_to_json(information_tuple, filename)

    with open(filename, "w+") as file:
        # Write the JSON data to the JSON logging file.
        json.dump(dictionaryObj, file)


def main():
    '''
        Main program
    '''
    
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
    subject = None  # The subject the user is studying.
    BREAK_TIME = config.DESIRED_BREAK_TIME  # in minutes

    # Returns a tuple of required information.
    repetitions, minutes, subject = ask_user_for_control_variables()

    # Run the loop for the amount of repetitions specified.
    for i in range(repetitions):
        print(f'Beginning repetition #{i + 1}')

        for i in range(minutes):  # Run for the duration of each study period.
            time.sleep(60)  # Pause for one minute.
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
        time.sleep(BREAK_TIME * 60)  # waits for the break time

        # Notify the user that the break is done.
        print('The break is over. Type any phrase and hit ENTER to continue!')
        while len(input().strip()) < 1:
            continue  # validate that the input is not empty

        print('Continuing...\n\n\n\n')  # Print some spacing.

    print(
        f'Done! Your study period for {subject} has completed. Please go enjoy your day now.')

    log_info((repetitions, minutes, subject), LOGGING_FILE)


def TEST_CASES():
    '''
        Runs a test one the data.
    '''
    repetitions = choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
    minutes = choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
    # The subject the user is studying.
    subject = choice(['math', 'english', 'reading', 'nothing'])

    log_info((repetitions, minutes, subject), TEST_LOGGING_FILE)

IS_TESTING = False # Controls whether to run the test code or not.

if IS_TESTING:
    for _ in range(150):
        TEST_CASES()
else:
    main()
