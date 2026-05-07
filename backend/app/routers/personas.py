"""
Persona Routes - Phase 3B/4

CRUD endpoints for AI personas with OCEAN personality inference,
motto generation (Claude), and avatar generation (DALL-E).
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.persona import Persona
from app.models.moderation import ModerationAuditLog
from app.models.traits import PersonalityVector
from app.models.affinity import AffinityCalculator
from app.models.archetypes import get_all_archetypes
from app.services.ocean_inference import OceanInferenceService
from app.services.llm_service import LLMService
from app.services.image_generation_service import ImageGenerationService
from app.services.content_moderation_service import ContentModerationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["personas"])

VALID_ATTITUDES = {"Neutral", "Sarcastic", "Comical", "Somber", "Confrontational", "Blunt", "Cynical"}

class PersonaCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    attitude: Optional[str] = None
    model_used: Optional[str] = None
    is_public: bool = True

    @field_validator("attitude")
    @classmethod
    def validate_attitude(cls, v):
        if v is not None and v not in VALID_ATTITUDES:
            raise ValueError(f"attitude must be one of: {', '.join(sorted(VALID_ATTITUDES))}")
        return v

class CompatibilityRequest(BaseModel):
    persona_ids: List[str] = Field(..., min_length=2)

@router.post(
    "/personas",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new persona",
)
def create_persona(
    request: PersonaCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.display_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must set a display name before creating a persona."
        )

    # Step 1: Moderate content
    description = request.description or f"A person named {request.name}"
    try:
        mod_service = ContentModerationService()
        toxicity_score = mod_service.analyze_toxicity(description)
        if not mod_service.is_safe(toxicity_score):
            audit_log = ModerationAuditLog(
                content=description[:4096],
                toxicity_score=toxicity_score,
                source="persona_creation",
                source_id="blocked_before_save",
                action_taken="blocked",
            )
            db.add(audit_log)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content failed moderation check (score: {toxicity_score:.2f}). Please revise the description.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Content moderation check failed for '{request.name}': {e}")

    # Step 2: Infer OCEAN traits
    try:
        service = OceanInferenceService()
        ocean_scores = service.infer_ocean_traits(description)
    except Exception as e:
        logger.error(f"OCEAN inference failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OCEAN inference service failed: {e}",
        )

    # Step 3: Calculate archetype affinities
    persona_vector = PersonalityVector({
        "O": ocean_scores["openness"],
        "C": ocean_scores["conscientiousness"],
        "E": ocean_scores["extraversion"],
        "A": ocean_scores["agreeableness"],
        "N": ocean_scores["neuroticism"],
    })
    calculator = AffinityCalculator(get_all_archetypes())
    affinities = calculator.calculate(persona_vector)

    # Step 4: Generate motto
    persona_details = {
        "name": request.name,
        "description": description,
        "attitude": request.attitude or "Neutral",
        "ocean_scores": ocean_scores,
        "archetype_affinities": affinities,
    }
    motto = None
    try:
        llm_service = LLMService()
        motto = llm_service.generate_motto(persona_details)
    except Exception as e:
        logger.warning(f"Motto generation failed for '{request.name}': {e}")

    # Step 5: Generate avatar
    avatar_url = None
    try:
        img_service = ImageGenerationService()
        avatar_url = img_service.generate_avatar_for_persona({
            **persona_details,
            "age": request.age,
            "gender": request.gender,
            "model_used": request.model_used,
        })
    except Exception as e:
        logger.warning(f"Avatar generation failed for '{request.name}': {e}")

    # Step 6: Create persona in database
    persona = Persona(
        user_id=current_user.id,
        name=request.name,
        age=request.age,
        gender=request.gender,
        description=request.description,
        attitude=request.attitude,
        model_used=request.model_used,
        is_public=request.is_public,
        ocean_openness=ocean_scores["openness"],
        ocean_conscientiousness=ocean_scores["conscientiousness"],
        ocean_extraversion=ocean_scores["extraversion"],
        ocean_agreeableness=ocean_scores["agreeableness"],
        ocean_neuroticism=ocean_scores["neuroticism"],
        archetype_affinities=affinities,
        motto=motto,
        avatar_url=avatar_url,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)

    return persona.to_dict()

@router.get("/personas")
def list_personas(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    personas = db.query(Persona).filter(Persona.user_id == current_user.id).order_by(Persona.created_at.desc()).all()
    return [p.to_dict() for p in personas]

@router.get("/personas/public")
def list_public_personas(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), q: Optional[str] = None):
    query = db.query(Persona).filter(Persona.is_public == True, Persona.user_id != current_user.id).order_by(Persona.upvote_count.desc(), Persona.created_at.desc())
    if q:
        query = query.filter(Persona.name.ilike(f"%{q}%"))
    personas = query.limit(100).all()
    return [p.to_dict() for p in personas]

@router.get("/personas/{unique_id}")
def get_persona(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id, Persona.user_id == current_user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona.to_dict()

@router.delete("/personas/{unique_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id, Persona.user_id == current_user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(persona)
    db.commit()

@router.post("/personas/{unique_id}/regenerate-avatar")
def regenerate_persona_avatar(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id, Persona.user_id == current_user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    img_service = ImageGenerationService()
    new_avatar = img_service.generate_avatar_for_persona({
        "name": persona.name,
        "age": persona.age,
        "gender": persona.gender,
        "description": persona.description or "",
        "attitude": persona.attitude or "Neutral",
    })
    if not new_avatar:
        raise HTTPException(status_code=500, detail="Avatar generation failed")
    persona.avatar_url = new_avatar
    db.commit()
    db.refresh(persona)
    return persona.to_dict()

@router.post("/personas/compatibility")
def calculate_compatibility(request: CompatibilityRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    personas = db.query(Persona).filter(Persona.unique_id.in_(request.persona_ids), Persona.user_id == current_user.id).all()
    if len(personas) != len(request.persona_ids):
        raise HTTPException(status_code=404, detail="One or more personas not found")
    vectors = [PersonalityVector({"O": p.ocean_openness, "C": p.ocean_conscientiousness, "E": p.ocean_extraversion, "A": p.ocean_agreeableness, "N": p.ocean_neuroticism}) for p in personas]
    pairwise = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            dist = vectors[i].euclidean_distance(vectors[j])
            pairwise.append({"persona_a": personas[i].unique_id, "persona_b": personas[j].unique_id, "distance": round(float(dist), 4)})
    distances = [p["distance"] for p in pairwise]
    diversity_score = sum(distances) / len(distances) if distances else 0.0
    return {"diversity_score": round(diversity_score, 4), "pairwise_distances": pairwise, "persona_count": len(personas)}

@router.get("/archetypes")
def list_archetypes():
    return [{"code": a.code, "name": a.name, "description": a.description, "ocean_vector": a.ocean_vector.to_dict()} for a in get_all_archetypes()]
