from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from typing import Optional

from database import get_db
import models

router = APIRouter(prefix="/runs", tags=["readings"])

jinja_env = Environment(loader=FileSystemLoader("templates"))
templates = Jinja2Templates(env=jinja_env)


@router.get("/{run_id}/readings", response_class=HTMLResponse)
def view_readings(run_id: int, request: Request, db: Session = Depends(get_db)):
    run = db.query(models.SpiritRun).filter(models.SpiritRun.id == run_id).first()
    if not run:
        return RedirectResponse(url="/runs", status_code=303)
    readings = (
        db.query(models.FermentationReading)
        .filter(models.FermentationReading.spirit_run_id == run_id)
        .order_by(models.FermentationReading.timestamp.asc())
        .all()
    )
    return templates.TemplateResponse("readings/detail.html", {
        "request": request,
        "run": run,
        "readings": readings,
    })


@router.post("/{run_id}/readings/add")
def add_reading(
    run_id: int,
    gravity: Optional[float] = Form(None),
    temperature_c: Optional[float] = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    run = db.query(models.SpiritRun).filter(models.SpiritRun.id == run_id).first()
    if not run:
        return RedirectResponse(url="/runs", status_code=303)

    reading = models.FermentationReading(
        spirit_run_id=run_id,
        gravity=gravity,
        temperature_c=temperature_c,
        source="manual",
    )
    db.add(reading)
    db.commit()
    return RedirectResponse(url=f"/runs/{run_id}/readings", status_code=303)


@router.post("/{run_id}/readings/{reading_id}/delete")
def delete_reading(run_id: int, reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(models.FermentationReading).filter(
        models.FermentationReading.id == reading_id
    ).first()
    if reading:
        db.delete(reading)
        db.commit()
    return RedirectResponse(url=f"/runs/{run_id}/readings", status_code=303)