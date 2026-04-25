from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

from app.core.database import get_db
from app.models.models import ContentCalendarItem, GeneratedHook
from app.schemas import (
    CalendarItemCreate, CalendarItemResponse, CalendarItemUpdate,
    CalendarView
)

router = APIRouter(prefix="/calendar", tags=["calendar"])

# Helper function for current UTC time
def now_utc():
    return datetime.now(timezone.utc)


@router.post("/", response_model=CalendarItemResponse)
async def create_calendar_item(
    item: CalendarItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new calendar item."""
    
    # Validate hook_id if provided
    if item.hook_id:
        from sqlalchemy import select
        result = await db.execute(
            select(GeneratedHook).where(GeneratedHook.id == item.hook_id)
        )
        hook = result.scalar_one_or_none()
        if not hook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hook not found"
            )
    
    calendar_item = ContentCalendarItem(**item.model_dump())
    db.add(calendar_item)
    await db.commit()
    await db.refresh(calendar_item)
    
    return calendar_item


@router.get("/", response_model=List[CalendarItemResponse])
async def get_calendar_items(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get calendar items with optional filtering."""
    from sqlalchemy import select, and_
    
    # Default to next 30 days if no dates provided
    if not start_date:
        start_date = now_utc().replace(hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    query = select(ContentCalendarItem).where(
        and_(
            ContentCalendarItem.scheduled_date >= start_date,
            ContentCalendarItem.scheduled_date <= end_date
        )
    )
    
    if platform:
        query = query.where(ContentCalendarItem.platform == platform)
    
    if status:
        query = query.where(ContentCalendarItem.status == status)
    
    query = query.order_by(ContentCalendarItem.scheduled_date)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    return items


@router.get("/view/monthly", response_model=List[CalendarView])
async def get_monthly_calendar_view(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get calendar view grouped by date for a specific month."""
    from sqlalchemy import extract
    from collections import defaultdict
    
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # Calculate date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    query = (
        select(ContentCalendarItem)
        .where(
            and_(
                ContentCalendarItem.scheduled_date >= start_date,
                ContentCalendarItem.scheduled_date <= end_date
            )
        )
        .order_by(ContentCalendarItem.scheduled_date)
    )
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Group by date
    items_by_date = defaultdict(list)
    for item in items:
        date_key = item.scheduled_date.replace(hour=0, minute=0, second=0, microsecond=0)
        items_by_date[date_key].append(item)
    
    # Create CalendarView objects
    calendar_views = []
    current_date = start_date
    while current_date <= end_date:
        date_items = items_by_date.get(current_date, [])
        calendar_views.append(CalendarView(
            date=current_date,
            items=date_items
        ))
        current_date += timedelta(days=1)
    
    return calendar_views


@router.get("/{item_id}", response_model=CalendarItemResponse)
async def get_calendar_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific calendar item by ID."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ContentCalendarItem).where(ContentCalendarItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )
    
    return item


@router.patch("/{item_id}", response_model=CalendarItemResponse)
async def update_calendar_item(
    item_id: int,
    update_data: CalendarItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a calendar item."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ContentCalendarItem).where(ContentCalendarItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(item)
    
    return item


@router.post("/{item_id}/publish", response_model=CalendarItemResponse)
async def publish_calendar_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a calendar item as published."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ContentCalendarItem).where(ContentCalendarItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )
    
    item.status = "published"
    item.published_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(item)
    
    return item


@router.post("/{item_id}/duplicate", response_model=CalendarItemResponse)
async def duplicate_calendar_item(
    item_id: int,
    scheduled_date: datetime,
    db: AsyncSession = Depends(get_db)
):
    """Duplicate a calendar item for a new date."""
    from sqlalchemy.orm import select
    
    result = await db.execute(
        select(ContentCalendarItem).where(ContentCalendarItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )
    
    # Create new item with same data but new date
    new_item = ContentCalendarItem(
        title=item.title,
        description=item.description,
        platform=item.platform,
        content_type=item.content_type,
        scheduled_date=scheduled_date,
        status="draft",
        hook_id=item.hook_id,
        caption=item.caption,
        hashtags=item.hashtags,
        media_urls=item.media_urls
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    return new_item


@router.delete("/{item_id}")
async def delete_calendar_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a calendar item."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(ContentCalendarItem).where(ContentCalendarItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar item not found"
        )
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "Calendar item deleted successfully"}


@router.get("/stats/overview")
async def get_calendar_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get calendar statistics."""
    from sqlalchemy import func, and_
    from collections import defaultdict
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now() + timedelta(days=30)
    
    # Get all items in range
    query = (
        select(ContentCalendarItem)
        .where(
            and_(
                ContentCalendarItem.scheduled_date >= start_date,
                ContentCalendarItem.scheduled_date <= end_date
            )
        )
    )
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Calculate stats
    status_counts = defaultdict(int)
    platform_counts = defaultdict(int)
    content_type_counts = defaultdict(int)
    
    for item in items:
        status_counts[item.status] += 1
        platform_counts[item.platform] += 1
        content_type_counts[item.content_type] += 1
    
    return {
        "total_items": len(items),
        "by_status": dict(status_counts),
        "by_platform": dict(platform_counts),
        "by_content_type": dict(content_type_counts),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.post("/batch/create")
async def create_batch_calendar_items(
    items: List[CalendarItemCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create multiple calendar items in batch."""
    created_items = []
    
    for item_data in items:
        calendar_item = ContentCalendarItem(**item_data.model_dump())
        db.add(calendar_item)
        created_items.append(calendar_item)
    
    await db.commit()
    
    for item in created_items:
        await db.refresh(item)
    
    return {
        "message": f"Created {len(created_items)} calendar items",
        "items": created_items
    }
