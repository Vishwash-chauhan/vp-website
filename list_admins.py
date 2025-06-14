# list_admins.py
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin
cred = credentials.Certificate('firebase-auth.json')
firebase_admin.initialize_app(cred)

def list_admin_users():
    # Get all users (paginated)
    admin_users = []
    page = auth.list_users()
    
    while page:
        for user in page.users:
            # Check if user has admin claim
            claims = user.custom_claims or {}
            if claims.get('admin') == True:
                admin_users.append({
                    'email': user.email,
                    'uid': user.uid,
                    'display_name': user.display_name
                })
        
        # Get next page
        page = page.get_next_page()
    
    # Print results
    if admin_users:
        print("\n===== ADMIN USERS =====")
        for i, admin in enumerate(admin_users):
            print(f"{i+1}. Email: {admin['email']}")
            print(f"   Name: {admin['display_name'] or 'Not set'}")
            print(f"   UID: {admin['uid']}")
            print("------------------------")
        print(f"Total admin users: {len(admin_users)}")
    else:
        print("No admin users found!")

# Run the function
list_admin_users()