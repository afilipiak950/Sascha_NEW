from typing import List, Optional
from datetime import datetime
import logging
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.models.post import Post
from app.db.session import async_session
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

class PostDraftAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service

    async def generate_post_content(self, topic: str, tone: str = "professionell", length: str = "mittel") -> dict:
        """Generiert den Inhalt für einen LinkedIn-Post"""
        prompt = f"""
        Erstelle einen LinkedIn-Post zum Thema: {topic}
        
        Tonalität: {tone}
        Länge: {length}
        
        Der Post sollte:
        - Eine fesselnde Überschrift haben
        - Wertvollen Inhalt bieten
        - Authentisch und nicht zu werblich klingen
        - Relevante Hashtags enthalten (max. 5)
        
        Format:
        {{"title": "Überschrift", "content": "Haupttext", "hashtags": ["hashtag1", "hashtag2", ...]}}
        """
        
        response = await self.ai.generate_text(prompt)
        try:
            # Konvertiere den generierten Text in ein Dictionary
            # Hier müsste noch eine bessere Fehlerbehandlung implementiert werden
            return eval(response)
        except Exception as e:
            logger.error(f"Fehler beim Parsen des generierten Posts: {str(e)}")
            return {
                "title": "Fehler bei der Generierung",
                "content": "Bitte versuchen Sie es erneut.",
                "hashtags": []
            }

    async def create_post_draft(self, topic: str, tone: str = "professionell", length: str = "mittel") -> bool:
        """Erstellt einen Post-Entwurf und speichert ihn"""
        try:
            # Generiere Post-Inhalt
            post_data = await self.generate_post_content(topic, tone, length)
            
            # Speichere in der Datenbank
            async with async_session() as session:
                post = Post(
                    title=post_data["title"],
                    content=post_data["content"],
                    hashtags=post_data["hashtags"],
                    status="draft",
                    created_at=datetime.utcnow()
                )
                session.add(post)
                await session.commit()
            
            # Erstelle Draft in LinkedIn
            success = await self.linkedin.create_draft_post(
                post_data["title"],
                post_data["content"],
                post_data["hashtags"]
            )
            
            if success:
                logger.info(f"Post-Entwurf erfolgreich erstellt: {post_data['title']}")
                return True
            else:
                logger.error("Fehler beim Erstellen des LinkedIn-Entwurfs")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Post-Entwurfs: {str(e)}")
            return False

    async def get_draft_posts(self, limit: int = 10) -> List[dict]:
        """Ruft die letzten Draft-Posts aus der Datenbank ab"""
        try:
            async with async_session() as session:
                query = select(Post).where(
                    Post.status == "draft"
                ).order_by(
                    Post.created_at.desc()
                ).limit(limit)
                
                result = await session.execute(query)
                posts = result.scalars().all()
                
                return [
                    {
                        "id": post.id,
                        "title": post.title,
                        "content": post.content,
                        "hashtags": post.hashtags,
                        "created_at": post.created_at.isoformat()
                    }
                    for post in posts
                ]
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Draft-Posts: {str(e)}")
            return []

    async def schedule_post_creation(self, topics: List[str], posts_per_week: int = 3):
        """Plant die Erstellung mehrerer Posts"""
        try:
            for topic in topics[:posts_per_week]:
                success = await self.create_post_draft(topic)
                if not success:
                    logger.warning(f"Konnte keinen Post zum Thema '{topic}' erstellen")
                
        except Exception as e:
            logger.error(f"Fehler bei der geplanten Post-Erstellung: {str(e)}")
            raise 