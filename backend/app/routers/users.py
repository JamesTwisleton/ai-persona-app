from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])

class UserUpdate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)

@router.get("/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user.to_dict(show_private=True)

@router.patch("/me")
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.display_name = update_data.display_name

    # Handle preview mode state persistence
    if settings.ENV == "preview":
        import app.main
        app.main.PREVIEW_USER_DISPLAY_NAME = update_data.display_name

    try:
        state = inspect(current_user)
        if state and state.session:
            db.commit()
            db.refresh(current_user)
    except:
        # If not a real DB object, just proceed
        pass

    return current_user.to_dict(show_private=True)
