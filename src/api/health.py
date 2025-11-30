from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "",
    status_code=200,
    summary="Проверка здоровья",
    responses={200: {"description": "Service is up"}},
)
async def health():
    return {"status": "ok"}
