from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from src.models import Notification, NotificationType


async def create_notification(
    db: Session,
    user_id: UUID,
    type: NotificationType,
    title: str,
    content: Optional[str] = None,
    related_task_id: Optional[UUID] = None,
    related_chat_id: Optional[UUID] = None
) -> Notification:
    """Create a new notification"""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        related_task_id=related_task_id,
        related_chat_id=related_chat_id
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification







