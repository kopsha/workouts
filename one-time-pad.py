#!/usr/bin/env python3
from itertools import cycle, chain


OFFSET = ord("A")


def otp_encrypt(message: str, key: str):
    """Encrypts message using OTP cipher"""
    kn = len(key)
    cipher = list()
    for i, c in enumerate(message):
        if c.isalpha():
            left = ord(c) - OFFSET
            right = ord(key[i % kn]) - OFFSET
            k = key[i % kn]
            print(c, left, right, k)
            enc_c = chr((left + right) % 26 + OFFSET)
            cipher.append(enc_c)
        else:
            cipher.append(c)

    return "".join(cipher)

def otp_decrypt(ciphertext, known):
    """Decrypts OTP ciphertext given a known secret"""




    return None


def test():

    original_message = "SECRET YOUR PHONE HAS BEEN TAPPED"
    encrypted_message = "TGFVJZ FWDB ATBBT XRK UYZJ QYOPFF"


    print("Encrypted message:", encrypted_message)
    print(otp_decrypt(encrypted_message, "SECRET"))

    # encrypted = otp_encrypt(original_message, "SECRET")
    # print(original_message, encrypted)


if __name__ == "__main__":
    test()

# if __name__ == "__main__":
#     text = ""
#     clear_text = decrypt(text, shared_secret="SECRET")
#     print(f"{text} => {clear_text}")
