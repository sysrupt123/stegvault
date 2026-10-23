# StegVault

A small web app that encrypts a message with a password and hides it inside an
image. Everything runs locally; nothing is uploaded anywhere.

## Why I built it
I built this project while exploring cybersecurity and encryption.I wanted to try something practical instead of just learning thoery and to improve my Python skills and understand how messages could be protected using img.

## How it works
1. The message is encrypted with Fernet (AES-based). The key is derived from
   your password with PBKDF2-HMAC-SHA256 and a random salt.
2. The encrypted bytes are hidden in the least significant bit of each pixel
   colour value (LSB steganography). This changes each colour by at most 1/255,
   which the eye can't see.
3. The output is always PNG, because JPEG compression would destroy the bits.

## Run it
```bash
git clone https://github.com/sysrupt123/stegvault.git
cd stegvault
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Try `samples/hidden.png` with password `demo1234`.

## Security notes
- Upload size capped at 5 MB; uploaded filenames are never used or saved.
- Revealed text is HTML-escaped by Jinja2 (hidden content is attacker-controlled).
- Same error for wrong password and "no message", so it doesn't leak which.
- Runs on localhost with debug off.

## Limitations
- Weak passwords can be guessed offline; the encryption is only as strong as the password.
- LSB hiding is detectable by steganalysis tools. Encryption protects the
  content, but this is not undetectable hiding.
- Recompression (WhatsApp photos, Instagram) destroys the hidden data. Send as a file.
- Not audited; don't use it for high-stakes secrets.

## Built with
Python, Flask, Pillow, cryptography. Written with AI assistance (Claude), which I
used to learn and build; I reviewed and understand the code.

## License
MIT
