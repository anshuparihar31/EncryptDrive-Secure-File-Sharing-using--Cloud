import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

BLOCK_SIZE = 128  

# AES Encryption Function
def encrypt_file(file_content, password):
    """
    Encrypts the file content using AES encryption with CBC mode.

    :param file_content: The content of the file to be encrypted (byte format).
    :param password: The password used for deriving the encryption key.
    :return: The encrypted file content (includes IV + encrypted data).
    """
   
    iv = os.urandom(16)
 
    key = hashlib.sha256(password.encode()).digest()
    
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

   
    padder = padding.PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(file_content) + padder.finalize()

    # Encrypt the padded data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return the IV + encrypted data
    return iv + encrypted_data

# AES Decryption Function
def decrypt_file(encrypted_data, password):
    """
    Decrypts the encrypted file content using AES decryption with CBC mode.

    :param encrypted_data: The encrypted file data (includes IV + encrypted content).
    :param password: The password used for deriving the decryption key.
    :return: The decrypted file content (original content).
    """
    
    iv = encrypted_data[:16]
    
   
    key = hashlib.sha256(password.encode()).digest()
    
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()

    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()
    file_content = unpadder.update(padded_data) + unpadder.finalize()

    return file_content

# Example Usage
if __name__ == "__main__":
   
    file_content = b"This is a secret message to be encrypted."
    password = "supersecurepassword"

  
    encrypted_data = encrypt_file(file_content, password)
    print(f"Encrypted Data: {encrypted_data.hex()}")

    decrypted_data = decrypt_file(encrypted_data, password)
    print(f"Decrypted Data: {decrypted_data.decode('utf-8')}")
