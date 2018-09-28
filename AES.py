from Crypto.Cipher import AES
from pkcs7 import PKCS7Encoder
from os import urandom

encoder = PKCS7Encoder()


def encrypt(plaintext):
    key = urandom(16)
    iv = urandom(16)
    encryption_suite = AES.new(key, AES.MODE_CBC, iv)
    pad = encoder.encode(plaintext)
    cipher_text = encryption_suite.encrypt(pad.encode())
    return key, cipher_text, iv


def decrypt(ciphertext, key, iv):
    decryption_suite = AES.new(key, AES.MODE_CBC, iv)
    padded = decryption_suite.decrypt(ciphertext)
    return encoder.decode(padded.decode())