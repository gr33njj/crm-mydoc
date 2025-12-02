from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from src.models import UserRole, TaskPriority, TaskStatus, ChatRoomType, NotificationType


# Auth Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    department_id: Optional[UUID] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    department_id: Optional[UUID] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[int] = None
    department_id: Optional[UUID] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    avatar_url: Optional[str] = None
    telegram_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    head_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    head_id: Optional[UUID] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    head_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.LOW
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    assignee_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    assignee_id: Optional[UUID] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    creator_id: UUID
    assignee_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    status: TaskStatus
    parent_task_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Task Comment Schemas
class TaskCommentCreate(BaseModel):
    content: str


class TaskCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


# Checklist Schemas
class ChecklistCreate(BaseModel):
    title: str = Field(..., max_length=500)
    order: int = 0


class ChecklistUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None


class ChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    title: str
    order: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime


# Chat Room Schemas
class ChatRoomCreate(BaseModel):
    name: Optional[str] = None
    type: ChatRoomType
    department_id: Optional[UUID] = None
    member_ids: List[UUID] = []


class ChatRoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: Optional[str] = None
    type: ChatRoomType
    department_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime


# Chat Message Schemas
class ChatMessageCreate(BaseModel):
    content: str
    reply_to_id: Optional[UUID] = None


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    room_id: UUID
    sender_id: UUID
    content: str
    reply_to_id: Optional[UUID] = None
    is_edited: bool
    created_at: datetime
    updated_at: datetime


# Report Schemas
class ReportCreate(BaseModel):
    title: str = Field(..., max_length=500)
    period_start: datetime
    period_end: datetime
    department_id: Optional[UUID] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    period_start: datetime
    period_end: datetime
    generated_by: UUID
    department_id: Optional[UUID] = None
    narrative_text: str
    created_at: datetime


# Notification Schemas
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    content: Optional[str] = None
    is_read: bool
    related_task_id: Optional[UUID] = None
    related_chat_id: Optional[UUID] = None
    created_at: datetime


# File Upload Response
class FileUploadResponse(BaseModel):
    id: UUID
    filename: str
    filesize: int
    mime_type: Optional[str] = None
    created_at: datetime







