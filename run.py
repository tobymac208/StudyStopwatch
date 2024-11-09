'''
    A study timer application that supports two modes:
    1. Normal mode: Runs a configurable study timer with breaks
       Example: "3,30,Math" runs 3 study sessions of 30 minutes each
    2. Pomodoro mode: Runs continuous 25-minute sessions with 5-minute breaks
    
    Usage:
    - Command line: python run.py <repetitions> <minutes> <subject>
    - Interactive: Follow the prompts to choose mode and settings
    
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
import os

from datetime import date
from random import choice


class StudyTimer:
    """A study timer application supporting normal and pomodoro study modes"""
    
    LOGGING_FILE = "logfile.json"
    TEST_LOGGING_FILE = "test_logfile.json"
    
    DEFAULT_REPETITIONS = 3
    DEFAULT_MINUTES = 30
    DEFAULT_SUBJECT = "Unspecified"
    
    POMODORO_SESSION_LENGTH = 25  # minutes
    POMODORO_BREAK_TIME = 5  # minutes
    
    @staticmethod
    def ask_user_for_control_variables():
        """Get study session parameters from user input."""
        prompt = ('Enter the number of reps, the length for each rep, and the subject you are studying.\n'
                 'Repetitions,minutes,subject: ')

        try:
            user_input = input(prompt)
            repetitions, minutes, subject = user_input.split(',')
            return (int(repetitions), int(minutes), subject.strip())

        except (ValueError, IndexError) as e:
            print(f'Invalid input: {str(e)}')
            print(f'Defaulting to {StudyTimer.DEFAULT_REPETITIONS} repetitions, {StudyTimer.DEFAULT_MINUTES} minutes.')
            return (StudyTimer.DEFAULT_REPETITIONS, StudyTimer.DEFAULT_MINUTES, StudyTimer.DEFAULT_SUBJECT)

    @staticmethod
    def format_user_input_to_json(data_structure, filename):
        unique_id = uuid4()
        current_logs = {}

        if exists(filename):
            try:
                with open(filename) as file:
                    current_logs = json.load(file)
            except json.decoder.JSONDecodeError:
                remove(filename)
            except Exception as e:
                traceback.print_exc(e)

        current_logs[str(unique_id)] = {
            "name": data_structure[2],
            "repetitions": data_structure[0],
            "minutes": data_structure[1],
            "date": str(date.today())
        }
        return current_logs

    @staticmethod
    def log_info(information_tuple, filename):
        dictionaryObj = StudyTimer.format_user_input_to_json(information_tuple, filename)
        with open(filename, "w+") as file:
            json.dump(dictionaryObj, file)

    @staticmethod
    def run_normal_mode(repetitions, minutes, subject, break_time):
        print(f'You want to study for {minutes} minute(s), {repetitions} time(s). You want to study for {subject}. Thanks!')
        
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
                time.sleep(break_time * 60)  # waits for the break time

                # Notify the user that the break is done.
                print('The break is over. Type any phrase and hit ENTER to continue!')
                while len(input().strip()) < 1:
                    continue  # validate that the input is not empty

                print('Continuing...\n\n\n\n')  # Print some spacing.

        print(
            f'\n\nDone! Your study period for {subject} has completed. Please go enjoy your day now.')

    @staticmethod
    def run_pomodoro_mode():
        print("You chose the continuous Pomodoro option! Here it goes...")
        session_count = 0

        while True:
            session_count = session_count + 1
            print(f"Here comes session #{session_count}.")

            for i in range(StudyTimer.POMODORO_SESSION_LENGTH):
                time.sleep(60)  # Pause for one minute.
                # Notify the user whenever one minute has passed.
                print(f'{i+1}', end=" ", flush=True)

            # break time!
            print("\n\n\t\tBreak time!")
            time.sleep( StudyTimer.POMODORO_BREAK_TIME * 60 )
            print('The break is over. Type any phrase and hit ENTER to continue, or type EXIT to stop!')
            continue_or_exit = input('Phrase or "EXIT": ')
            if continue_or_exit.upper() == "EXIT":
                break
            else:
                continue
        
        return session_count, StudyTimer.POMODORO_SESSION_LENGTH, "None"

    @classmethod
    def main(cls):
        print("Welcome! It's time to study.")
        
        repetitions = None
        minutes = None
        subject = None
        
        # Handle CLI arguments
        if len(sys.argv) == 4:
            try:
                repetitions = int(sys.argv[1])
                minutes = int(sys.argv[2])
                subject = sys.argv[3]
            except:
                print('There was a problem with the command line arguments. Please try again.')
        else:
            print("NOTE: \"Pomodoro\" means the timer will just run, no further input.\n\"Normal\" will ask you to enter three more pieces of information.")
            study_type_input = input('Enter "Pomodoro" or "normal": ')
            study_type = "normal"
            STUDY_TYPES = ('normal', 'pomodoro')
            
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')

            if study_type_input.upper() == "POMODORO":
                study_type = "pomodoro"
            elif study_type_input.upper() == "NORMAL":
                study_type = "normal"
            else:
                print("Study type input failed: User did not enter a valid option. Default value is \"normal\".")

            if study_type == STUDY_TYPES[0]:
                # Returns a tuple of required information since the user has not passed in the data via the CLI.
                repetitions, minutes, subject = StudyTimer.ask_user_for_control_variables()

                # Print control variables as a response to the user's input. The lets them know what they entered.
                print(
                    f'You want to study for {minutes} minute(s), {repetitions} time(s). You want to study for {subject}. Thanks!')

                # Run the loop for the amount of repetitions specified.
                StudyTimer.run_normal_mode(repetitions, minutes, subject, StudyTimer.POMODORO_BREAK_TIME)
            elif study_type == STUDY_TYPES[1]:
                session_count, minutes, subject = StudyTimer.run_pomodoro_mode()
                repetitions = session_count

        if all([repetitions, minutes, subject]):
            cls.log_info((repetitions, minutes, subject), cls.LOGGING_FILE)
        else:
            print("ERROR: A required value was not given. Required values are repetitions, minutes, and subject.")

    @classmethod
    def test(cls):
        cls.log_info((2, 2, "test"), "test.json")

if __name__ == "__main__":
    if config.IS_TESTING:
        StudyTimer.test()
    else:
        StudyTimer.main()
