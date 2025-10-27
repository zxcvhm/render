from fastapi import APIRouter

router = APIRouter(prefix='')

@router.get('/')
def likes():
    return "좋아요 기능 추가 완료."