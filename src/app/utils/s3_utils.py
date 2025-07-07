# src/app/utils/s3_utils.py
import boto3
from pathlib import Path
import json
from typing import TypedDict, List, Union
from src.app.models.models import Problem
from src.app.config.config import settings

BUCKET = settings.PROBLEM_BUCKET
REGION = settings.AWS_REGION

class ProblemURLBundle(TypedDict):
    problem_url: str           # JSON 본문 presigned URL
    image_urls : List[str]     # 0-N개 presigned URL, 순서 유지


class ProblemLocalBundle(TypedDict):
    problem_data: dict        # 로컬 JSON 데이터
    image_urls: List[str]


if not BUCKET or not REGION:
    raise RuntimeError("환경변수 PROBLEM_BUCKET / AWS_REGION 설정이 필요합니다")

ENDTIMER = 300 #유통기한 타이머
s3 = boto3.client("s3", region_name=REGION)

# 로컬 문제 JSON 디렉터리 (repo_root/data)
DATA_DIR = Path(__file__).resolve().parents[3] / "data"



def sign_s3_url(key: str, ttl: int) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=ttl,
    )



async def issue_problem_urls(problem: Problem) -> Union[ProblemURLBundle, ProblemLocalBundle]:

    if problem is None:
        raise ValueError("Problem 객체가 없습니다")

    print(f"[DEBUG] issue_problem_urls: {problem.problem_id}, body_key: {problem.body_key}, image_keys: {problem.image_keys}")
    try:
        problem_url = sign_s3_url(problem.body_key, ttl=ENDTIMER)
        using_local = False
    except Exception as e:  # pragma: no cover - S3 문제 시 로컬 사용
        print(f"[WARN] cannot access s3 for {problem.body_key}: {e} - falling back to local file")
        using_local = True

    image_urls: list[str] = []

    if not problem.image_keys:
        print(f"[DEBUG] 문제 {problem.problem_id}에 이미지가 없습니다.")
    else:
        for key in problem.image_keys:
            try:
                url = sign_s3_url(key, ttl=ENDTIMER)
                image_urls.append(url)
            except Exception as e:
                print(f"[WARN] cannot sign image url {key}: {e}")
                local_path = str(DATA_DIR / key)
                if Path(local_path).exists():
                    image_urls.append(local_path)

    if using_local:
        json_path = DATA_DIR / problem.body_key
        try:
            with json_path.open(encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Local problem file not found: {json_path}") from e
        return {
            "problem_data": data,
            "image_urls": image_urls,
        }

    return {
        "problem_url": problem_url,
        "image_urls": image_urls,
    }