from cryptography.fernet import Fernet
import os

key_path = 'data/secret.key'

def generate_key():
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists(key_path):
        return generate_key()
    with open(key_path, 'rb') as key_file:
        return key_file.read()

def encrypt_file(filepath):
    key = load_key()
    f = Fernet(key)

    with open(filepath, 'rb') as file:
        original = file.read()

    encrypted = f.encrypt(original)
    encrypted_path = filepath + '.enc'

    with open(encrypted_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

    return encrypted_path
