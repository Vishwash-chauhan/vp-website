"""
Featured Experts Migration Script
Adds featured functionality to the Expert model
"""

import sqlite3
import os
from datetime import datetime

def migrate_featured_experts():
    """Add featured columns to experts table"""
      # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'site.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(experts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        # Add is_featured column if it doesn't exist
        if 'is_featured' not in columns:
            cursor.execute("ALTER TABLE experts ADD COLUMN is_featured BOOLEAN DEFAULT 0")
            print("✅ Added is_featured column")
            changes_made = True
        else:
            print("ℹ️  is_featured column already exists")
        
        # Add featured_position column if it doesn't exist
        if 'featured_position' not in columns:
            cursor.execute("ALTER TABLE experts ADD COLUMN featured_position INTEGER")
            print("✅ Added featured_position column")
            changes_made = True
        else:
            print("ℹ️  featured_position column already exists")
        
        # Add featured_at column if it doesn't exist
        if 'featured_at' not in columns:
            cursor.execute("ALTER TABLE experts ADD COLUMN featured_at DATETIME")
            print("✅ Added featured_at column")
            changes_made = True
        else:
            print("ℹ️  featured_at column already exists")
        
        # Commit changes
        if changes_made:
            conn.commit()
            print("✅ Database migration completed successfully!")
        else:
            print("ℹ️  No migration needed - all columns already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting Featured Experts Migration...")
    print("=" * 50)
    
    success = migrate_featured_experts()
    
    print("=" * 50)
    if success:
        print("✅ Migration completed! You can now use featured experts functionality.")
        print("\n📋 Next steps:")
        print("1. Run your Flask app: python run.py")
        print("2. Go to Dashboard > Expert Management")
        print("3. Click the star icon to feature experts")
        print("4. Check the homepage to see featured experts")
    else:
        print("❌ Migration failed! Please check the error messages above.")
