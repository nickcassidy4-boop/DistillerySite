from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/")
def list_recipes(db: Session = Depends(get_db)):
    """Return all recipes."""
    recipes = db.query(models.Recipe).all()
    return recipes


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Return a single recipe by ID."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/")
def create_recipe(db: Session = Depends(get_db)):
    """Create a new recipe. (Form handling coming in Week 2)"""
    # Placeholder — full form handling built in Week 2
    return {"message": "Recipe creation coming in Week 2"}


@router.put("/{recipe_id}")
def update_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Update a recipe. (Week 2)"""
    return {"message": f"Update recipe {recipe_id} coming in Week 2"}


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()
    return {"message": f"Recipe {recipe_id} deleted"}
