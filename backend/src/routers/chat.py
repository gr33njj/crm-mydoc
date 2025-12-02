from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.database import get_db
from src.models import ChatRoom, ChatMember, ChatMessage, User
from src.schemas import (
    ChatRoomCreate, ChatRoomResponse,
    ChatMessageCreate, ChatMessageResponse
)
from src.auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    # Create room
    new_room = ChatRoom(
        name=room_data.name,
        type=room_data.type,
        department_id=room_data.department_id,
        created_by=current_user.id
    )
    
    db.add(new_room)
    db.flush()
    
    # Add creator as member
    creator_member = ChatMember(
        room_id=new_room.id,
        user_id=current_user.id
    )
    db.add(creator_member)
    
    # Add other members
    for member_id in room_data.member_ids:
        if member_id != current_user.id:
            member = ChatMember(
                room_id=new_room.id,
                user_id=member_id
            )
            db.add(member)
    
    db.commit()
    db.refresh(new_room)
    
    return new_room


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_user_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat rooms for current user"""
    memberships = db.query(ChatMember).filter(ChatMember.user_id == current_user.id).all()
    room_ids = [m.room_id for m in memberships]
    
    rooms = db.query(ChatRoom).filter(ChatRoom.id.in_(room_ids)).order_by(ChatRoom.created_at.desc()).all()
    return rooms


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_room_messages(
    room_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a chat room"""
    # Check if user is member
    membership = db.query(ChatMember).filter(
        ChatMember.room_id == room_id,
        ChatMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this room")
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id
    ).order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    
    # Update last read
    from datetime import datetime
    membership.last_read_at = datetime.utcnow()
    db.commit()
    
    return list(reversed(messages))


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    room_id: UUID,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to chat room"""
    # Check if user is member
    membership = db.query(ChatMember).filter(
        ChatMember.room_id == room_id,
        ChatMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this room")
    
    # Create message
    new_message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=message_data.content,
        reply_to_id=message_data.reply_to_id
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # TODO: Send via WebSocket to all room members
    
    return new_message


@router.post("/rooms/{room_id}/members", status_code=status.HTTP_201_CREATED)
async def add_room_member(
    room_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add member to chat room"""
    # Check if current user is member
    membership = db.query(ChatMember).filter(
        ChatMember.room_id == room_id,
        ChatMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this room")
    
    # Check if user already member
    existing = db.query(ChatMember).filter(
        ChatMember.room_id == room_id,
        ChatMember.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already in room")
    
    # Add member
    new_member = ChatMember(
        room_id=room_id,
        user_id=user_id
    )
    
    db.add(new_member)
    db.commit()
    
    return {"message": "Member added successfully"}


@router.delete("/rooms/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_room_member(
    room_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from chat room"""
    # Get room
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Only creator or admin can remove members
    if room.created_by != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Remove member
    membership = db.query(ChatMember).filter(
        ChatMember.room_id == room_id,
        ChatMember.user_id == user_id
    ).first()
    
    if membership:
        db.delete(membership)
        db.commit()
    
    return None







