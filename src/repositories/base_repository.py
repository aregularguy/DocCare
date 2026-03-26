"""Base repository with generic CRUD operations."""
from typing import Optional, List, TypeVar, Generic, Type
from ..database.db_manager import DatabaseManager

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository providing generic CRUD operations."""

    def __init__(self, table_name: str, model_class: Type[T]):
        """Initialize repository.

        Args:
            table_name: Database table name
            model_class: Model class with from_db_row method
        """
        self.table_name = table_name
        self.model_class = model_class
        self.db = DatabaseManager()

    def create(self, **kwargs) -> int:
        """Create a new record.

        Args:
            **kwargs: Field names and values

        Returns:
            ID of created record
        """
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        values = tuple(kwargs.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        cursor = self.db.execute(query, values)
        return cursor.lastrowid

    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        row = self.db.fetch_one(query, (id,))
        return self.model_class.from_db_row(row) if row else None

    def get_all(self) -> List[T]:
        """Get all records.

        Returns:
            List of model instances
        """
        query = f"SELECT * FROM {self.table_name}"
        rows = self.db.fetch_all(query)
        return [self.model_class.from_db_row(row) for row in rows]

    def update(self, id: int, **kwargs) -> bool:
        """Update a record.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            True if updated successfully
        """
        if not kwargs:
            return False

        set_clause = ', '.join(f"{field} = ?" for field in kwargs.keys())
        values = tuple(kwargs.values()) + (id,)

        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        cursor = self.db.execute(query, values)
        return cursor.rowcount > 0

    def delete(self, id: int) -> bool:
        """Delete a record.

        Args:
            id: Record ID

        Returns:
            True if deleted successfully
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        cursor = self.db.execute(query, (id,))
        return cursor.rowcount > 0

    def count(self) -> int:
        """Count total records.

        Returns:
            Number of records
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        row = self.db.fetch_one(query)
        return row['count'] if row else 0

    def exists(self, id: int) -> bool:
        """Check if record exists.

        Args:
            id: Record ID

        Returns:
            True if exists
        """
        query = f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1"
        row = self.db.fetch_one(query, (id,))
        return row is not None
