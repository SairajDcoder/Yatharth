from werkzeug.security import generate_password_hash

# --- IMPORTANT ---
# 1. Enter the password you want for your admin user here.
# 2. Run this script from your terminal: python hash_password.py
# 3. Copy the entire long output string.

password_to_hash = "sai@9090"
hashed_password = generate_password_hash(
    password_to_hash, method='pbkdf2:sha256', salt_length=16)

print("\n--- COPY THE HASHED PASSWORD BELOW ---\n")
print(hashed_password)
print("\n---------------------------------------\n")
