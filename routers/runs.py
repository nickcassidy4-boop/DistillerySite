from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from typing import Optional

from database import get_db
import models

router = APIRouter(prefix="/runs", tags=["runs"])

jinja_env = Environment(loader=FileSystemLoader("templates"))
templates = Jinja2Templates(env=jinja_env)


@router.get("/", response_class=HTMLResponse)
def list_runs(request: Request, db: Session = Depends(get_db)):
    runs = (
        db.query(models.SpiritRun)
        .order_by(models.SpiritRun.created_at.desc())
        .all()
    )
    return templates.TemplateResponse("runs/list.html", {
        "request": request,
        "runs": runs,
    })


@router.get("/new", response_class=HTMLResponse)
def new_run_form(request: Request, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).order_by(models.Recipe.name).all()
    return templates.TemplateResponse("runs/form.html", {
        "request": request,
        "run": None,
        "recipes": recipes,
        "action": "/runs/new",
        "title": "New Spirit Run",
    })


@router.post("/new")
def create_run(
    request: Request,
    recipe_id: int = Form(...),
    batch_number: int = Form(...),
    status: str = Form(models.SessionStatus.planning),
    fermentation_start_date: Optional[str] = Form(None),
    actual_og: Optional[float] = Form(None),
    actual_fg: Optional[float] = Form(None),
    actual_abv: Optional[float] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    run = models.SpiritRun(
        recipe_id=recipe_id,
        batch_number=batch_number,
        status=status,
        fermentation_start_date=fermentation_start_date or None,
        actual_og=actual_og,
        actual_fg=actual_fg,
        actual_abv=actual_abv,
        notes=notes or None,
    )
    db.add(run)
    db.commit()
    return RedirectResponse(url="/runs", status_code=303)


@router.get("/{run_id}/edit", response_class=HTMLResponse)
def edit_run_form(run_id: int, request: Request, db: Session = Depends(get_db)):
    run = db.query(models.SpiritRun).filter(models.SpiritRun.id == run_id).first()
    if not run:
        return RedirectResponse(url="/runs", status_code=303)
    recipes = db.query(models.Recipe).order_by(models.Recipe.name).all()
    return templates.TemplateResponse("runs/form.html", {
        "request": request,
        "run": run,
        "recipes": recipes,
        "action": f"/runs/{run_id}/edit",
        "title": "Edit Spirit Run",
    })


@router.post("/{run_id}/edit")
def update_run(
    run_id: int,
    request: Request,
    recipe_id: int = Form(...),
    batch_number: int = Form(...),
    status: str = Form(models.SessionStatus.planning),
    fermentation_start_date: Optional[str] = Form(None),
    actual_og: Optional[float] = Form(None),
    actual_fg: Optional[float] = Form(None),
    actual_abv: Optional[float] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    run = db.query(models.SpiritRun).filter(models.SpiritRun.id == run_id).first()
    if not run:
        return RedirectResponse(url="/runs", status_code=303)

    run.recipe_id = recipe_id
    run.batch_number = batch_number
    run.status = status
    run.fermentation_start_date = fermentation_start_date or None
    run.actual_og = actual_og
    run.actual_fg = actual_fg
    run.actual_abv = actual_abv
    run.notes = notes or None

    db.commit()
    return RedirectResponse(url="/runs", status_code=303)


@router.post("/{run_id}/delete")
def delete_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.SpiritRun).filter(models.SpiritRun.id == run_id).first()
    if run:
        db.delete(run)
        db.commit()
    return RedirectResponse(url="/runs", status_code=303)