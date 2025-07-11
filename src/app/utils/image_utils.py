import os
from uuid import uuid4
from pathlib import Path
from src.app.main import STATIC_DIR
from fastapi import UploadFile

from src.app.config.config import settings
from src.app.utils.s3_utils import upload_profile_image_to_s3

from src.app.main import STATIC_DIR

PROFILE_IMAGE_DIR = STATIC_DIR / "profile_images"


async def upload_profile_image(file: UploadFile) -> str:
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4()}{file_ext}"
    file_bytes = await file.read()

    if settings.ENV == "local":
        PROFILE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PROFILE_IMAGE_DIR / file_name
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return f"/static/profile_images/{file_name}"
    else:
        return await upload_profile_image_to_s3(file)
