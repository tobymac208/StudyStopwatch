#!/usr/bin/env python3

import json
import sys
import time
import logging
import sqlite3
import traceback
from datetime import date, datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
from uuid import uuid4
import re
import os
from dataclasses import dataclass
from contextlib import contextmanager

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
    """A secure study timer application supporting normal and pomodoro modes"""
    
    # Base paths and database
    BASE_DIR = Path(__file__).parent.resolve()
    DB_PATH = BASE_DIR / "study_timer.db"
    
    # Application defaults
    DEFAULT_REPETITIONS = 3
    DEFAULT_MINUTES = 30
    DEFAULT_SUBJECT = "Unspecified"
    
    # Pomodoro settings
    POMODORO_SESSION_LENGTH = 25  # minutes
    POMODORO_BREAK_TIME = 5  # minutes

    @staticmethod
    @contextmanager
    def get_db_connection():
        """Secure database connection context manager"""
        conn = None
        try:
            conn = sqlite3.connect(StudyTimer.DB_PATH)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @classmethod
    def setup_database(cls):
        """Initialize database tables"""
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS study_sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            repetitions INTEGER NOT NULL,
            minutes INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_runtime_logs_table = """
        CREATE TABLE IF NOT EXISTS runtime_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_temp_sessions_table = """
        CREATE TABLE IF NOT EXISTS temp_sessions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            repetitions INTEGER NOT NULL,
            minutes INTEGER NOT NULL
        );
        """
        
        with cls.get_db_connection() as conn:
            conn.execute(create_sessions_table)
            conn.execute(create_runtime_logs_table)
            conn.execute(create_temp_sessions_table)

    class DatabaseHandler(logging.Handler):
        """Custom logging handler for SQLite database"""
        def emit(self, record):
            try:
                with StudyTimer.get_db_connection() as conn:
                    conn.execute(
                        "INSERT INTO runtime_logs (level, message, timestamp) VALUES (?, ?, ?)",
                        (record.levelname, record.getMessage(), datetime.now())
                    )
            except Exception:
                self.handleError(record)
    @classmethod
    def setup_logging(cls) -> None:
        """Configure logging with database handler"""
        # Create and initialize the database
        cls.setup_database()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                # Database handler for all logs
                cls.DatabaseHandler(),
                # Keep console output for errors only
                logging.StreamHandler(sys.stderr)
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
    def log_info(cls, information_tuple: Tuple[int, int, str], 
                 is_temporary: bool = False) -> None:
        """Log study session information to database"""
        try:
            repetitions, minutes, subject = information_tuple
            
            # Validate inputs
            repetitions = cls.validate_numeric_input(
                repetitions, SecurityConfig.MAX_REPETITIONS, "Repetitions")
            minutes = cls.validate_numeric_input(
                minutes, SecurityConfig.MAX_MINUTES, "Minutes")
            subject = cls.sanitize_input(subject)
            
            # Only log permanent sessions (not temporary crash recovery)
            if not is_temporary:
                with cls.get_db_connection() as conn:
                    conn.execute("""
                        INSERT INTO study_sessions (id, name, repetitions, minutes, date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(uuid4()), subject, repetitions, minutes, str(date.today())))
                    logging.info(f"Successfully logged study session for {subject}")
            
            # For temporary crash recovery, store in temp_sessions table
            else:
                with cls.get_db_connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO temp_sessions (id, name, repetitions, minutes)
                        VALUES (1, ?, ?, ?)
                    """, (subject, repetitions, minutes))
                    
        except Exception as e:
            logging.error(f"Failed to log study session: {type(e).__name__}")
            raise
    @classmethod
    def run_normal_mode(cls, repetitions: int, minutes: int, 
                       subject: str, break_time: int) -> None:
        """Run normal study mode with database logging"""
        try:
            repetitions = cls.validate_numeric_input(
                repetitions, SecurityConfig.MAX_REPETITIONS, "Repetitions")
            minutes = cls.validate_numeric_input(
                minutes, SecurityConfig.MAX_MINUTES, "Minutes")
            break_time = cls.validate_numeric_input(
                break_time, SecurityConfig.MAX_MINUTES, "Break time")
            subject = cls.sanitize_input(subject)

            logging.info(f'Starting study session: {minutes} minute(s), '
                        f'{repetitions} time(s), Subject: {subject}')
            
            for i in range(repetitions):
                logging.info(f"Session {i + 1} of {repetitions}")
                
                # Session countdown
                for minute in range(minutes, 0, -1):
                    logging.info(f"Minutes remaining: {minute}")
                    # Log temporary progress
                    cls.log_info((repetitions - i, minute, subject), is_temporary=True)
                    time.sleep(60)
                
                if i < repetitions - 1:  # No break after last session
                    logging.info(f"Break time: {break_time} minutes")
                    # Break countdown
                    for minute in range(break_time, 0, -1):
                        logging.info(f"Break minutes remaining: {minute}")
                        time.sleep(60)

        except ValueError as e:
            logging.error(f"Invalid parameters for normal mode: {str(e)}")
            raise

    @classmethod
    def run_pomodoro_mode(cls) -> Tuple[int, int, str]:
        """Run pomodoro mode with database logging"""
        try:
            session_count = 0
            while True:
                logging.info(f"Pomodoro session {session_count + 1}")
                
                for minute in range(cls.POMODORO_SESSION_LENGTH, 0, -1):
                    logging.info(f"Minutes remaining: {minute}")
                    # Log temporary progress
                    cls.log_info((session_count + 1, minute, "Pomodoro"), is_temporary=True)
                    time.sleep(60)
                
                session_count += 1
                logging.info(f"Break time: {cls.POMODORO_BREAK_TIME} minutes")
                
                # Break countdown
                for minute in range(cls.POMODORO_BREAK_TIME, 0, -1):
                    logging.info(f"Break minutes remaining: {minute}")
                    time.sleep(60)

        except KeyboardInterrupt:
            logging.info(f"Pomodoro mode ended after {session_count} sessions")
            return (session_count, cls.POMODORO_SESSION_LENGTH, "Pomodoro")

    @classmethod
    def get_study_history(cls) -> List[Dict]:
        """Retrieve study session history"""
        with cls.get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM study_sessions 
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_runtime_logs(cls, limit: int = 100) -> List[Dict]:
        """Retrieve recent runtime logs"""
        with cls.get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM runtime_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def main(cls) -> None:
        """Main application entry point with secure execution"""
        cls.setup_logging()
        logging.info("Starting StudyTimer application")

        try:
            print("Welcome! It's time to study.")
            
            # Handle CLI arguments
            if len(sys.argv) == 4:
                try:
                    repetitions = cls.validate_numeric_input(
                        sys.argv[1], SecurityConfig.MAX_REPETITIONS, "Repetitions")
                    minutes = cls.validate_numeric_input(
                        sys.argv[2], SecurityConfig.MAX_MINUTES, "Minutes")
                    subject = cls.sanitize_input(sys.argv[3])
                    
                    cls.log_info((repetitions, minutes, subject))
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
                cls.log_info(user_input)
                cls.run_normal_mode(*user_input, cls.POMODORO_BREAK_TIME)
            elif mode == "2":
                result = cls.run_pomodoro_mode()
                cls.log_info(result)
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
            cls.log_info((2, 2, "test"))
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