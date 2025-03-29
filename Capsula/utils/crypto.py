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


def generate_doc(original_filename, encrypted_filename):
    doc_text = f"""
CAPSULA DEL TIEMPO - DOCUMENTACIÓN

Archivo original: {original_filename}
Archivo cifrado: {encrypted_filename}
Método de cifrado: Fernet (criptografía simétrica)
Librería usada: cryptography (Python)

Instrucciones:
Para descifrar el archivo, se necesita el archivo .enc y la clave secreta original.
Puedes usar la función decrypt_file() desde este mismo sistema.

Advertencia:
El contenido ha sido cifrado por seguridad y no puede ser interpretado sin la clave.
    """
    doc_filename = os.path.splitext(encrypted_filename)[0] + '_info.txt'
    with open(doc_filename, 'w') as f:
        f.write(doc_text.strip())
    return doc_filename
