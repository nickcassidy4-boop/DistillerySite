from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import recipes, runs, readings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homebrew Tracker", version="0.1.0")

jinja_env = Environment(loader=FileSystemLoader("templates"))
templates = Jinja2Templates(env=jinja_env)

app.include_router(recipes.router)
app.include_router(runs.router)
app.include_router(readings.router)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    recipe_count = db.query(models.Recipe).count()
    run_count = db.query(models.SpiritRun).count()
    active_count = db.query(models.SpiritRun).filter(
        models.SpiritRun.status == models.SessionStatus.fermenting
    ).count()
    recent_runs = (
        db.query(models.SpiritRun)
        .order_by(models.SpiritRun.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "recipe_count": recipe_count,
        "run_count": run_count,
        "active_count": active_count,
        "recent_runs": recent_runs,
    })