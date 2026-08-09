from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.chat import ChatResponse
from backend.app.services.feedback import save_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=ChatResponse)
def submit_feedback(message_id: int, feedback: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    save_feedback(db=db, message_id=message_id, user=current_user, feedback_value=feedback)
    return {"answer": "Feedback saved", "sources": [], "confidence": 0, "follow_up_questions": []}
