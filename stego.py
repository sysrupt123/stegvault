import base64
import os
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _make_key(password, salt):
    # Turns a human password into a strong 32-byte encryption key
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(message, password):
    salt = os.urandom(16)  # random salt, stored with the data
    token = Fernet(_make_key(password, salt)).encrypt(message.encode())
    return salt + token


def decrypt(data, password):
    salt, token = data[:16], data[16:]
    # raises InvalidToken if the password is wrong
    return Fernet(_make_key(password, salt)).decrypt(token).decode()


def hide(image_path, out_path, message, password):
    img = Image.open(image_path).convert("RGB")
    payload = encrypt(message, password)
    data = len(payload).to_bytes(4, "big") + payload  # 4-byte length header
    bits = "".join(f"{b:08b}" for b in data)

    pixels = bytearray(img.tobytes())
    if len(bits) > len(pixels):
        raise ValueError("Message too long for this image")

    for i, bit in enumerate(bits):
        # overwrite the last bit of each color value (invisible to the eye)
        pixels[i] = (pixels[i] & 0xFE) | int(bit)

    Image.frombytes("RGB", img.size, bytes(pixels)).save(out_path, "PNG")


def _read_bytes(pixels, start_bit, count):
    out = bytearray()
    for i in range(count):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | (pixels[start_bit + i * 8 + j] & 1)
        out.append(byte)
    return bytes(out)


def reveal(image_path, password):
    pixels = Image.open(image_path).convert("RGB").tobytes()
    length = int.from_bytes(_read_bytes(pixels, 0, 4), "big")
    if length <= 0 or 32 + length * 8 > len(pixels):
        raise ValueError("No hidden message found")
    payload = _read_bytes(pixels, 32, length)
    return decrypt(payload, password)
