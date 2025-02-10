# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import router as auth_router
from utils import decode_access_token, get_user, update_user

app = FastAPI()

# Monter le dossier static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inclure le routeur d'authentification
app.include_router(auth_router)

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user_email = None
    token = request.cookies.get("access_token")
    if token:
        payload = decode_access_token(token)
        if payload:
            user_email = payload.get("sub")
    return templates.TemplateResponse("index.html", {"request": request, "user_email": user_email})

@app.get("/caca", response_class=HTMLResponse)
async def caca(request: Request):
    return templates.TemplateResponse("caca.html", {"request": request})


# ------------------------
# PAGE GARANCE (accessible uniquement pour becot.garance@gmail.com)
# ------------------------
@app.get("/garance", response_class=HTMLResponse)
async def garance(request: Request):
    token = request.cookies.get("access_token")
    if not token:
         return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    if not payload or payload.get("sub") != "becot.garance@gmail.com":
         return RedirectResponse(url="/", status_code=302)
    email = payload.get("sub")
    user = get_user(email)
    return templates.TemplateResponse("garance.html", {"request": request, "user": user})

# ------------------------
# ENDPOINTS POUR LES ÉPREUVES
# Pour chaque épreuve, nous créons un endpoint GET et un endpoint POST
# ------------------------

@app.post("/reset_flags")
async def reset_flags(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    # On s'assure que seul le user secret peut réinitialiser sa progression
    if email != "becot.garance@gmail.com":
        return RedirectResponse(url="/profile", status_code=302)
    # Réinitialisation de tous les flags
    update_user(email, {
        "epreuve1": False,
        "epreuve2": False,
        "epreuve3": False,
        "epreuve4": False
    })
    return RedirectResponse(url="/profile", status_code=302)

# Épreuve 1
@app.get("/garance/epreuve1", response_class=HTMLResponse)
async def epreuve1_get(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    return templates.TemplateResponse("epreuve1.html", {"request": request, "user": user})

@app.post("/garance/epreuve1")
async def epreuve1_post(request: Request, code: str = Form(...)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    # Vérification du code saisi
    if code == "255":
        update_user(email, {"epreuve1": True})
        return RedirectResponse(url="/garance", status_code=302)
    else:
        # En cas d'erreur, on renvoie à la même page en affichant un message d'erreur
        return templates.TemplateResponse("epreuve1.html", {"request": request, "user": user, "error": "Code incorrect. Réessayez."})

# Épreuve 2
@app.get("/garance/epreuve2", response_class=HTMLResponse)
async def epreuve2_get(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    return templates.TemplateResponse("epreuve2.html", {"request": request, "user": user})

@app.post("/garance/epreuve2")
async def epreuve2_post(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    if not user.get("epreuve2", False):
        update_user(email, {"epreuve2": True})
    return RedirectResponse(url="/garance", status_code=302)

# Épreuve 3
@app.get("/garance/epreuve3", response_class=HTMLResponse)
async def epreuve3_get(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    return templates.TemplateResponse("epreuve3.html", {"request": request, "user": user})

@app.post("/garance/epreuve3")
async def epreuve3_post(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    if not user.get("epreuve3", False):
        update_user(email, {"epreuve3": True})
    return RedirectResponse(url="/garance", status_code=302)

# Épreuve 4
@app.get("/garance/epreuve4", response_class=HTMLResponse)
async def epreuve4_get(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    return templates.TemplateResponse("epreuve4.html", {"request": request, "user": user})

@app.post("/garance/epreuve4")
async def epreuve4_post(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    if not user.get("epreuve4", False):
        update_user(email, {"epreuve4": True})
    return RedirectResponse(url="/garance", status_code=302)

# ------------------------
# ENDPOINT POUR LA PAGE DE JEU
# ------------------------
@app.get("/game", response_class=HTMLResponse)
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})
