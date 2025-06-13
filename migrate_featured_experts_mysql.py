"""
MySQL Featured Experts Migration Script
Adds featured functionality columns to the experts table
"""

import pymysql
import os
from datetime import datetime

def migrate_featured_experts_mysql():
    """Add featured columns to experts table in MySQL"""
    
    try:
        # Database connection parameters
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='vyapaarniti_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("🔗 Connected to MySQL database successfully!")
        
        with connection.cursor() as cursor:
            # Check if columns already exist
            cursor.execute("DESCRIBE experts")
            columns = [row['Field'] for row in cursor.fetchall()]
            
            changes_made = False
            
            # Add is_featured column if it doesn't exist
            if 'is_featured' not in columns:
                cursor.execute("ALTER TABLE experts ADD COLUMN is_featured BOOLEAN DEFAULT FALSE")
                print("✅ Added is_featured column")
                changes_made = True
            else:
                print("ℹ️  is_featured column already exists")
            
            # Add featured_position column if it doesn't exist
            if 'featured_position' not in columns:
                cursor.execute("ALTER TABLE experts ADD COLUMN featured_position INT")
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
                connection.commit()
                print("✅ Database migration completed successfully!")
            else:
                print("ℹ️  No migration needed - all columns already exist")
        
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        return False
        
    finally:
        if connection:
            connection.close()
            print("🔗 Database connection closed")

if __name__ == "__main__":
    print("🚀 Starting Featured Experts MySQL Migration...")
    print("=" * 60)
    
    success = migrate_featured_experts_mysql()
    
    print("=" * 60)
    if success:
        print("✅ Migration completed! You can now use featured experts functionality.")
        print("\n📋 Next steps:")
        print("1. Run your Flask app: python run.py")
        print("2. Go to Dashboard > Expert Management")
        print("3. Click the star icon to feature experts")
        print("4. Check the homepage to see featured experts")
    else:
        print("❌ Migration failed! Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check database credentials in config.py")
        print("3. Ensure vyapaarniti_db database exists")
