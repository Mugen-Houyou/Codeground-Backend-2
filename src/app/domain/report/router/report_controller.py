from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.domain.report.service import report_service as service

router = APIRouter()


@router.post("/", status_code=201)
async def create_report(
        game_id: int | None = Form(None),
        reason: str = Form(...),
        description: str = Form(...),
        video: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    await service.save_report(db, game_id, reason, description, video)
    return {"message": "Report received"}