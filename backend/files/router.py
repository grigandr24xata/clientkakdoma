from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/")
def files_stub() -> dict[str, str]:
    return {"status": "stub", "module": "files"}


@router.get("/health")
def files_health() -> dict[str, str]:
    return {"status": "ok", "storage": "in-memory stub"}
