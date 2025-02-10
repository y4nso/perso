# utils.py
import json
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# --- Configuration ---
SECRET_KEY = "votre_cle_secrete_très_long_et_unique"  # Changez cette clé en production !
ALGORITHM = "HS256"
USERS_FILE = "users.json"

# Contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Gestion du fichier JSON ---
# S'assurer que le fichier users.json existe
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

def get_users():
    with open(USERS_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []
    return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user(email: str):
    users = get_users()
    for user in users:
        if user["email"] == email:
            return user
    return None

def create_user(user_data: dict):
    users = get_users()
    users.append(user_data)
    save_users(users)

# --- Gestion des mots de passe ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Gestion des tokens JWT ---
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.PyJWTError:
        return None
    
def update_user(email: str, updated_data: dict):
    users = get_users()
    for i, user in enumerate(users):
        if user["email"] == email:
            users[i].update(updated_data)
            save_users(users)
            return

