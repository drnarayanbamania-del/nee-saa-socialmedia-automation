from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from database import get_db
from models import Script, User, Topic
from schemas import ScriptCreate, ScriptResponse, ScriptRequest
from services.ai_service import AIService
from middleware.auth import get_current_user
from utils.credits import deduct_credits

router = APIRouter()

@router.post("/generate", response_model=Dict[str, Any])
async def generate_script(
    request: ScriptRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a script from a trending topic"""
    
    # Check user credits
    if current_user.credits < 10:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    ai_service = AIService()
    result = await ai_service.generate_script(request)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    script_data = result["script"]
    
    # Create topic if doesn't exist
    topic = db.query(Topic).filter(Topic.title == request.topic).first()
    if not topic:
        topic = Topic(
            user_id=current_user.id,
            title=request.topic,
            source="user_input",
            trend_score=70.0
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
    
    # Save script to database
    script = Script(
        user_id=current_user.id,
        topic_id=topic.id,
        title=script_data["title"],
        content=script_data["scenes"][0]["narration"] if script_data["scenes"] else "",
        hook=script_data.get("hook"),
        scenes=script_data["scenes"],
        duration_estimate=script_data.get("duration_estimate"),
        tone=request.tone,
        status="completed",
        metadata={
            "keywords": script_data.get("keywords", []),
            "hashtags": script_data.get("hashtags", [])
        }
    )
    
    db.add(script)
    db.commit()
    db.refresh(script)
    
    # Deduct credits
    background_tasks.add_task(deduct_credits, current_user.id, 10, db)
    
    return {
        "script": script_data,
        "script_id": script.id,
        "credits_used": 10
    }

@router.get("/", response_model=List[ScriptResponse])
async def get_scripts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scripts for current user"""
    
    scripts = db.query(Script).filter(
        Script.user_id == current_user.id
    ).order_by(desc(Script.created_at)).offset(skip).limit(limit).all()
    
    return scripts

@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.user_id == current_user.id
    ).first()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    return script

@router.put("/{script_id}")
async def update_script(
    script_id: int,
    script_update: ScriptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.user_id == current_user.id
    ).first()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # Update fields
    for field, value in script_update.dict(exclude_unset=True).items():
        setattr(script, field, value)
    
    db.commit()
    db.refresh(script)
    
    return {"message": "Script updated successfully", "script_id": script.id}

@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a script"""
    
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.user_id == current_user.id
    ).first()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    db.delete(script)
    db.commit()
    
    return {"message": "Script deleted successfully"}

@router.post("/{script_id}/regenerate")
async def regenerate_script(
    script_id: int,
    request: ScriptRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a script with new parameters"""
    
    # Check user credits
    if current_user.credits < 10:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Get existing script
    script = db.query(Script).filter(
        Script.id == script_id,
        Script.user_id == current_user.id
    ).first()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # Generate new script
    ai_service = AIService()
    result = await ai_service.generate_script(request)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    script_data = result["script"]
    
    # Update existing script
    script.title = script_data["title"]
    script.content = script_data["scenes"][0]["narration"] if script_data["scenes"] else ""
    script.hook = script_data.get("hook")
    script.scenes = script_data["scenes"]
    script.duration_estimate = script_data.get("duration_estimate")
    script.tone = request.tone
    script.status = "completed"
    script.metadata = {
        "keywords": script_data.get("keywords", []),
        "hashtags": script_data.get("hashtags", [])
    }
    
    db.commit()
    db.refresh(script)
    
    # Deduct credits
    background_tasks.add_task(deduct_credits, current_user.id, 10, db)
    
    return {
        "script": script_data,
        "script_id": script.id,
        "credits_used": 10
    }