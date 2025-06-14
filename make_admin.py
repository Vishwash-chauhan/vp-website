import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin with your credentials file
cred = credentials.Certificate('firebase-auth.json')
firebase_admin.initialize_app(cred)

# The email of the user to make admin
TARGET_EMAIL = 'vishwashchauhan77@gmail.com'  # Replace with the user's email

# Make the user admin
try:
    # Get the user by email
    user = auth.get_user_by_email(TARGET_EMAIL)
    
    # Set admin privileges via custom claims
    auth.set_custom_user_claims(user.uid, {'admin': True})
    
    print(f"✅ Successfully made {TARGET_EMAIL} an admin!")
    print("🔑 Log out and log back in to the app to apply changes")
    
except Exception as e:
    print(f"❌ Error: {e}")