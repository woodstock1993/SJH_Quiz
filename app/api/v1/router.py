from fastapi import APIRouter

from app.api.v1.endpoints import auth, choice, users, quiz, question


router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(choice.router, prefix="/choice", tags=["choices"])
router.include_router(users.router, prefix="/user", tags=["users"])
router.include_router(quiz.router, prefix="/quiz", tags=["quizzes"])
router.include_router(question.router, prefix="/question", tags=["questions"])