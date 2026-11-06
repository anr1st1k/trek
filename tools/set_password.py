# -*- coding: utf-8 -*-
"""Сменить пароль своего плана.

Запуск из папки репозитория (рядом с index.html):
    pip install cryptography
    python3 tools/set_password.py

Скрипт спросит логин, старый и новый пароль и перезапишет свой файл в plans/.
Потом загрузи этот файл в репозиторий. Каждое устройство один раз попросит войти заново;
прогресс в Gist перешифруется при следующей синхронизации.
"""
import base64, getpass, hashlib, json, os, secrets, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
def key(pw, salt, it): return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw.encode())

login = input("Логин: ").strip().lower()
rel = "plans/" + hashlib.sha256(("trek|" + login).encode()).hexdigest()[:20] + ".enc"
path = os.path.join(ROOT, rel)
if not os.path.exists(path): sys.exit("Плана для этого логина нет.")
enc = json.load(open(path))
old = getpass.getpass("Старый пароль: ")
try:
    plain = AESGCM(key(old, base64.b64decode(enc["salt"]), enc["iter"])).decrypt(base64.b64decode(enc["iv"]), base64.b64decode(enc["ct"]), None)
except Exception:
    sys.exit("Старый пароль не подошёл.")
new = getpass.getpass("Новый пароль (не короче 12 символов): ")
if len(new) < 12: sys.exit("Слишком короткий пароль.")
if new != getpass.getpass("Ещё раз: "): sys.exit("Пароли не совпадают.")
salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
ct = AESGCM(key(new, salt, enc["iter"])).encrypt(iv, plain, None)
enc.update(salt=base64.b64encode(salt).decode(), iv=base64.b64encode(iv).decode(), ct=base64.b64encode(ct).decode())
json.dump(enc, open(path, "w"))
print("Готово: перезаписан " + rel + ". Загрузи его в репозиторий (Add file → Upload files, в папку plans).")
