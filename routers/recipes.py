from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from typing import Optional

from database import get_db
import models

router = APIRouter(prefix="/recipes", tags=["recipes"])

jinja_env = Environment(loader=FileSystemLoader("templates"))
templates = Jinja2Templates(env=jinja_env)


@router.get("/", response_class=HTMLResponse)
def list_recipes(request: Request, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()
    return templates.TemplateResponse("recipes/list.html", {
        "request": request,
        "recipes": recipes,
    })


@router.get("/new", response_class=HTMLResponse)
def new_recipe_form(request: Request):
    return templates.TemplateResponse("recipes/form.html", {
        "request": request,
        "recipe": None,
        "action": "/recipes/new",
        "title": "New Recipe",
    })


@router.post("/new")
def create_recipe(
    request: Request,
    name: str = Form(...),
    spirit_type: str = Form(""),
    mash_bill: str = Form(""),
    target_wash_og: Optional[float] = Form(None),
    target_wash_abv: Optional[float] = Form(None),
    water_volume_litres: Optional[float] = Form(None),
    yeast_strain: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    recipe = models.Recipe(
        name=name,
        spirit_type=spirit_type or None,
        mash_bill=mash_bill or None,
        target_wash_og=target_wash_og,
        target_wash_abv=target_wash_abv,
        water_volume_litres=water_volume_litres,
        yeast_strain=yeast_strain or None,
        notes=notes or None,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return RedirectResponse(url="/recipes", status_code=303)


@router.get("/{recipe_id}/edit", response_class=HTMLResponse)
def edit_recipe_form(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        return RedirectResponse(url="/recipes", status_code=303)
    return templates.TemplateResponse("recipes/form.html", {
        "request": request,
        "recipe": recipe,
        "action": f"/recipes/{recipe_id}/edit",
        "title": "Edit Recipe",
    })


@router.post("/{recipe_id}/edit")
def update_recipe(
    recipe_id: int,
    request: Request,
    name: str = Form(...),
    spirit_type: str = Form(""),
    mash_bill: str = Form(""),
    target_wash_og: Optional[float] = Form(None),
    target_wash_abv: Optional[float] = Form(None),
    water_volume_litres: Optional[float] = Form(None),
    yeast_strain: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        return RedirectResponse(url="/recipes", status_code=303)

    recipe.name = name
    recipe.spirit_type = spirit_type or None
    recipe.mash_bill = mash_bill or None
    recipe.target_wash_og = target_wash_og
    recipe.target_wash_abv = target_wash_abv
    recipe.water_volume_litres = water_volume_litres
    recipe.yeast_strain = yeast_strain or None
    recipe.notes = notes or None

    db.commit()
    return RedirectResponse(url="/recipes", status_code=303)


@router.post("/{recipe_id}/delete")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if recipe:
        db.delete(recipe)
        db.commit()
    return RedirectResponse(url="/recipes", status_code=303)