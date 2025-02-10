# auth.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from models import User, UserIn, Token
from utils import get_user, create_user, verify_password, get_password_hash, create_access_token, decode_access_token
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ACCESS_TOKEN_EXPIRE_MINUTES = 600  # 1 heure

# Page de connexion (GET)
@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Connexion (POST)
@router.post("/login")
async def login_post(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Email ou mot de passe incorrect"})
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# Page d'inscription (GET)
@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Inscription (POST)
@router.post("/register")
async def register_post(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None)
):
    if get_user(email):
        return templates.TemplateResponse("register.html", {"request": request, "error": "L'email existe déjà."})
    hashed_password = get_password_hash(password)
    # Ajout des flags d'épreuves
    user_data = {
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "epreuve1": False,
        "epreuve2": False,
        "epreuve3": False,
        "epreuve4": False
    }
    create_user(user_data)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# Page de profil (accessible après connexion)
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    payload = decode_access_token(token)
    if payload is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    email = payload.get("sub")
    user = get_user(email)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

# Déconnexion
@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
