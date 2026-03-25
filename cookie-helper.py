#!/usr/bin/env python3
"""Read Chrome's sessionKey cookie for claude.ai and print it as JSON."""
import sqlite3, os, shutil, tempfile, json, sys

COOKIE_PATHS = [
    '~/.config/google-chrome/Default/Cookies',
    '~/.config/google-chrome/Profile 1/Cookies',
    '~/.config/google-chrome/Profile 2/Cookies',
    '~/.config/chromium/Default/Cookies',
]


def _decrypt_aes_cbc(encrypted, password):
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA1(), length=16,
            salt=b'saltysalt', iterations=1,
            backend=default_backend(),
        )
        key = kdf.derive(password if isinstance(password, bytes) else password.encode())
        iv = b' ' * 16
        dec = Cipher(algorithms.AES(key), modes.CBC(iv),
                     backend=default_backend()).decryptor()
        raw = dec.update(encrypted) + dec.finalize()
        pad = raw[-1]
        return raw[:-pad].decode('utf-8')
    except Exception as e:
        return None


def _gnome_keyring_password():
    try:
        import secretstorage
        bus = secretstorage.dbus_init()
        col = secretstorage.get_default_collection(bus)
        for item in col.get_all_items():
            if 'Safe Storage' in item.get_label():
                return item.get_secret()
    except Exception:
        pass
    return None


def main():
    db_path = next(
        (os.path.expanduser(p) for p in COOKIE_PATHS if os.path.exists(os.path.expanduser(p))),
        None,
    )
    if not db_path:
        print(json.dumps({'error': 'Chrome cookie file not found'}))
        return

    tmp = tempfile.mktemp(suffix='.sqlite')
    try:
        shutil.copy2(db_path, tmp)
    except Exception as e:
        print(json.dumps({'error': f'Cannot copy cookie file: {e}'}))
        return

    try:
        conn = sqlite3.connect(tmp)
        c = conn.cursor()
        c.execute(
            'SELECT encrypted_value FROM cookies '
            'WHERE host_key LIKE "%claude.ai%" AND name = "sessionKey" '
            'ORDER BY expires_utc DESC LIMIT 1'
        )
        row = c.fetchone()
        conn.close()
    except Exception as e:
        print(json.dumps({'error': f'SQLite error: {e}'}))
        return
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass

    if not row:
        print(json.dumps({'error': 'sessionKey cookie not found — make sure you are logged in to claude.ai in Chrome'}))
        return

    enc = row[0]
    if isinstance(enc, str):
        enc = enc.encode('latin-1')

    prefix = enc[:3]
    body   = enc[3:]

    if prefix == b'v10':
        key = _decrypt_aes_cbc(body, b'peanuts')
    elif prefix == b'v11':
        password = _gnome_keyring_password()
        if password is None:
            print(json.dumps({'error': 'Could not read Chrome Safe Storage key from GNOME keyring — install python3-secretstorage'}))
            return
        key = _decrypt_aes_cbc(body, password)
    else:
        # Unencrypted (rare)
        key = enc.decode('utf-8', errors='replace')

    if key:
        print(json.dumps({'key': key}))
    else:
        print(json.dumps({'error': 'Decryption failed — install python3-cryptography'}))


main()
