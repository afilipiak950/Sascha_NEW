import asyncio
import logging
from datetime import datetime, timedelta
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.agents.interaction_agent import InteractionAgent
from app.agents.post_draft_agent import PostDraftAgent
from app.agents.connection_agent import ConnectionAgent
from app.agents.hashtag_agent import HashtagAgent

logger = logging.getLogger(__name__)

class AgentScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
        # Services initialisieren
        self.linkedin_service = LinkedInService()
        self.ai_service = AIService()
        
        # Agenten initialisieren
        self.interaction_agent = InteractionAgent(self.linkedin_service, self.ai_service)
        self.post_draft_agent = PostDraftAgent(self.linkedin_service, self.ai_service)
        self.connection_agent = ConnectionAgent(self.linkedin_service, self.ai_service)
        self.hashtag_agent = HashtagAgent(self.linkedin_service, self.ai_service)
        
        # Konfiguration
        self.posts_per_week = settings.POSTS_PER_WEEK
        self.connections_per_day = settings.CONNECTIONS_PER_DAY
        self.target_hashtags = settings.TARGET_HASHTAGS
        self.max_interactions_per_day = settings.MAX_INTERACTIONS_PER_DAY

    async def schedule_post_creation(self):
        """Plant die Erstellung von Posts"""
        try:
            # Beispiel-Themen (sollten eigentlich aus der Konfiguration kommen)
            topics = [
                "KI im Marketing",
                "LinkedIn Growth Hacks",
                "Content Marketing Trends",
                "Social Selling",
                "Personal Branding"
            ]
            
            await self.post_draft_agent.schedule_post_creation(
                topics=topics,
                posts_per_week=self.posts_per_week
            )
            
        except Exception as e:
            logger.error(f"Fehler bei der geplanten Post-Erstellung: {str(e)}")

    async def schedule_connections(self):
        """Plant die Vernetzung mit neuen Profilen"""
        try:
            # Hier müssten die Profile aus einer Queue oder Datenbank kommen
            profile_urls = [
                "https://linkedin.com/in/profile1",
                "https://linkedin.com/in/profile2",
                # ...
            ]
            
            await self.connection_agent.connect_with_profiles(
                profile_urls=profile_urls,
                send_message=True
            )
            
        except Exception as e:
            logger.error(f"Fehler bei der geplanten Vernetzung: {str(e)}")

    async def schedule_follow_ups(self):
        """Plant das Senden von Follow-up Nachrichten"""
        try:
            await self.connection_agent.send_follow_up(
                days_since_connection=3
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Senden von Follow-ups: {str(e)}")

    async def schedule_interactions(self):
        """Plant Interaktionen mit Posts in der Zielgruppe"""
        try:
            await self.interaction_agent.interact_with_target_group(
                hashtags=self.target_hashtags,
                max_interactions=self.max_interactions_per_day
            )
            
        except Exception as e:
            logger.error(f"Fehler bei den geplanten Interaktionen: {str(e)}")

    async def schedule_hashtag_comments(self):
        """Plant das Kommentieren von Hashtag-Posts"""
        try:
            await self.hashtag_agent.comment_on_hashtag_posts(
                hashtags=self.target_hashtags,
                max_comments_per_hashtag=5
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Kommentieren von Hashtag-Posts: {str(e)}")

    def start(self):
        """Startet den Scheduler mit allen Jobs"""
        try:
            # Post-Erstellung: 3-4x pro Woche (Montag, Mittwoch, Freitag)
            self.scheduler.add_job(
                self.schedule_post_creation,
                CronTrigger(day_of_week='mon,wed,fri', hour=10, minute=0),
                name='post_creation'
            )
            
            # Vernetzung: Täglich
            self.scheduler.add_job(
                self.schedule_connections,
                CronTrigger(hour=9, minute=0),
                name='connections'
            )
            
            # Follow-ups: Täglich
            self.scheduler.add_job(
                self.schedule_follow_ups,
                CronTrigger(hour=14, minute=0),
                name='follow_ups'
            )
            
            # Interaktionen: Mehrmals täglich
            for hour in [11, 13, 15, 17]:
                self.scheduler.add_job(
                    self.schedule_interactions,
                    CronTrigger(hour=hour, minute=random.randint(0, 59)),
                    name=f'interactions_{hour}'
                )
            
            # Hashtag-Kommentare: Mehrmals täglich
            for hour in [10, 12, 14, 16]:
                self.scheduler.add_job(
                    self.schedule_hashtag_comments,
                    CronTrigger(hour=hour, minute=random.randint(0, 59)),
                    name=f'hashtag_comments_{hour}'
                )
            
            # Scheduler starten
            self.scheduler.start()
            logger.info("Scheduler erfolgreich gestartet")
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Schedulers: {str(e)}")
            raise

    def stop(self):
        """Stoppt den Scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler erfolgreich gestoppt")
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Schedulers: {str(e)}")
            raise 