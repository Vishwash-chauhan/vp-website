#!/usr/bin/env python3
"""
Database migration script to add categories system
"""

from app import create_app, db
from app.models import Category, Expert
from sqlalchemy import text

def run_migration():
    app = create_app()
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created/updated successfully")
            
            # Check if categories table exists and is empty
            result = db.session.execute(text('SELECT COUNT(*) FROM categories')).scalar()
            
            if result == 0:
                # Insert default categories
                categories_data = [
                    ('Business Development', 'Business strategy, growth, and development consulting'),
                    ('Marketing & Sales', 'Digital marketing, sales strategies, and customer acquisition'),
                    ('Finance & Accounting', 'Financial planning, accounting, and investment advice'),
                    ('Technology & IT', 'Software development, IT consulting, and digital transformation'),
                    ('Operations & Management', 'Process optimization, team management, and operations'),
                    ('Legal & Compliance', 'Legal advice, compliance, and regulatory matters'),
                    ('Human Resources', 'HR management, recruitment, and talent development'),
                    ('Consulting', 'General business consulting and advisory services'),
                    ('Data Science & Analytics', 'Data analysis, machine learning, and business intelligence'),
                    ('Digital Marketing', 'Social media, SEO, content marketing, and online advertising'),
                    ('Product Management', 'Product strategy, development, and lifecycle management'),
                    ('Design & Creative', 'UI/UX design, graphic design, and creative solutions')
                ]
                
                for name, description in categories_data:
                    category = Category(name=name, description=description)
                    db.session.add(category)
                
                db.session.commit()
                print(f"✅ Added {len(categories_data)} categories to the database")
            else:
                print(f"ℹ️  Categories table already has {result} records")
            
            # Verify expert_categories table exists
            try:
                result = db.session.execute(text('SELECT COUNT(*) FROM expert_categories')).scalar()
                print(f"✅ Expert-categories junction table working ({result} relationships)")
            except Exception as e:
                print(f"⚠️  Expert-categories table issue: {e}")
            
            print("\n🎉 Categories system migration completed successfully!")
            print("\nNext steps:")
            print("1. Restart your Flask application")
            print("2. Go to the admin dashboard")
            print("3. Edit experts to assign categories")
            print("4. Test category filtering on the experts page")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    run_migration()
