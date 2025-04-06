from typing import Dict, List
import time
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.linkedin import LinkedInService
from app.services.openai import OpenAIService
from app.models.post import Post, PostStatus
from app.models.interaction import Interaction, InteractionType, InteractionStatus
from app.models.settings import Settings
from app.db.session import SessionLocal

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.linkedin_service = LinkedInService()
        self.openai_service = OpenAIService()
        self.settings = None
        self.is_running = False
        self.db = SessionLocal()

    def __del__(self):
        """Cleanup beim Beenden des Services"""
        self.db.close()
        self.linkedin_service.close()

    def start(self, settings: Settings):
        """Scheduler mit den gegebenen Einstellungen starten"""
        self.settings = settings
        self.is_running = True
        
        # Posts planen
        self.schedule_posts()
        
        # Interaktionen planen
        self.schedule_interactions()
        
        # Scheduler starten
        self.scheduler.start()

    def stop(self):
        """Scheduler stoppen"""
        self.is_running = False
        self.scheduler.shutdown()

    def schedule_posts(self):
        """Posts nach den Einstellungen planen"""
        if not self.settings or not self.settings.post_frequency:
            return
        
        # Posts pro Woche in Tage aufteilen
        posts_per_week = self.settings.post_frequency
        days = random.sample(range(7), posts_per_week)
        
        for day in days:
            # Zufällige Uhrzeit zwischen 9 und 17 Uhr
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            
            # Cron-Trigger für jeden Tag der Woche
            trigger = CronTrigger(
                day_of_week=day,
                hour=hour,
                minute=minute
            )
            
            self.scheduler.add_job(
                self.create_post,
                trigger=trigger,
                id=f"post_{day}_{hour}_{minute}",
                replace_existing=True
            )

    def schedule_interactions(self):
        """Interaktionen nach den Einstellungen planen"""
        if not self.settings or not self.settings.interaction_interval:
            return
        
        # Intervall in Minuten
        interval = self.settings.interaction_interval
        
        # Cron-Trigger für regelmäßige Interaktionen
        trigger = CronTrigger(
            minute=f"*/{interval}"
        )
        
        self.scheduler.add_job(
            self.perform_interaction,
            trigger=trigger,
            id="interaction",
            replace_existing=True
        )

    def create_post(self):
        """Einen neuen Post erstellen"""
        if not self.is_running or not self.settings:
            return
        
        try:
            # Zufälliges Thema auswählen
            topic = random.choice(self.settings.post_topics)
            tone = random.choice(self.settings.post_tones)
            length = random.choice(self.settings.post_lengths)
            hashtags = random.sample(self.settings.post_hashtags, 3)
            
            # Post mit GPT generieren
            content = self.openai_service.generate_post(
                topic=topic,
                tone=tone,
                length=length,
                hashtags=hashtags
            )
            
            if not content:
                return
            
            # Post erstellen
            post = Post(
                title=topic,
                content=content,
                hashtags=",".join(hashtags),
                status=PostStatus.DRAFT,
                user_id=self.settings.user_id
            )
            
            # Post veröffentlichen oder als Entwurf speichern
            if self.settings.auto_publish_posts:
                success = self.linkedin_service.create_post(post)
                if success:
                    post.status = PostStatus.PUBLISHED
                    post.published_at = datetime.now()
            
            # Post in der Datenbank speichern
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
        except Exception as e:
            self.db.rollback()
            print(f"Post-Erstellung fehlgeschlagen: {str(e)}")

    def perform_interaction(self):
        """Eine Interaktion durchführen"""
        if not self.is_running or not self.settings:
            return
        
        try:
            # Zufälligen Interaktionstyp auswählen
            interaction_type = random.choice(self.settings.interaction_types)
            
            if interaction_type == InteractionType.LIKE:
                self.perform_like()
            elif interaction_type == InteractionType.COMMENT:
                self.perform_comment()
            elif interaction_type == InteractionType.CONNECTION:
                self.perform_connection()
            elif interaction_type == InteractionType.MESSAGE:
                self.perform_message()
            elif interaction_type == InteractionType.SHARE:
                self.perform_share()
            
            # Zufällige Pause einlegen
            time.sleep(random.randint(30, 120))
            
        except Exception as e:
            print(f"Interaktion fehlgeschlagen: {str(e)}")

    def perform_like(self):
        """Einen Beitrag liken"""
        try:
            # Nach Beiträgen suchen, die noch nicht geliked wurden
            search_query = " ".join(self.settings.target_keywords)
            posts = self.linkedin_service.search_profiles(
                keywords=[search_query],
                filters={
                    "industry": self.settings.target_industries,
                    "location": self.settings.target_locations
                }
            )
            
            if not posts:
                return
            
            # Zufälligen Post auswählen und liken
            post = random.choice(posts)
            success = self.linkedin_service.like_post(post["url"])
            
            if success:
                # Interaktion in der Datenbank speichern
                interaction = Interaction(
                    type=InteractionType.LIKE,
                    status=InteractionStatus.COMPLETED,
                    target_id=post["id"],
                    target_name=post["name"],
                    target_title=post["title"],
                    user_id=self.settings.user_id
                )
                self.db.add(interaction)
                self.db.commit()
                self.db.refresh(interaction)
                
        except Exception as e:
            self.db.rollback()
            print(f"Like fehlgeschlagen: {str(e)}")

    def perform_comment(self):
        """Einen Kommentar verfassen"""
        try:
            # Nach Beiträgen suchen, die noch nicht kommentiert wurden
            search_query = " ".join(self.settings.target_keywords)
            posts = self.linkedin_service.search_profiles(
                keywords=[search_query],
                filters={
                    "industry": self.settings.target_industries,
                    "location": self.settings.target_locations
                }
            )
            
            if not posts:
                return
            
            # Zufälligen Post auswählen
            post = random.choice(posts)
            
            # Kommentar mit GPT generieren
            comment = self.openai_service.generate_comment(
                post_content=post["content"],
                tone=random.choice(self.settings.post_tones)
            )
            
            if not comment:
                return
            
            # Kommentar veröffentlichen
            success = self.linkedin_service.comment_on_post(post["url"], comment)
            
            if success:
                # Interaktion in der Datenbank speichern
                interaction = Interaction(
                    type=InteractionType.COMMENT,
                    status=InteractionStatus.COMPLETED,
                    target_id=post["id"],
                    target_name=post["name"],
                    target_title=post["title"],
                    content=comment,
                    user_id=self.settings.user_id
                )
                self.db.add(interaction)
                self.db.commit()
                self.db.refresh(interaction)
                
        except Exception as e:
            self.db.rollback()
            print(f"Kommentar fehlgeschlagen: {str(e)}")

    def perform_connection(self):
        """Eine Verbindungsanfrage senden"""
        try:
            # Nach Profilen suchen, die noch nicht verbunden sind
            search_query = " ".join(self.settings.target_keywords)
            profiles = self.linkedin_service.search_profiles(
                keywords=[search_query],
                filters={
                    "industry": self.settings.target_industries,
                    "location": self.settings.target_locations
                }
            )
            
            if not profiles:
                return
            
            # Zufälliges Profil auswählen
            profile = random.choice(profiles)
            
            # Verbindungsnachricht mit GPT generieren
            message = self.openai_service.generate_connection_message(
                profile_info=profile,
                template=random.choice(self.settings.message_templates["connection"])
            )
            
            if not message:
                return
            
            # Verbindungsanfrage senden
            success = self.linkedin_service.send_connection_request(profile["url"], message)
            
            if success:
                # Interaktion in der Datenbank speichern
                interaction = Interaction(
                    type=InteractionType.CONNECTION,
                    status=InteractionStatus.COMPLETED,
                    target_id=profile["id"],
                    target_name=profile["name"],
                    target_title=profile["title"],
                    content=message,
                    user_id=self.settings.user_id
                )
                self.db.add(interaction)
                self.db.commit()
                self.db.refresh(interaction)
                
        except Exception as e:
            self.db.rollback()
            print(f"Verbindungsanfrage fehlgeschlagen: {str(e)}")

    def perform_message(self):
        """Eine Nachricht senden"""
        try:
            # Nach verbundenen Profilen suchen, die noch keine Nachricht erhalten haben
            search_query = " ".join(self.settings.target_keywords)
            profiles = self.linkedin_service.search_profiles(
                keywords=[search_query],
                filters={
                    "industry": self.settings.target_industries,
                    "location": self.settings.target_locations,
                    "connection_status": "connected"
                }
            )
            
            if not profiles:
                return
            
            # Zufälliges Profil auswählen
            profile = random.choice(profiles)
            
            # Nachricht mit GPT generieren
            message = self.openai_service.generate_follow_up_message(
                profile_info=profile,
                template=random.choice(self.settings.message_templates["follow_up"])
            )
            
            if not message:
                return
            
            # Nachricht senden
            success = self.linkedin_service.send_message(profile["url"], message)
            
            if success:
                # Interaktion in der Datenbank speichern
                interaction = Interaction(
                    type=InteractionType.MESSAGE,
                    status=InteractionStatus.COMPLETED,
                    target_id=profile["id"],
                    target_name=profile["name"],
                    target_title=profile["title"],
                    content=message,
                    user_id=self.settings.user_id
                )
                self.db.add(interaction)
                self.db.commit()
                self.db.refresh(interaction)
                
        except Exception as e:
            self.db.rollback()
            print(f"Nachricht fehlgeschlagen: {str(e)}")

    def perform_share(self):
        """Einen Beitrag teilen"""
        try:
            # Nach Beiträgen suchen, die noch nicht geteilt wurden
            search_query = " ".join(self.settings.target_keywords)
            posts = self.linkedin_service.search_profiles(
                keywords=[search_query],
                filters={
                    "industry": self.settings.target_industries,
                    "location": self.settings.target_locations
                }
            )
            
            if not posts:
                return
            
            # Zufälligen Post auswählen
            post = random.choice(posts)
            
            # Beitrag teilen
            success = self.linkedin_service.share_post(post["url"])
            
            if success:
                # Interaktion in der Datenbank speichern
                interaction = Interaction(
                    type=InteractionType.SHARE,
                    status=InteractionStatus.COMPLETED,
                    target_id=post["id"],
                    target_name=post["name"],
                    target_title=post["title"],
                    user_id=self.settings.user_id
                )
                self.db.add(interaction)
                self.db.commit()
                self.db.refresh(interaction)
                
        except Exception as e:
            self.db.rollback()
            print(f"Teilen fehlgeschlagen: {str(e)}") 