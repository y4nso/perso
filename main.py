# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import router as auth_router
from utils import decode_access_token, get_user, update_user, get_users, save_users

app = FastAPI()

# Monter le dossier static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inclure le routeur d'authentification
app.include_router(auth_router)

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# Panneau Administrateur
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, search: str = "", filter_admin: str = "", filter_zoo: str = ""):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    current_email = payload.get("sub")
    current_user = get_user(current_email)
    if not current_user.get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    # Récupérer tous les utilisateurs
    users = get_users()
    # Appliquer les filtres si renseignés
    if search:
        users = [u for u in users if search.lower() in ((u.get("full_name") or "").lower() + u["email"].lower())]
    if filter_admin:
        users = [u for u in users if u.get("is_admin", False)]
    if filter_zoo:
        users = [u for u in users if u.get("is_zoo", False)]
    return templates.TemplateResponse("admin.html", {"request": request, "users": users, "search": search, "filter_admin": filter_admin, "filter_zoo": filter_zoo, "user": current_user})

# Mise à jour d'un utilisateur
@app.post("/admin/update_user")
async def admin_update_user(request: Request, email: str = Form(...), full_name: str = Form(""), new_password: str = Form(""), is_admin: str = Form(None), is_zoo: str = Form(None)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    current_email = payload.get("sub")
    current_user = get_user(current_email)
    if not current_user.get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    new_is_admin = True if is_admin is not None else False
    new_is_zoo = True if is_zoo is not None else False
    updated_data = {"full_name": full_name, "is_admin": new_is_admin, "is_zoo": new_is_zoo}
    if new_password.strip() != "":
        from utils import get_password_hash
        updated_data["hashed_password"] = get_password_hash(new_password)
    update_user(email, updated_data)
    return RedirectResponse(url="/admin", status_code=302)

# Suppression d'un utilisateur (sauf admin principal)
@app.post("/admin/delete_user")
async def admin_delete_user(request: Request, email: str = Form(...)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    current_email = payload.get("sub")
    current_user = get_user(current_email)
    if not current_user.get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    if email == "admin@admin.com":
        return RedirectResponse(url="/admin", status_code=302)
    users = get_users()
    users = [u for u in users if u["email"] != email]
    save_users(users)
    return RedirectResponse(url="/admin", status_code=302)

# Reset des flags pour l'utilisateur secret
@app.post("/admin/reset_secret")
async def admin_reset_secret(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    current_email = payload.get("sub")
    current_user = get_user(current_email)
    if not current_user.get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    update_user("becot.garance@gmail.com", {"epreuve1": False, "epreuve2": False, "epreuve3": False, "epreuve4": False})
    return RedirectResponse(url="/admin", status_code=302)

# Page Zoo (accessible uniquement aux utilisateurs ayant le rôle zoo)
@app.get("/zoo", response_class=HTMLResponse)
async def zoo_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    if not user.get("is_zoo", False):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("zoo.html", {"request": request, "user": user})

@app.get("/caca", response_class=HTMLResponse)
async def caca(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    # Transmet l'objet user dans le contexte pour que le template le reconnaisse
    return templates.TemplateResponse("caca.html", {"request": request, "user": user})



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
        "epreuve4": False,
        "item1": False,
        "item2": False,
        "item3": False,
        "item4": False,
        "item5": False,
        "item6": False,
        "item7": False,
        "item8": False,
        "item9": False,
        "item10": False
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
async def epreuve2_post(request: Request, final_day: str = Form(...), final_month: str = Form(...), final_year: str = Form(...)):
    token = request.cookies.get("access_token")
    if not token:
         return RedirectResponse(url="/login", status_code=302)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    # Le code final attendu est "22/08/24"
    const_correct = "22/08/24"
    entered_date = f"{final_day}/{final_month}/{final_year}"
    if entered_date == const_correct:
         update_user(email, {"epreuve2": True})
         return RedirectResponse(url="/garance", status_code=302)
    else:
         # En cas d'erreur, on renvoie à la même page en affichant un message d'erreur
         return templates.TemplateResponse("epreuve2.html", {"request": request, "user": user, "error": "Date incorrecte. Réessayez."})


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
async def game_page(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("game.html", {"request": request, "user": user})


@app.get("/articles/projets", response_class=HTMLResponse)
async def projets_article(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("projets.html", {"request": request, "user": user})

@app.get("/articles/guerre", response_class=HTMLResponse)
async def guerre_article(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("guerre.html", {"request": request, "user": user})

@app.get("/articles/yanso", response_class=HTMLResponse)
async def yanso_article(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("yanso.html", {"request": request, "user": user})

@app.get("/articles/daize", response_class=HTMLResponse)
async def daize_article(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("daize.html", {"request": request, "user": user})

@app.get("/articles/zeyo", response_class=HTMLResponse)
async def zeyo_article(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return templates.TemplateResponse("zeyo.html", {"request": request, "user": user})


# --- Utilitaire pour récupérer l'utilisateur courant ---
def current_user(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user = get_user(payload.get("sub"))
    return user

# Endpoint de la page "suivant" (secret items page)
@app.get("/secret-items", response_class=HTMLResponse)
async def secret_items_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    # Calculer le compteur d'items trouvés (somme des flags item1 à item10)
    count = sum([1 for i in range(1, 11) if user.get(f'item{i}', False)])
    return templates.TemplateResponse("secret_items.html", {"request": request, "user": user, "count": count})

# Endpoint pour mettre à jour un item secret (appelé par la fonction JS)
@app.post("/update_item")
async def update_item(request: Request, item_number: int = Form(...)):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse({"error": "Not authenticated"}, status_code=403)
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user(email)
    # Si l'item n'est pas déjà cliqué, mettre à jour le flag correspondant
    if not user.get(f'item{item_number}', False):
        update_user(email, {f"item{item_number}": True})
        # Rafraîchissez l'objet user après mise à jour
        user = get_user(email)
    # Calculer le compteur d'items trouvés
    count = sum([1 for i in range(1, 11) if user.get(f'item{i}', False)])
    return JSONResponse({"new_count": count})