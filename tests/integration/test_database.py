"""
Integration tests for database operations.

This module contains integration tests that interact with a PostgreSQL database.
"""

import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Database connection parameters - would typically come from environment variables
DB_PARAMS = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'qa_user'),
    'password': os.getenv('DB_PASSWORD', 'qa_password'),
    'database': os.getenv('DB_NAME', 'qa_db')
}


@pytest.fixture(scope="module")
def db_connection():
    """Create a database connection for testing."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host=DB_PARAMS['host'],
        port=DB_PARAMS['port'],
        user=DB_PARAMS['user'],
        password=DB_PARAMS['password'],
        database=DB_PARAMS['database']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create a test table
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    yield conn
    
    # Clean up after tests
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS test_users")
    
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """Create a database cursor for executing queries."""
    cursor = db_connection.cursor()
    yield cursor
    
    # Clean up test data after each test
    cursor.execute("DELETE FROM test_users")
    cursor.close()


def test_insert_user(db_cursor):
    """Test inserting a user into the database."""
    # Insert a user
    db_cursor.execute(
        "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id",
        ("testuser", "test@example.com")
    )
    user_id = db_cursor.fetchone()[0]
    
    # Verify the user was inserted
    db_cursor.execute("SELECT username, email FROM test_users WHERE id = %s", (user_id,))
    user = db_cursor.fetchone()
    
    assert user is not None
    assert user[0] == "testuser"
    assert user[1] == "test@example.com"


def test_update_user(db_cursor):
    """Test updating a user in the database."""
    # Insert a user
    db_cursor.execute(
        "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id",
        ("updateuser", "update@example.com")
    )
    user_id = db_cursor.fetchone()[0]
    
    # Update the user
    db_cursor.execute(
        "UPDATE test_users SET email = %s WHERE id = %s",
        ("updated@example.com", user_id)
    )
    
    # Verify the user was updated
    db_cursor.execute("SELECT email FROM test_users WHERE id = %s", (user_id,))
    email = db_cursor.fetchone()[0]
    
    assert email == "updated@example.com"


def test_delete_user(db_cursor):
    """Test deleting a user from the database."""
    # Insert a user
    db_cursor.execute(
        "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id",
        ("deleteuser", "delete@example.com")
    )
    user_id = db_cursor.fetchone()[0]
    
    # Delete the user
    db_cursor.execute("DELETE FROM test_users WHERE id = %s", (user_id,))
    
    # Verify the user was deleted
    db_cursor.execute("SELECT * FROM test_users WHERE id = %s", (user_id,))
    user = db_cursor.fetchone()
    
    assert user is None


def test_unique_constraint(db_cursor):
    """Test that the unique constraint on username works."""
    # Insert a user
    db_cursor.execute(
        "INSERT INTO test_users (username, email) VALUES (%s, %s)",
        ("uniqueuser", "unique@example.com")
    )
    
    # Try to insert another user with the same username
    with pytest.raises(psycopg2.IntegrityError) as excinfo:
        db_cursor.execute(
            "INSERT INTO test_users (username, email) VALUES (%s, %s)",
            ("uniqueuser", "another@example.com")
        )
    
    assert "duplicate key value violates unique constraint" in str(excinfo.value)