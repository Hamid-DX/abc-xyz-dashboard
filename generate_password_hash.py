import hashlib
import getpass

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    # Get password input (hidden)
    print("Password Hasher for ABC-XYZ Dashboard")
    print("-" * 40)
    
    try:
        password = getpass.getpass("Enter password to hash: ")
        hashed = hash_password(password)
        
        print("\nPassword Hash (copy this to your config.yaml):")
        print("-" * 40)
        print(hashed)
        print("-" * 40)
    except Exception as e:
        print(f"Error: {e}")
    
    # Allow for multiple password generation
    while True:
        try:
            choice = input("\nHash another password? (y/n): ")
            if choice.lower() != 'y':
                break
                
            password = getpass.getpass("Enter password to hash: ")
            hashed = hash_password(password)
            
            print("\nPassword Hash (copy this to your config.yaml):")
            print("-" * 40)
            print(hashed)
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
            
    print("\nDone!")