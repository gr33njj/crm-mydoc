from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.database import get_db
from src.models import Task, User, TaskComment, TaskFile, Checklist, TaskStatus
from src.schemas import (
    TaskCreate, TaskUpdate, TaskResponse,
    TaskCommentCreate, TaskCommentResponse,
    ChecklistCreate, ChecklistUpdate, ChecklistResponse
)
from src.auth import get_current_user
from src.services.notifications import create_notification, NotificationType

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    department_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    creator_id: Optional[UUID] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of tasks with filters"""
    query = db.query(Task)
    
    # Apply filters
    if department_id:
        query = query.filter(Task.department_id == department_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if creator_id:
        query = query.filter(Task.creator_id == creator_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    # Non-admin users can only see their tasks or department tasks
    if current_user.role == "EMPLOYEE":
        query = query.filter(
            or_(
                Task.assignee_id == current_user.id,
                Task.creator_id == current_user.id,
                Task.department_id == current_user.department_id
            )
        )
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        creator_id=current_user.id,
        assignee_id=task_data.assignee_id,
        department_id=task_data.department_id,
        priority=task_data.priority,
        deadline=task_data.deadline,
        parent_task_id=task_data.parent_task_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Send notification to assignee
    if task_data.assignee_id and task_data.assignee_id != current_user.id:
        await create_notification(
            db=db,
            user_id=task_data.assignee_id,
            type=NotificationType.TASK_ASSIGNED,
            title="Новая задача назначена",
            content=f"Вам назначена задача: {task_data.title}",
            related_task_id=new_task.id
        )
    
    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check permissions
    if current_user.role == "EMPLOYEE":
        if (task.assignee_id != current_user.id and 
            task.creator_id != current_user.id and 
            task.department_id != current_user.department_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check permissions
    if current_user.role == "EMPLOYEE":
        if task.creator_id != current_user.id and task.assignee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark task as completed"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Only assignee can complete task
    if task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only assignee can complete the task"
        )
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    # Notify creator
    if task.creator_id != current_user.id:
        await create_notification(
            db=db,
            user_id=task.creator_id,
            type=NotificationType.TASK_ASSIGNED,
            title="Задача выполнена",
            content=f"Задача '{task.title}' выполнена",
            related_task_id=task.id
        )
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Only creator or admin can delete
    if current_user.role != "ADMIN" and task.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    db.delete(task)
    db.commit()
    
    return None


# Task Comments
@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: UUID,
    comment_data: TaskCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add comment to task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    new_comment = TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # Notify task assignee
    if task.assignee_id and task.assignee_id != current_user.id:
        await create_notification(
            db=db,
            user_id=task.assignee_id,
            type=NotificationType.TASK_COMMENT,
            title="Новый комментарий к задаче",
            content=f"Комментарий к задаче '{task.title}'",
            related_task_id=task.id
        )
    
    return new_comment


@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at).all()
    return comments


# Subtasks
@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
async def get_subtasks(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subtasks for a task"""
    subtasks = db.query(Task).filter(Task.parent_task_id == task_id).all()
    return subtasks


# Checklists
@router.post("/{task_id}/checklists", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(
    task_id: UUID,
    checklist_data: ChecklistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add checklist item to task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    new_item = Checklist(
        task_id=task_id,
        title=checklist_data.title,
        order=checklist_data.order
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item


@router.get("/{task_id}/checklists", response_model=List[ChecklistResponse])
async def get_checklists(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all checklist items for a task"""
    items = db.query(Checklist).filter(Checklist.task_id == task_id).order_by(Checklist.order).all()
    return items


@router.patch("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist_item(
    checklist_id: UUID,
    checklist_data: ChecklistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update checklist item"""
    item = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    
    update_data = checklist_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    if checklist_data.is_completed and not item.is_completed:
        item.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return item







