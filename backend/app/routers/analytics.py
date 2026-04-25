from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import pandas as pd
import os
import re
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.models import UploadedData, AnalyticsRecord
from app.schemas import (
    UploadedDataResponse, UploadedDataWithRecords, AnalyticsSummary,
    CSVUploadResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    platform: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process analytics CSV file."""
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    filename_lower = file.filename.lower()
    if not filename_lower.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Check file size before reading
    # Read chunk by chunk to avoid memory issues
    content = b""
    chunk_size = 1024 * 1024  # 1MB chunks
    file_size = 0
    
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
            )
        content += chunk
    
    # Sanitize filename - remove path traversal characters
    safe_base = re.sub(r'[^\w\-. ]', '_', file.filename)
    safe_base = safe_base.strip('._ ')  # Remove leading/trailing dots, underscores, spaces
    if not safe_base:
        safe_base = "upload"
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file with sanitized name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{safe_base}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Process CSV with pandas
    try:
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        # Store upload metadata
        uploaded_data = UploadedData(
            filename=file.filename,
            file_path=file_path,
            platform=platform,
            row_count=row_count,
            processed_data={
                "columns": df.columns.tolist(),
                "sample_values": df.head(3).to_dict('records')
            }
        )
        db.add(uploaded_data)
        await db.flush()
        
        # Parse and store analytics records
        # Standardize column names (basic mapping)
        column_mapping = {
            'views': 'views',
            'Views': 'views',
            'likes': 'likes',
            'Likes': 'likes',
            'comments': 'comments',
            'Comments': 'comments',
            'shares': 'shares',
            'Shares': 'shares',
            'impressions': 'impressions',
            'Impressions': 'impressions',
            'reach': 'reach',
            'Reach': 'reach',
            'engagement_rate': 'engagement_rate',
            'Engagement Rate': 'engagement_rate',
            'title': 'title',
            'Title': 'title',
            'date': 'date',
            'Date': 'date',
        }
        
        records_to_insert = []
        for _, row in df.iterrows():
            record_data = {
                'uploaded_data_id': uploaded_data.id,
                'date': pd.to_datetime(row.get('date', row.get('Date', datetime.now()))),
                'content_type': row.get('content_type', row.get('Content Type', 'unknown')),
                'title': str(row.get('title', row.get('Title', ''))),
                'views': int(row.get('views', row.get('Views', 0)) or 0),
                'likes': int(row.get('likes', row.get('Likes', 0)) or 0),
                'comments': int(row.get('comments', row.get('Comments', 0)) or 0),
                'shares': int(row.get('shares', row.get('Shares', 0)) or 0),
                'impressions': int(row.get('impressions', row.get('Impressions', 0)) or 0),
                'reach': int(row.get('reach', row.get('Reach', 0)) or 0),
                'engagement_rate': float(row.get('engagement_rate', row.get('Engagement Rate', 0)) or 0),
                'platform_data': row.to_dict()
            }
            
            record = AnalyticsRecord(**record_data)
            records_to_insert.append(record)
        
        for record in records_to_insert:
            db.add(record)
        
        await db.commit()
        
        return CSVUploadResponse(
            success=True,
            records_processed=row_count,
            uploaded_data_id=uploaded_data.id,
            message=f"Successfully processed {row_count} records"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.get("/uploads", response_model=List[UploadedDataResponse])
async def get_uploads(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of uploaded analytics data."""
    from sqlalchemy import select
    
    query = select(UploadedData)
    if platform:
        query = query.where(UploadedData.platform == platform)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    uploads = result.scalars().all()
    return uploads


@router.get("/uploads/{uploaded_data_id}", response_model=UploadedDataWithRecords)
async def get_uploaded_data_with_records(
    uploaded_data_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get uploaded data with all its analytics records."""
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    result = await db.execute(
        select(UploadedData)
        .options(joinedload(UploadedData.analytics_records))
        .where(UploadedData.id == uploaded_data_id)
    )
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    return upload


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated analytics summary."""
    from sqlalchemy import select, func
    
    query = select(AnalyticsRecord)
    
    if platform:
        # Join with UploadedData to filter by platform
        query = query.join(UploadedData).where(UploadedData.platform == platform)
    
    if start_date:
        query = query.where(AnalyticsRecord.date >= start_date)
    
    if end_date:
        query = query.where(AnalyticsRecord.date <= end_date)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    if not records:
        return AnalyticsSummary(
            total_views=0,
            total_likes=0,
            total_comments=0,
            total_shares=0,
            avg_engagement_rate=0.0,
            top_performing_content=[],
            growth_by_date=[]
        )
    
    # Calculate aggregates
    total_views = sum(r.views for r in records)
    total_likes = sum(r.likes for r in records)
    total_comments = sum(r.comments for r in records)
    total_shares = sum(r.shares for r in records)
    avg_engagement = sum(r.engagement_rate for r in records) / len(records) * 100
    
    # Top performing content (by engagement rate)
    top_content = sorted(records, key=lambda x: x.engagement_rate, reverse=True)[:5]
    
    # Growth by date
    from collections import defaultdict
    growth_data = defaultdict(lambda: {"views": 0, "likes": 0, "comments": 0, "shares": 0})
    
    for r in records:
        date_key = r.date.strftime("%Y-%m-%d")
        growth_data[date_key]["views"] += r.views
        growth_data[date_key]["likes"] += r.likes
        growth_data[date_key]["comments"] += r.comments
        growth_data[date_key]["shares"] += r.shares
    
    growth_by_date = [
        {"date": date, **metrics}
        for date, metrics in sorted(growth_data.items())
    ]
    
    return AnalyticsSummary(
        total_views=total_views,
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares,
        avg_engagement_rate=avg_engagement,
        top_performing_content=top_content,
        growth_by_date=growth_by_date
    )


@router.delete("/uploads/{uploaded_data_id}")
async def delete_upload(
    uploaded_data_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete uploaded data and its records."""
    from sqlalchemy import select, delete
    
    result = await db.execute(
        select(UploadedData).where(UploadedData.id == uploaded_data_id)
    )
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    await db.delete(upload)
    await db.commit()
    
    return {"message": "Upload deleted successfully"}
