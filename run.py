'''
	Runs a timer for a specified amount of time, for a specified number
	of minutes. For instance, 3,30 would run a timer 3 times for a duration
	of 30 minutes.

	Author: Nik F.
	Date created: 04.15.2023
'''
import time
import config
import sys

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

    current_logs[str(unique_id)] = { # This will clobber any entry that already existed with the UUID given. I don't love this approach because of that.
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

    print("Welcome! It's time to study.")

    repetitions = None
    minutes = None
    subject = None  # The subject the user is studying.
    BREAK_TIME = config.DESIRED_BREAK_TIME  # in minutes
    
    # Check if the user has passed the parameters through the CLI already.
    CLI_arguments = sys.argv
    number_of_args = len(CLI_arguments)
    
    # TODO: Fix the input validation later.
    if number_of_args == 4:
        try:
            repetitions = int(CLI_arguments[1])
            minutes = int(CLI_arguments[2])
            subject = CLI_arguments[3]
        except:
            print('There was a problem with the command line arguments. Please try again.')
    else:
        print("NOTE: Pomodoro means the timer will just run, no further input.\nNormal will ask you to enter three more pieces of information.")
        study_type_input = input('Enter "Pomodoro" or "normal": ')
        study_type = "normal"
        STUDY_TYPES = ('normal', 'pomodoro')
        
        if study_type_input.upper() == "POMODORO":
            study_type = "pomodoro"
        elif study_type_input.upper() == "NORMAL":
            study_type = "normal"
        else:
            print("Study type input failed: User did not enter a valid option. Default value is \"normal\".")

        if study_type == STUDY_TYPES[0]:
            # Returns a tuple of required information since the user has not passed in the data via the CLI.
            repetitions, minutes, subject = ask_user_for_control_variables()

            # Print control variables as a response to the user's input. The lets them know what they entered.
            print(
                f'You want to study for {minutes} minute(s), {repetitions} time(s). You want to study for {subject}. Thanks!')

            # Run the loop for the amount of repetitions specified.
            for i in range(repetitions):
                print(f'Beginning repetition #{i + 1}')

                for j in range(minutes):  # Run for the duration of each study period.
                    time.sleep(60)  # Pause for one minute.
                    # Notify the user whenever one minute has passed.
                    print(f'{j+1}', end=" ", flush=True)

                # Only take a break if it is NOT the last repetition.
                # Where i+1 is the current rep count.
                if (i+1) != repetitions:
                    print('Break Time. Play some games!')
                    time.sleep(BREAK_TIME * 60)  # waits for the break time

                    # Notify the user that the break is done.
                    print('The break is over. Type any phrase and hit ENTER to continue!')
                    while len(input().strip()) < 1:
                        continue  # validate that the input is not empty

                    print('Continuing...\n\n\n\n')  # Print some spacing.

            print(
                f'\n\nDone! Your study period for {subject} has completed. Please go enjoy your day now.')
        elif study_type == STUDY_TYPES[1]:
            print("You chose the continuous Pomodoro option! Here it goes...")

            SESSION_LENGTH = 25 # in minutes
            BREAK_TIME = 5 # in minutes
            session_count = 0 # keeps track of how many times the user studied

            while True:
                session_count = session_count + 1
                print(f"Here comes session #{session_count}.")

                for i in range(SESSION_LENGTH):
                    time.sleep(60)  # Pause for one minute.
                    # Notify the user whenever one minute has passed.
                    print(f'{i+1}', end=" ", flush=True)

                # break time!
                print("Break time!")
                time.sleep( BREAK_TIME * 60 )
                print('The break is over. Type any phrase and hit ENTER to continue, or type EXIT to stop!')
                continue_or_exit = input('Phrase or "EXIT": ')
                if continue_or_exit.upper() == "EXIT":
                    break
                else:
                    continue
            
            repetitions = session_count
            minutes = SESSION_LENGTH
            subject = "None"
    
    # Shorthand way of checking that the arguments are not null.
    if repetitions and minutes and subject:
        log_info((repetitions, minutes, subject), LOGGING_FILE)
    else:
        print("ERROR: A required value was not given. Required values are repetitions, minutes, and subject.")


TESTING = False

def test():
    log_info((2, 2, "test"), "test.json")

if __name__ == "__main__":
    
    if TESTING:
        test()
    else:
        main()

