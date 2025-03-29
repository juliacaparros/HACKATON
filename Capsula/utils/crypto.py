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

def decrypt_file(encrypted_path, key_path):
    # Leer la clave secreta
    with open(key_path, 'rb') as f:
        key = f.read()

    fernet = Fernet(key)

    # Leer datos cifrados
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()

    # Desencriptar los datos
    decrypted_data = fernet.decrypt(encrypted_data)

    # Crear nombre de archivo restaurado
    decrypted_path = encrypted_path.replace('.enc', '.restaurado')

    # Guardar archivo desencriptado
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)

    return decrypted_path


def generate_doc(original_filename, encrypted_filename):
    doc_text = f"""
CAPSULA DEL TIEMPO - DOCUMENTACIÓN

Archivo original: {original_filename}
Archivo cifrado: {encrypted_filename}
Método de cifrado: Fernet (criptografía simétrica)
Librería usada: cryptography (Python)

----------------------------------------------
ESPAÑOL 🇪🇸
Para descifrar este archivo, necesitas el archivo .enc y la clave secreta.
Utiliza una herramienta compatible con Fernet (Python 'cryptography').

----------------------------------------------
ENGLISH 🇬🇧
To decrypt this file, you need the .enc file and the secret key.
Use a tool compatible with Fernet (Python 'cryptography').

----------------------------------------------
FRANÇAIS 🇫🇷
Pour déchiffrer ce fichier, vous avez besoin du fichier .enc et de la clé secrète.
Utilisez un outil compatible avec Fernet (librairie Python 'cryptography').

----------------------------------------------
中文 🇨🇳
要解密此文件，您需要 .enc 文件和密钥。
请使用与 Fernet（Python 'cryptography' 库）兼容的工具。

----------------------------------------------
العربية 🇸🇦
لفك تشفير هذا الملف، تحتاج إلى ملف .enc والمفتاح السري.
استخدم أداة متوافقة مع Fernet (مكتبة Python 'cryptography').

    """

    doc_filename = os.path.splitext(encrypted_filename)[0] + '_info.txt'
    doc_path = os.path.join('data', os.path.basename(doc_filename))

    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_text.strip())

    return doc_path
