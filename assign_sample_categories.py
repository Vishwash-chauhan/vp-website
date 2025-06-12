#!/usr/bin/env python3
"""
Script to assign sample categories to existing experts for testing
"""

from app import create_app, db
from app.models import Expert, Category

def assign_sample_categories():
    app = create_app()
    with app.app_context():
        try:
            experts = Expert.query.all()
            categories = Category.query.all()
            
            if not experts:
                print("No experts found in database")
                return
            
            if not categories:
                print("No categories found in database")
                return
            
            print(f"Found {len(experts)} experts and {len(categories)} categories")
            
            # Sample category assignments for demonstration
            assignments = [
                # Expert 1 - Business Development, Marketing & Sales
                (0, ['Business Development', 'Marketing & Sales']),
                # Expert 2 - Technology & IT, Data Science & Analytics
                (1, ['Technology & IT', 'Data Science & Analytics']),
                # Expert 3 - Finance & Accounting, Consulting
                (2, ['Finance & Accounting', 'Consulting']),
                # Expert 4 - Operations & Management, Human Resources
                (3, ['Operations & Management', 'Human Resources'])
            ]
            
            for expert_idx, category_names in assignments:
                if expert_idx < len(experts):
                    expert = experts[expert_idx]
                    expert_categories = []
                    
                    for cat_name in category_names:
                        category = Category.query.filter_by(name=cat_name).first()
                        if category:
                            expert_categories.append(category)
                    
                    expert.categories = expert_categories
                    print(f"Assigned {len(expert_categories)} categories to {expert.name}")
            
            db.session.commit()
            print("\n✅ Sample category assignments completed successfully!")
            
            # Print final state
            print("\nFinal expert-category assignments:")
            for expert in experts:
                cat_names = [c.name for c in expert.categories]
                print(f"- {expert.name}: {', '.join(cat_names) if cat_names else 'No categories'}")
            
        except Exception as e:
            print(f"❌ Error assigning categories: {e}")
            db.session.rollback()

if __name__ == '__main__':
    assign_sample_categories()
