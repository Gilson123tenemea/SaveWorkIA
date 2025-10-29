from fastapi import APIRouter

router = APIRouter(
    prefix="/example",
    tags=["example"]
)

@router.get("/")
def get_example():
    return {"message": "Este es un endpoint de ejemplo"}
