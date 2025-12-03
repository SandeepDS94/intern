from utils import supabase
import time

def create_admin():
    email = "admin@internship.com"  # Using a standard domain
    password = "Welcome@123"
    
    print(f"Attempting to create admin user: {email}")
    
    try:
        # Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": "System Admin",
                    "role": "company" # Companies act as admins
                }
            }
        })
        
        if response.user:
            print("User created successfully!")
            print(f"ID: {response.user.id}")
            print(f"Email: {response.user.email}")
            print("Please check your email for a confirmation link if Supabase requires it.")
        else:
            print("User creation returned no user object. They might already exist.")
            
    except Exception as e:
        print(f"Error creating user: {e}")

if __name__ == "__main__":
    create_admin()
