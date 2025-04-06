from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services.ai_service import AIService
from app.services.linkedin_service import LinkedInService

router = APIRouter()
ai_service = AIService()
linkedin_service = LinkedInService()

@router.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db)
):
    """Erstellt einen neuen LinkedIn-Post."""
    try:
        # KI-generierten Content erstellen
        content = await ai_service.generate_post_content(
            topic=post.topic,
            tone=post.tone,
            length=post.length,
            hashtags=post.hashtags
        )
        
        # Post-Objekt erstellen
        db_post = Post(
            title=post.title,
            content=content["content"],
            hashtags=" ".join(content["hashtags"]),
            status=PostStatus.DRAFT,
            ai_generated=True,
            ai_prompt=f"Topic: {post.topic}"
        )
        
        # Als Entwurf in LinkedIn speichern
        success = await linkedin_service.create_draft_post(db_post)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Fehler beim Erstellen des LinkedIn-Post-Entwurfs"
            )
        
        # In Datenbank speichern
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        
        return db_post
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[PostStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """Ruft alle Posts ab, optional gefiltert nach Status."""
    try:
        query = db.query(Post)
        if status:
            query = query.filter(Post.status == status)
        posts = await query.offset(skip).limit(limit).all()
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ruft einen spezifischen Post ab."""
    try:
        post = await db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post nicht gefunden"
            )
        return post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Aktualisiert einen Post."""
    try:
        db_post = await db.query(Post).filter(Post.id == post_id).first()
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post nicht gefunden"
            )
        
        # Post aktualisieren
        for field, value in post_update.dict(exclude_unset=True).items():
            setattr(db_post, field, value)
        
        # Wenn der Post veröffentlicht werden soll
        if post_update.status == PostStatus.PUBLISHED:
            # TODO: Implementiere LinkedIn-Publishing
            pass
        
        await db.commit()
        await db.refresh(db_post)
        return db_post
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Löscht einen Post."""
    try:
        post = await db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post nicht gefunden"
            )
        
        await db.delete(post)
        await db.commit()
        
        return {"message": "Post erfolgreich gelöscht"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 