from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import recipes, sessions

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homebrew Tracker", version="0.1.0")

templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(recipes.router)
app.include_router(sessions.router)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page."""
    recipe_count = db.query(models.Recipe).count()
    session_count = db.query(models.BrewSession).count()
    active_count = db.query(models.BrewSession).filter(
        models.BrewSession.status == models.SessionStatus.fermenting
    ).count()
    recent_sessions = (
        db.query(models.BrewSession)
        .order_by(models.BrewSession.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipe_count": recipe_count,
        "session_count": session_count,
        "active_count": active_count,
        "sessions": recent_sessions,
    })


@app.get("/recipes", response_class=HTMLResponse)
def recipes_page(request: Request, db: Session = Depends(get_db)):
    """Recipes list page. (Full UI coming Week 2)"""
    all_recipes = db.query(models.Recipe).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipe_count": len(all_recipes),
        "session_count": 0,
        "active_count": 0,
        "sessions": [],
    })


@app.get("/sessions", response_class=HTMLResponse)
def sessions_page(request: Request, db: Session = Depends(get_db)):
    """Brew sessions list page. (Full UI coming Week 3)"""
    all_sessions = db.query(models.BrewSession).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipe_count": 0,
        "session_count": len(all_sessions),
        "active_count": 0,
        "sessions": all_sessions,
    })
