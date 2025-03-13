import streamlit_authenticator as stauth

# ✅ List your real passwords here
passwords = ["Hamid@123", "Nick@123"]

# ✅ Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# ✅ Print hashed passwords
for password, hash_val in zip(passwords, hashed_passwords):
    print(f"Plaintext: {password} -> Hashed: {hash_val}")
