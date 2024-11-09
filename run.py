#!/usr/bin/env python3

import json
import sys
import time
import logging
from datetime import date
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from uuid import uuid4
import re
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

@dataclass
class StudySession:
    """Data class for study session parameters"""
    name: str
    repetitions: int
    minutes: int
    date: str

class SecurityConfig:
    """Security-related configuration settings"""
    MAX_REPETITIONS = 100
    MAX_MINUTES = 480  # 8 hours
    MAX_SUBJECT_LENGTH = 100
    MAX_FILE_SIZE = 10_000_000  # 10MB
    ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9\s\-_]+$')

class StudyTimer:
    """A secure study timer application supporting normal and pomodoro study modes"""
    
    # Secure path handling
    BASE_DIR = Path(__file__).parent.resolve()
    LOGGING_FILE = BASE_DIR / "logfile.json"
    TEST_LOGGING_FILE = BASE_DIR / "test_logfile.json"
    LOG_DIR = BASE_DIR / "logs"
    
    # Application defaults
    DEFAULT_REPETITIONS = 3
    DEFAULT_MINUTES = 30
    DEFAULT_SUBJECT = "Unspecified"
    
    # Pomodoro settings
    POMODORO_SESSION_LENGTH = 25  # minutes
    POMODORO_BREAK_TIME = 5  # minutes

    @classmethod
    def setup_logging(cls) -> None:
        """Configure secure logging with rotation and proper formatting"""
        cls.LOG_DIR.mkdir(exist_ok=True)
        log_file = cls.LOG_DIR / "study_timer.log"
        
        # Ensure secure file permissions
        log_file.touch(mode=0o600, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    log_file,
                    maxBytes=1024*1024,  # 1MB
                    backupCount=3,
                    mode='a'
                ),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not value:
            return ""
        # Remove any potentially dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9\s\-_]', '', value)
        return sanitized[:SecurityConfig.MAX_SUBJECT_LENGTH]

    @staticmethod
    def validate_numeric_input(value: int, max_value: int, name: str) -> int:
        """Validate numeric inputs are within acceptable ranges"""
        try:
            value = int(value)
            if not 0 < value <= max_value:
                raise ValueError
            return value
        except (ValueError, TypeError):
            logging.warning(f"Invalid {name} provided: {value}")
            raise ValueError(f"{name} must be between 1 and {max_value}")

    @classmethod
    def validate_file_path(cls, filepath: Path) -> bool:
        """Validate file path is safe and within allowed directory"""
        try:
            filepath = Path(filepath).resolve()
            return filepath.parent == cls.BASE_DIR.resolve()
        except (TypeError, ValueError):
            return False

    @classmethod
    def safe_file_read(cls, filepath: Path) -> Dict:
        """Safely read JSON file with proper error handling"""
        if not cls.validate_file_path(filepath):
            logging.error(f"Invalid file path: {filepath}")
            raise ValueError("Invalid file path")

        try:
            if filepath.exists():
                if filepath.stat().st_size > SecurityConfig.MAX_FILE_SIZE:
                    logging.error(f"File too large: {filepath}")
                    raise ValueError("File exceeds size limit")
                
                with filepath.open('r') as file:
                    return json.load(file)
            return {}
        except (OSError, JSONDecodeError) as e:
            logging.error(f"File read error: {type(e).__name__}")
            return {}

    @classmethod
    def safe_file_write(cls, filepath: Path, data: Dict, overwrite: bool = False) -> None:
        """Safely write to JSON file with proper error handling"""
        if not cls.validate_file_path(filepath):
            logging.error(f"Invalid file path: {filepath}")
            raise ValueError("Invalid file path")

        try:
            mode = 'w' if overwrite else 'w+'
            with filepath.open(mode) as file:
                if overwrite:
                    file.seek(0)
                    file.truncate()
                json.dump(data, file, indent=2)
                
            # Set secure file permissions
            os.chmod(filepath, 0o600)
        except OSError as e:
            logging.error(f"File write error: {type(e).__name__}")
            raise

    @classmethod
    def ask_user_for_control_variables(cls) -> Tuple[int, int, str]:
        """Get and validate study session parameters from user input"""
        prompt = ('Enter the number of reps, the length for each rep, and the subject you are studying.\n'
                 'Repetitions,minutes,subject: ')

        try:
            user_input = input(prompt).strip()
            if not user_input:
                raise ValueError("Empty input")

            parts = [part.strip() for part in user_input.split(',')]
            if len(parts) != 3:
                raise ValueError("Invalid input format")

            repetitions = cls.validate_numeric_input(
                parts[0], 
                SecurityConfig.MAX_REPETITIONS,
                "Repetitions"
            )
            minutes = cls.validate_numeric_input(
                parts[1],
                SecurityConfig.MAX_MINUTES,
                "Minutes"
            )
            subject = cls.sanitize_input(parts[2])

            if not subject:
                subject = cls.DEFAULT_SUBJECT

            return (repetitions, minutes, subject)

        except (ValueError, IndexError) as e:
            logging.warning(f"Invalid input provided: {str(e)}")
            return (cls.DEFAULT_REPETITIONS, cls.DEFAULT_MINUTES, cls.DEFAULT_SUBJECT)

    @classmethod
    def format_user_input_to_json(cls, data_structure: Tuple[int, int, str], 
                                 filename: Path, overwrite: bool = False) -> Dict:
        """Format user input into JSON structure with validation"""
        unique_id = str(uuid4())
        current_logs = {} if overwrite else cls.safe_file_read(filename)

        session = StudySession(
            name=cls.sanitize_input(data_structure[2]),
            repetitions=cls.validate_numeric_input(
                data_structure[0], 
                SecurityConfig.MAX_REPETITIONS,
                "Repetitions"
            ),
            minutes=cls.validate_numeric_input(
                data_structure[1],
                SecurityConfig.MAX_MINUTES,
                "Minutes"
            ),
            date=str(date.today())
        )

        current_logs[unique_id] = {
            "name": session.name,
            "repetitions": session.repetitions,
            "minutes": session.minutes,
            "date": session.date
        }
        return current_logs

    @classmethod
    def log_info(cls, information_tuple: Tuple[int, int, str], 
                 filename: Path, overwrite: bool = False) -> None:
        """Safely log study session information"""
        try:
            filename = Path(filename)
            data = cls.format_user_input_to_json(information_tuple, filename, overwrite)
            cls.safe_file_write(filename, data, overwrite)
            logging.info(f"Successfully logged study session to {filename}")
        except Exception as e:
            logging.error(f"Failed to log study session: {type(e).__name__}")
            raise

    @classmethod
    def run_normal_mode(cls, repetitions: int, minutes: int, 
                       subject: str, break_time: int) -> None:
        """Run normal study mode with secure input validation"""
        try:
            repetitions = cls.validate_numeric_input(
                repetitions, SecurityConfig.MAX_REPETITIONS, "Repetitions")
            minutes = cls.validate_numeric_input(
                minutes, SecurityConfig.MAX_MINUTES, "Minutes")
            break_time = cls.validate_numeric_input(
                break_time, SecurityConfig.MAX_MINUTES, "Break time")
            subject = cls.sanitize_input(subject)

            print(f'Starting study session: {minutes} minute(s), '
                  f'{repetitions} time(s), Subject: {subject}')
            
            for i in range(repetitions):
                print(f"\nSession {i + 1} of {repetitions}")
                time.sleep(minutes * 60)  # Convert to seconds
                if i < repetitions - 1:  # No break after last session
                    print(f"\nBreak time: {break_time} minutes")
                    time.sleep(break_time * 60)

        except ValueError as e:
            logging.error(f"Invalid parameters for normal mode: {str(e)}")
            raise

    @classmethod
    def run_pomodoro_mode(cls) -> Tuple[int, int, str]:
        """Run pomodoro mode with secure timing"""
        try:
            session_count = 0
            while True:
                print(f"\nPomodoro session {session_count + 1}")
                time.sleep(cls.POMODORO_SESSION_LENGTH * 60)
                
                session_count += 1
                print(f"\nBreak time: {cls.POMODORO_BREAK_TIME} minutes")
                time.sleep(cls.POMODORO_BREAK_TIME * 60)

        except KeyboardInterrupt:
            logging.info(f"Pomodoro mode ended after {session_count} sessions")
            return (session_count, cls.POMODORO_SESSION_LENGTH, "Pomodoro")

    @classmethod
    def main(cls) -> None:
        """Main application entry point with secure execution"""
        cls.setup_logging()
        logging.info("Starting StudyTimer application")

        try:
            print("Welcome! It's time to study.")
            
            # Handle CLI arguments securely
            if len(sys.argv) == 4:
                try:
                    repetitions = cls.validate_numeric_input(
                        sys.argv[1], SecurityConfig.MAX_REPETITIONS, "Repetitions")
                    minutes = cls.validate_numeric_input(
                        sys.argv[2], SecurityConfig.MAX_MINUTES, "Minutes")
                    subject = cls.sanitize_input(sys.argv[3])
                    
                    cls.log_info((repetitions, minutes, subject), cls.LOGGING_FILE)
                    cls.run_normal_mode(repetitions, minutes, subject, cls.POMODORO_BREAK_TIME)
                    return
                except ValueError as e:
                    logging.error(f"Invalid CLI arguments: {str(e)}")
                    print("Invalid command line arguments. Switching to interactive mode.")

            # Interactive mode
            print("\n1: Normal mode\n2: Pomodoro mode")
            mode = input("Choose your mode (1/2): ").strip()

            if mode == "1":
                user_input = cls.ask_user_for_control_variables()
                cls.log_info(user_input, cls.LOGGING_FILE)
                cls.run_normal_mode(*user_input, cls.POMODORO_BREAK_TIME)
            elif mode == "2":
                result = cls.run_pomodoro_mode()
                cls.log_info(result, cls.LOGGING_FILE)
            else:
                logging.warning(f"Invalid mode selected: {mode}")
                print("Invalid mode selected. Please try again.")

        except Exception as e:
            logging.error(f"Application error: {type(e).__name__}: {str(e)}")
            print("An error occurred. Please check the logs for details.")
            raise

    @classmethod
    def test(cls) -> None:
        """Test method with secure execution"""
        cls.setup_logging()
        try:
            cls.log_info((2, 2, "test"), cls.TEST_LOGGING_FILE, True)
            logging.info("Test completed successfully")
        except Exception as e:
            logging.error(f"Test failed: {type(e).__name__}: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            StudyTimer.test()
        else:
            StudyTimer.main()
    except Exception as e:
        logging.critical(f"Application failed to start: {type(e).__name__}: {str(e)}")
        sys.exit(1)
