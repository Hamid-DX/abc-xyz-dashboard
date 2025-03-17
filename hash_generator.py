import hashlib
import sys

def hash_password(password):
    """Create a SHA-256 hash of the password - identical to function in authentication.py"""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    # Check if password was provided as command line argument
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        # Otherwise prompt for password
        password = input("Enter password to hash: ")
    
    # Calculate and display the hash
    hashed = hash_password(password)
    
    print("\n======= Password Hash =======")
    print(f"Password: {password}")
    print(f"SHA-256 Hash: {hashed}")
    print("=============================")
    
    # Config snippet for easy copy-paste
    print("\nConfig file snippet:")
    print("----------------------------")
    print(f"    # Password: {password}")
    print(f"    password: {hashed}")
    print("----------------------------")