from pathlib import Path
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile

from src.app.domain.report.crud import report_crud

ROOT_DIR = Path(__file__).resolve().parents[4]
REPORT_DIR = ROOT_DIR / "resource" / "static" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


async def save_report(
    db: Session,
    game_id: int | None,
    reason: str,
    description: str,
    video: UploadFile
) -> None:
    file_name = f"{uuid.uuid4()}.webm"
    file_path = REPORT_DIR / file_name
    with open(file_path, "wb") as f:
        f.write(await video.read())
    report_crud.create_report(db, game_id, reason, description, str(file_path))
