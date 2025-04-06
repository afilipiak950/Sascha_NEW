from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import random
import logging
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.models.comment import Comment
from app.db.session import async_session
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

class HashtagAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service
        self.min_delay = 45  # Minimale Verzögerung zwischen Kommentaren (Sekunden)
        self.max_delay = 240  # Maximale Verzögerung zwischen Kommentaren (Sekunden)

    async def generate_comment(self, post_text: str, hashtag: str) -> str:
        """Generiert einen relevanten Kommentar für einen Post"""
        prompt = f"""
        Generiere einen professionellen Kommentar für den folgenden LinkedIn-Post zum Thema #{hashtag}.
        
        Post-Text: {post_text}
        
        Der Kommentar sollte:
        - Relevant und wertvoll sein
        - Eine persönliche Perspektive oder Erfahrung einbringen
        - Zwischen 100-200 Zeichen lang sein
        - Authentisch und nicht werblich klingen
        - Keine Emojis enthalten
        """
        return await self.ai.generate_text(prompt)

    async def comment_on_hashtag_posts(self, hashtags: List[str], max_comments_per_hashtag: int = 5):
        """Kommentiert Posts mit bestimmten Hashtags"""
        try:
            total_comments = 0
            
            for hashtag in hashtags:
                try:
                    # Suche nach Posts mit dem Hashtag
                    posts = await self.linkedin.search_posts_by_hashtag(hashtag, limit=max_comments_per_hashtag)
                    
                    for post in posts:
                        try:
                            # Prüfe, ob wir diesen Post bereits kommentiert haben
                            async with async_session() as session:
                                query = select(Comment).where(Comment.post_url == post["url"])
                                result = await session.execute(query)
                                existing_comment = result.scalar_one_or_none()
                                
                                if existing_comment:
                                    logger.info(f"Post wurde bereits kommentiert: {post['url']}")
                                    continue
                            
                            # Zufällige Verzögerung
                            delay = random.uniform(self.min_delay, self.max_delay)
                            await asyncio.sleep(delay)
                            
                            # Generiere und sende Kommentar
                            comment_text = await self.generate_comment(post["text"], hashtag)
                            success = await self.linkedin.interact_with_post(
                                post["url"],
                                "comment",
                                comment_text
                            )
                            
                            # Speichere in der Datenbank
                            async with async_session() as session:
                                comment = Comment(
                                    post_url=post["url"],
                                    hashtag=hashtag,
                                    content=comment_text,
                                    status="success" if success else "failed",
                                    created_at=datetime.utcnow()
                                )
                                session.add(comment)
                                await session.commit()
                            
                            if success:
                                total_comments += 1
                                logger.info(f"Kommentar erfolgreich gepostet für #{hashtag}: {post['url']}")
                            else:
                                logger.error(f"Fehler beim Kommentieren des Posts: {post['url']}")
                            
                        except Exception as e:
                            logger.error(f"Fehler beim Kommentieren eines Posts für #{hashtag}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Fehler bei der Verarbeitung von #{hashtag}: {str(e)}")
                    continue
                    
            logger.info(f"Hashtag-Kommentar-Session beendet. {total_comments} Kommentare gepostet.")
            
        except Exception as e:
            logger.error(f"Fehler während der Hashtag-Kommentar-Session: {str(e)}")
            raise

    async def get_comment_stats(self, days: int = 7) -> dict:
        """Gibt Statistiken über die Hashtag-Kommentare zurück"""
        try:
            async with async_session() as session:
                since_date = datetime.utcnow() - timedelta(days=days)
                
                # Abfrage für alle Kommentare im Zeitraum
                query = select(Comment).where(
                    Comment.created_at >= since_date
                )
                result = await session.execute(query)
                comments = result.scalars().all()
                
                # Statistiken berechnen
                stats = {
                    "total": len(comments),
                    "successful": len([c for c in comments if c.status == "success"]),
                    "failed": len([c for c in comments if c.status == "failed"]),
                    "by_hashtag": {},
                    "by_day": {}
                }
                
                # Gruppiere nach Hashtag
                for comment in comments:
                    if comment.hashtag not in stats["by_hashtag"]:
                        stats["by_hashtag"][comment.hashtag] = {
                            "total": 0,
                            "successful": 0,
                            "failed": 0
                        }
                    
                    stats["by_hashtag"][comment.hashtag]["total"] += 1
                    if comment.status == "success":
                        stats["by_hashtag"][comment.hashtag]["successful"] += 1
                    else:
                        stats["by_hashtag"][comment.hashtag]["failed"] += 1
                
                # Gruppiere nach Tag
                for comment in comments:
                    day = comment.created_at.date()
                    if day not in stats["by_day"]:
                        stats["by_day"][day] = {
                            "total": 0,
                            "successful": 0,
                            "failed": 0
                        }
                    
                    stats["by_day"][day]["total"] += 1
                    if comment.status == "success":
                        stats["by_day"][day]["successful"] += 1
                    else:
                        stats["by_day"][day]["failed"] += 1
                
                return stats
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Kommentar-Statistiken: {str(e)}")
            return {} 