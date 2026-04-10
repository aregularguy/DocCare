"""Database connection manager for DentNest application."""
import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls):
        """Singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database manager."""
        if self._connection is None:
            self._setup_database()

    def _setup_database(self):
        """Set up database connection and enable foreign keys."""
        import sys
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller .exe — store DB next to the .exe, not in temp folder
            project_root = Path(sys.executable).parent
        else:
            # Running from source
            project_root = Path(__file__).parent.parent.parent
        db_dir = project_root / 'data'

        # Create data directory if it doesn't exist
        db_dir.mkdir(exist_ok=True)

        db_path = db_dir / 'dentnest.db'

        logger.info(f"Connecting to database at: {db_path}")

        # Create connection with row factory for dict-like access
        self._connection = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            timeout=30.0
        )

        # Enable foreign key constraints
        self._connection.execute("PRAGMA foreign_keys = ON")

        # Enable WAL mode for better concurrent performance
        self._connection.execute("PRAGMA journal_mode = WAL")

        # Set row factory for dict-like access
        self._connection.row_factory = sqlite3.Row

        logger.info("Database connection established successfully")

    def get_connection(self) -> sqlite3.Connection:
        """Get the database connection.

        Returns:
            SQLite connection object
        """
        if self._connection is None:
            self._setup_database()
        return self._connection

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single query.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Cursor object with query results
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except Exception:
            conn.rollback()
            raise

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Cursor object
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor
        except Exception:
            conn.rollback()
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch single row from query.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Single row or None
        """
        cursor = self.get_connection().cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Fetch all rows from query.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of rows
        """
        cursor = self.get_connection().cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
