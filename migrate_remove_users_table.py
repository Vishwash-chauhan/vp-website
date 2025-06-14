"""
Migration script to remove the users table from MySQL
as part of the Firebase authentication migration.

This script will:
1. Connect to the MySQL database
2. Drop the users table
3. Remove any foreign key constraints referring to users
4. Remove the user-related migrations from the alembic version history

Usage:
    python migrate_remove_users_table.py
"""

import os
import sys
import pymysql
from sqlalchemy import create_engine, text
from config import Config

def get_db_connection():
    """Connect to the database using SQLAlchemy"""
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def check_if_users_table_exists(connection):
    """Check if the users table exists in the database"""
    try:
        result = connection.execute(text("SHOW TABLES LIKE 'users'"))
        return result.rowcount > 0
    except Exception as e:
        print(f"Error checking if users table exists: {e}")
        return False

def get_foreign_key_constraints(connection):
    """Get all foreign key constraints referencing the users table"""
    try:
        # Query to find all foreign keys that reference the users table
        query = text("""
            SELECT 
                TABLE_NAME, CONSTRAINT_NAME
            FROM
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE
                REFERENCED_TABLE_NAME = 'users'
                AND TABLE_SCHEMA = DATABASE();
        """)
        
        result = connection.execute(query)
        return [(row[0], row[1]) for row in result]
    except Exception as e:
        print(f"Error getting foreign key constraints: {e}")
        return []

def drop_foreign_keys(connection, constraints):
    """Drop foreign key constraints that reference the users table"""
    if not constraints:
        print("No foreign key constraints found referencing the users table.")
        return
    
    print(f"Found {len(constraints)} foreign key constraint(s) to drop...")
    
    for table_name, constraint_name in constraints:
        try:
            print(f"Dropping foreign key {constraint_name} from table {table_name}...")
            connection.execute(text(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`;"))
            print(f"Successfully dropped constraint {constraint_name}")
        except Exception as e:
            print(f"Error dropping constraint {constraint_name}: {e}")

def drop_users_table(connection):
    """Drop the users table"""
    try:
        print("Dropping users table...")
        connection.execute(text("DROP TABLE IF EXISTS `users`;"))
        print("Successfully dropped users table")
        return True
    except Exception as e:
        print(f"Error dropping users table: {e}")
        return False

def update_migration_history(connection):
    """Update alembic migration history to remove user-related migrations"""
    try:
        # Find user-related migrations in alembic_version table
        query = text("""
            SELECT version_num FROM alembic_version 
            WHERE version_num LIKE '%user%' OR version_num LIKE '%auth%';
        """)
        
        result = connection.execute(query)
        user_migrations = [row[0] for row in result]
        
        if not user_migrations:
            print("No user-related migrations found in alembic_version table.")
            return
        
        print(f"Found {len(user_migrations)} user-related migration(s) in alembic_version table.")
        
        for migration in user_migrations:
            print(f"Removing migration {migration} from alembic_version table...")
            delete_query = text(f"DELETE FROM alembic_version WHERE version_num = '{migration}';")
            connection.execute(delete_query)
            print(f"Successfully removed migration {migration}")
    
    except Exception as e:
        print(f"Error updating migration history: {e}")

def main():
    """Main function to execute the migration"""
    print("Starting Firebase authentication migration...")
    print(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
    
    # Connect to the database
    connection = get_db_connection()
    
    # Begin transaction
    transaction = connection.begin()
    
    try:
        # Check if users table exists
        if not check_if_users_table_exists(connection):
            print("Users table does not exist. Nothing to drop.")
            return
        
        # Get foreign key constraints
        constraints = get_foreign_key_constraints(connection)
        
        # Drop foreign keys
        drop_foreign_keys(connection, constraints)
        
        # Drop users table
        if drop_users_table(connection):
            # Update migration history
            update_migration_history(connection)
            
            # Commit transaction
            transaction.commit()
            print("Migration completed successfully!")
        else:
            transaction.rollback()
            print("Migration failed. Rolling back changes.")
    except Exception as e:
        transaction.rollback()
        print(f"An error occurred during migration: {e}")
        print("Rolling back all changes.")

if __name__ == "__main__":
    main()
