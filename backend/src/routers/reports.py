from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from src.database import get_db
from src.models import Task, User, Report, TaskStatus, TaskPriority
from src.schemas import ReportCreate, ReportResponse
from src.auth import get_current_user, get_current_active_manager

router = APIRouter(prefix="/api/reports", tags=["reports"])


def generate_narrative_report(
    tasks: List[Task],
    period_start: datetime,
    period_end: datetime,
    department_name: str = None
) -> str:
    """Generate narrative-style report text"""
    total_tasks = len(tasks)
    
    # Count by priority
    critical_count = len([t for t in tasks if t.priority == TaskPriority.CRITICAL])
    important_count = len([t for t in tasks if t.priority == TaskPriority.IMPORTANT])
    low_count = len([t for t in tasks if t.priority == TaskPriority.LOW])
    
    # Calculate average completion time
    completion_times = []
    for task in tasks:
        if task.completed_at and task.created_at:
            delta = (task.completed_at - task.created_at).days
            completion_times.append(delta)
    
    avg_completion = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Count by assignee
    assignee_counts = {}
    for task in tasks:
        if task.assignee:
            name = task.assignee.full_name
            assignee_counts[name] = assignee_counts.get(name, 0) + 1
    
    # Sort by count
    top_performers = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate narrative
    report_text = f"""ОТЧЁТ О ВЫПОЛНЕННЫХ ЗАДАЧАХ

Период: {period_start.strftime('%d.%m.%Y')} - {period_end.strftime('%d.%m.%Y')}
"""
    
    if department_name:
        report_text += f"Отдел: {department_name}\n"
    
    report_text += f"""
За отчётный период было выполнено {total_tasks} задач(и).

Распределение по приоритетам:
- Критичных задач выполнено: {critical_count} ({critical_count/total_tasks*100:.1f}%)
- Важных задач: {important_count} ({important_count/total_tasks*100:.1f}%)
- Можно позже: {low_count} ({low_count/total_tasks*100:.1f}%)

Среднее время выполнения задачи: {avg_completion:.1f} дн.
"""
    
    if top_performers:
        report_text += "\nНаиболее активные сотрудники:\n"
        for i, (name, count) in enumerate(top_performers, 1):
            report_text += f"{i}. {name} - {count} задач(и)\n"
    
    return report_text


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_manager),
    db: Session = Depends(get_db)
):
    """Generate a new report"""
    # Query completed tasks in period
    query = db.query(Task).filter(
        and_(
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= report_data.period_start,
            Task.completed_at <= report_data.period_end
        )
    )
    
    # Filter by department if specified
    if report_data.department_id:
        query = query.filter(Task.department_id == report_data.department_id)
    
    tasks = query.all()
    
    # Get department name
    department_name = None
    if report_data.department_id:
        from src.models import Department
        dept = db.query(Department).filter(Department.id == report_data.department_id).first()
        department_name = dept.name if dept else None
    
    # Generate narrative text
    narrative_text = generate_narrative_report(
        tasks=tasks,
        period_start=report_data.period_start,
        period_end=report_data.period_end,
        department_name=department_name
    )
    
    # Prepare JSON content
    content = {
        "total_tasks": len(tasks),
        "period_start": report_data.period_start.isoformat(),
        "period_end": report_data.period_end.isoformat(),
        "department_id": str(report_data.department_id) if report_data.department_id else None,
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "priority": task.priority.value,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "assignee": task.assignee.full_name if task.assignee else None
            }
            for task in tasks
        ]
    }
    
    # Create report
    new_report = Report(
        title=report_data.title,
        period_start=report_data.period_start,
        period_end=report_data.period_end,
        generated_by=current_user.id,
        department_id=report_data.department_id,
        content=content,
        narrative_text=narrative_text
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.get("", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download report as text file"""
    from fastapi.responses import PlainTextResponse
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.txt"
    
    return PlainTextResponse(
        content=report.narrative_text,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )







