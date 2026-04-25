from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import random

from app.core.database import get_db
from app.models.models import GeneratedHook
from app.schemas import (
    HookGenerateRequest, HookResponse, HookCreate, HookUpdate
)

router = APIRouter(prefix="/hooks", tags=["hooks"])


# Hook templates for generation
HOOK_TEMPLATES = {
    "professional": [
        "In today's deep dive, we're exploring {}...",
        "The most overlooked insight about {} that professionals need to know",
        "Here's what {} really means for your strategy",
        "The data behind {} will surprise you",
        "We analyzed {} and found something interesting"
    ],
    "casual": [
        "So I was thinking about {} today...",
        "Here's a thought on {} - what do you think?",
        "Okay, hear me out about {}...",
        "Honestly? {} is way more interesting than I expected",
        "Just a quick take on {}"
    ],
    "dramatic": [
        "The shocking truth about {} will change everything",
        "Everything you know about {} is wrong",
        "I can't believe nobody's talking about this {} secret",
        "This {} revelation will blow your mind",
        "The {} scandal they don't want you to know about"
    ],
    "funny": [
        "Me explaining {} to my cat like it's not gonna give me the silent treatment",
        "{} is like a bad date - confusing, overwhelming, and somehow still worth it",
        "Plot twist: {} is actually just chaos with better branding",
        "I'm not saying {} is a conspiracy, but have you seen the evidence?",
        "POV: You just discovered {} and can't shut up about it"
    ],
    "inspirational": [
        "The power of {} changed my life - here's how",
        "What {} taught me about resilience and growth",
        "Find your strength in {}",
        "The journey through {} leads to transformation",
        "Believe in the magic of {}"
    ]
}

PLATFORM_HOOKS = {
    "youtube": [
        "This {} video will change how you see the world",
        "I spent 100 hours researching {} - here's what I learned",
        "The complete guide to {} nobody asked for but everyone needs",
        "From {} beginner to expert in 10 minutes"
    ],
    "tiktok": [
        "POV: You finally understand {}",
        "Tell me you love {} without telling me you love {}",
        "{} check! What level are you on?",
        "No one: ... Me at 3am researching {}",
        "The {} glow up we all needed"
    ],
    "instagram": [
        "Swipe to see the {} transformation",
        "The aesthetic guide to {} you didn't know you needed",
        "Living my best {} life ✨",
        "Monday motivation: embracing {}",
        "Your {} inspo for the day"
    ],
    "twitter": [
        "Hot take: {} is underrated",
        "Unpopular opinion but {} is actually good",
        "Thread 🧵 on why {} matters",
        "Normalize talking about {}",
        "The discourse around {} needs to change"
    ]
}


@router.post("/generate", response_model=List[HookResponse])
async def generate_hooks(
    request: HookGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate content hooks based on topic and tone."""
    
    generated_hooks = []
    templates = HOOK_TEMPLATES.get(request.tone, HOOK_TEMPLATES["professional"])
    platform_templates = PLATFORM_HOOKS.get(request.platform, [])
    
    # Combine templates
    all_templates = templates + platform_templates
    
    # Generate unique hooks
    selected_templates = random.sample(
        all_templates, 
        min(request.count, len(all_templates))
    )
    
    for template in selected_templates:
        hook_text = template.format(request.topic)
        
        # Add keywords if provided
        if request.keywords:
            hook_text = f"{hook_text} #{ ' #'.join(request.keywords[:3])}"
        
        hook = GeneratedHook(
            topic=request.topic,
            tone=request.tone,
            platform=request.platform,
            hook_text=hook_text,
            tags=request.keywords
        )
        db.add(hook)
        generated_hooks.append(hook)
    
    await db.commit()
    
    # Refresh all hooks to get IDs
    for hook in generated_hooks:
        await db.refresh(hook)
    
    return generated_hooks


@router.get("/", response_model=List[HookResponse])
async def get_hooks(
    platform: Optional[str] = None,
    tone: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get generated hooks with optional filtering."""
    from sqlalchemy import select
    from sqlalchemy import desc
    
    query = select(GeneratedHook)
    
    if platform:
        query = query.where(GeneratedHook.platform == platform)
    
    if tone:
        query = query.where(GeneratedHook.tone == tone)
    
    if is_favorite is not None:
        query = query.where(GeneratedHook.is_favorite == (1 if is_favorite else 0))
    
    query = query.order_by(desc(GeneratedHook.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    hooks = result.scalars().all()
    return hooks


@router.get("/favorites", response_model=List[HookResponse])
async def get_favorite_hooks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get favorite hooks."""
    from sqlalchemy import select, desc
    
    query = (
        select(GeneratedHook)
        .where(GeneratedHook.is_favorite == 1)
        .order_by(desc(GeneratedHook.created_at))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    hooks = result.scalars().all()
    return hooks


@router.get("/{hook_id}", response_model=HookResponse)
async def get_hook(
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific hook by ID."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedHook).where(GeneratedHook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    return hook


@router.patch("/{hook_id}", response_model=HookResponse)
async def update_hook(
    hook_id: int,
    update_data: HookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a hook."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedHook).where(GeneratedHook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    # Update fields
    if update_data.hook_text is not None:
        hook.hook_text = update_data.hook_text
    
    if update_data.is_favorite is not None:
        hook.is_favorite = 1 if update_data.is_favorite else 0
    
    if update_data.tags is not None:
        hook.tags = update_data.tags
    
    await db.commit()
    await db.refresh(hook)
    
    return hook


@router.post("/{hook_id}/use", response_model=HookResponse)
async def increment_hook_usage(
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Increment the usage count of a hook."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedHook).where(GeneratedHook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    hook.used += 1
    await db.commit()
    await db.refresh(hook)
    
    return hook


@router.delete("/{hook_id}")
async def delete_hook(
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a hook."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedHook).where(GeneratedHook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    await db.delete(hook)
    await db.commit()
    
    return {"message": "Hook deleted successfully"}


@router.post("/templates/refresh")
async def refresh_hook_templates():
    """Refresh hook templates with new creative ideas."""
    # This could be extended to include AI-powered hook generation
    # For now, it returns the current template counts
    return {
        "message": "Hook templates refreshed",
        "templates_count": {
            tone: len(templates) for tone, templates in HOOK_TEMPLATES.items()
        },
        "platform_templates_count": {
            platform: len(templates) for platform, templates in PLATFORM_HOOKS.items()
        }
    }
