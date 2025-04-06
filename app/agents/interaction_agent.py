from typing import List, Optional
import asyncio
import random
from datetime import datetime, timedelta
import logging
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.models.interaction import Interaction
from app.db.session import async_session
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

class InteractionAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service
        self.min_delay = 30  # Minimale Verzögerung zwischen Interaktionen (Sekunden)
        self.max_delay = 180  # Maximale Verzögerung zwischen Interaktionen (Sekunden)

    async def generate_comment(self, post_text: str) -> str:
        """Generiert einen Kommentar basierend auf dem Post-Text"""
        prompt = f"""
        Generiere einen professionellen und relevanten Kommentar für den folgenden LinkedIn-Post.
        Der Kommentar sollte authentisch wirken und einen Mehrwert bieten.
        
        Post: {post_text}
        """
        return await self.ai.generate_text(prompt)

    async def interact_with_target_group(self, hashtags: List[str], max_interactions: int = 10):
        """Interagiert mit Posts in der Zielgruppe"""
        try:
            total_interactions = 0
            
            for hashtag in hashtags:
                if total_interactions >= max_interactions:
                    break
                    
                posts = await self.linkedin.search_posts_by_hashtag(hashtag)
                
                for post in posts:
                    if total_interactions >= max_interactions:
                        break
                        
                    # Zufällige Verzögerung
                    delay = random.uniform(self.min_delay, self.max_delay)
                    await asyncio.sleep(delay)
                    
                    # Entscheide zufällig zwischen Like und Kommentar
                    action = random.choice(["like", "comment"])
                    
                    if action == "like":
                        success = await self.linkedin.interact_with_post(post["url"], "like")
                    else:
                        comment = await self.generate_comment(post["text"])
                        success = await self.linkedin.interact_with_post(post["url"], "comment", comment)
                    
                    if success:
                        # Speichere Interaktion in der Datenbank
                        async with async_session() as session:
                            interaction = Interaction(
                                type=action,
                                target_url=post["url"],
                                content=comment if action == "comment" else None,
                                status="success",
                                created_at=datetime.utcnow()
                            )
                            session.add(interaction)
                            await session.commit()
                        
                        total_interactions += 1
                        logger.info(f"Erfolgreiche {action}-Interaktion mit Post: {post['url']}")
                    
            logger.info(f"Interaktions-Session beendet. {total_interactions} erfolgreiche Interaktionen.")
            
        except Exception as e:
            logger.error(f"Fehler während der Interaktions-Session: {str(e)}")
            raise

    async def get_interaction_stats(self, days: int = 7) -> dict:
        """Gibt Statistiken über die letzten Interaktionen zurück"""
        try:
            async with async_session() as session:
                since_date = datetime.utcnow() - timedelta(days=days)
                
                # Abfrage für erfolgreiche Interaktionen
                query = select(Interaction).where(
                    Interaction.created_at >= since_date,
                    Interaction.status == "success"
                )
                result = await session.execute(query)
                interactions = result.scalars().all()
                
                # Statistiken berechnen
                stats = {
                    "total": len(interactions),
                    "likes": len([i for i in interactions if i.type == "like"]),
                    "comments": len([i for i in interactions if i.type == "comment"]),
                    "by_day": {}
                }
                
                # Gruppiere nach Tag
                for interaction in interactions:
                    day = interaction.created_at.date()
                    if day not in stats["by_day"]:
                        stats["by_day"][day] = {"likes": 0, "comments": 0}
                    
                    if interaction.type == "like":
                        stats["by_day"][day]["likes"] += 1
                    else:
                        stats["by_day"][day]["comments"] += 1
                
                return stats
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Interaktions-Statistiken: {str(e)}")
            return {} 