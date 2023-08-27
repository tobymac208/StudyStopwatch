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
import uuid


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


def format_user_input_to_json(data_structure):
    '''
                Description: Ensure that the provided data structure properly formats to JSON.

                Returns: JSON representation of the provided data structure.
    '''
    reps = None
    minutes = None
    subject = None
    unique_id = uuid.uuid4()
    current_logs = {}

    # Parse the data structure's information into fields.
    try:
        reps = int(data_structure[0])
        minutes = int(data_structure[1])
        subject = data_structure[2]
    except TypeError as error:
        print(f'{error}. There was an error. Please ensure the user input was correct.')

    # There was an exception. Return nothing to the caller.
    if reps is None and minutes is None and subject is None:
        return None
    
    try:
        current_logs = json.load(open('logfile.json', 'r').read()) # Read everything in from the file and convert it to a dictionary.
    except Exception as e:
        print(f'{e}. There was an error. It\'s likely that there are no entries in the file or that the file does not exist.')
    
    current_logs[str(unique_id)] = {
        "name": subject,
        "repetitions": reps,
        "minutes": minutes
    }
    
    jsonObject = json.dumps(current_logs) # Convert the whole dictionary back into a JSON object.

    # Return the JSON object to the caller.
    return jsonObject


def log_info(information_tuple):
    '''
                Regardless of the amount of information, log it to a text file for later parsing.
    '''
    with open("logfile.json", "w+") as file:
        # Convert the dictionary into a json object.
        jsonObj = format_user_input_to_json(information_tuple)

        # Write the JSON data to the JSON logging file.
        json.dump(jsonObj, file)


def main():
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
            time.sleep(1 * 60)  # Pause for one minute.
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

    log_info((repetitions, minutes, subject))


def TEST_CASES():
    '''
        Runs a string of tests to test the overall program's functionality.
    '''
    # TODO: Implement a series of test cases.


main()
