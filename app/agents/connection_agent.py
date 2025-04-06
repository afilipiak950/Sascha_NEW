from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import random
import logging
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.models.connection import Connection
from app.db.session import async_session
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

class ConnectionAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service
        self.max_connections_per_day = 39
        self.min_delay = 60  # Minimale Verzögerung zwischen Verbindungen (Sekunden)
        self.max_delay = 300  # Maximale Verzögerung zwischen Verbindungen (Sekunden)

    async def generate_connection_message(self, profile_info: dict) -> str:
        """Generiert eine personalisierte Verbindungsanfrage"""
        prompt = f"""
        Generiere eine kurze, personalisierte Verbindungsanfrage für ein LinkedIn-Profil.
        Die Nachricht sollte authentisch und nicht zu werblich sein.
        
        Profilinformationen:
        Name: {profile_info.get('name', '')}
        Position: {profile_info.get('title', '')}
        Unternehmen: {profile_info.get('company', '')}
        
        Die Nachricht sollte:
        - Höflich und professionell sein
        - Einen persönlichen Bezug herstellen
        - Maximal 300 Zeichen lang sein
        - Keine Emojis enthalten
        """
        return await self.ai.generate_text(prompt)

    async def connect_with_profiles(self, profile_urls: List[str], send_message: bool = True):
        """Sendet Verbindungsanfragen an eine Liste von Profilen"""
        try:
            # Prüfe, wie viele Verbindungen heute schon gesendet wurden
            async with async_session() as session:
                today = datetime.utcnow().date()
                query = select(Connection).where(
                    Connection.created_at >= today,
                    Connection.status == "sent"
                )
                result = await session.execute(query)
                connections_today = len(result.scalars().all())
                
                if connections_today >= self.max_connections_per_day:
                    logger.warning("Tägliches Verbindungslimit erreicht")
                    return
                
                remaining_connections = self.max_connections_per_day - connections_today
                
            for profile_url in profile_urls[:remaining_connections]:
                try:
                    # Prüfe, ob bereits eine Verbindungsanfrage gesendet wurde
                    async with async_session() as session:
                        query = select(Connection).where(Connection.profile_url == profile_url)
                        result = await session.execute(query)
                        existing_connection = result.scalar_one_or_none()
                        
                        if existing_connection:
                            logger.info(f"Profil wurde bereits kontaktiert: {profile_url}")
                            continue
                    
                    # Zufällige Verzögerung
                    delay = random.uniform(self.min_delay, self.max_delay)
                    await asyncio.sleep(delay)
                    
                    # Generiere personalisierte Nachricht
                    message = None
                    if send_message:
                        # Hier müssten wir noch die Profilinformationen abrufen
                        profile_info = {
                            "name": "Name",  # Placeholder
                            "title": "Title",
                            "company": "Company"
                        }
                        message = await self.generate_connection_message(profile_info)
                    
                    # Sende Verbindungsanfrage
                    success = await self.linkedin.connect_with_profile(profile_url, message)
                    
                    # Speichere in der Datenbank
                    async with async_session() as session:
                        connection = Connection(
                            profile_url=profile_url,
                            message=message,
                            status="sent" if success else "failed",
                            created_at=datetime.utcnow()
                        )
                        session.add(connection)
                        await session.commit()
                    
                    if success:
                        logger.info(f"Verbindungsanfrage erfolgreich gesendet: {profile_url}")
                    else:
                        logger.error(f"Fehler beim Senden der Verbindungsanfrage: {profile_url}")
                    
                except Exception as e:
                    logger.error(f"Fehler bei Profil {profile_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Fehler während der Verbindungs-Session: {str(e)}")
            raise

    async def send_follow_up(self, days_since_connection: int = 3):
        """Sendet Follow-up Nachrichten an kürzlich verbundene Profile"""
        try:
            async with async_session() as session:
                # Finde Verbindungen, die vor X Tagen akzeptiert wurden und noch kein Follow-up haben
                target_date = datetime.utcnow() - timedelta(days=days_since_connection)
                query = select(Connection).where(
                    Connection.status == "accepted",
                    Connection.accepted_at <= target_date,
                    Connection.follow_up_sent == False
                )
                result = await session.execute(query)
                connections = result.scalars().all()
                
                for connection in connections:
                    try:
                        # Generiere Follow-up Nachricht
                        prompt = f"""
                        Generiere eine kurze Follow-up Nachricht für eine LinkedIn-Verbindung.
                        Die Nachricht sollte:
                        - Sich für die Annahme der Verbindung bedanken
                        - Einen Mehrwert bieten (z.B. relevante Ressource teilen)
                        - Nicht zu werblich sein
                        - Maximal 500 Zeichen lang sein
                        """
                        message = await self.ai.generate_text(prompt)
                        
                        # Sende die Nachricht
                        # Hier müsste noch die eigentliche Nachrichtenfunktion implementiert werden
                        # await self.linkedin.send_message(connection.profile_url, message)
                        
                        # Update den Follow-up Status
                        connection.follow_up_sent = True
                        connection.follow_up_message = message
                        connection.follow_up_sent_at = datetime.utcnow()
                        await session.commit()
                        
                        logger.info(f"Follow-up Nachricht gesendet an: {connection.profile_url}")
                        
                        # Zufällige Verzögerung
                        delay = random.uniform(self.min_delay, self.max_delay)
                        await asyncio.sleep(delay)
                        
                    except Exception as e:
                        logger.error(f"Fehler beim Senden des Follow-ups an {connection.profile_url}: {str(e)}")
                        continue
                    
        except Exception as e:
            logger.error(f"Fehler beim Senden von Follow-ups: {str(e)}")
            raise

    async def get_connection_stats(self, days: int = 7) -> dict:
        """Gibt Statistiken über die Verbindungsanfragen zurück"""
        try:
            async with async_session() as session:
                since_date = datetime.utcnow() - timedelta(days=days)
                
                # Abfrage für alle Verbindungen im Zeitraum
                query = select(Connection).where(
                    Connection.created_at >= since_date
                )
                result = await session.execute(query)
                connections = result.scalars().all()
                
                # Statistiken berechnen
                stats = {
                    "total": len(connections),
                    "sent": len([c for c in connections if c.status == "sent"]),
                    "accepted": len([c for c in connections if c.status == "accepted"]),
                    "failed": len([c for c in connections if c.status == "failed"]),
                    "follow_ups_sent": len([c for c in connections if c.follow_up_sent]),
                    "by_day": {}
                }
                
                # Gruppiere nach Tag
                for connection in connections:
                    day = connection.created_at.date()
                    if day not in stats["by_day"]:
                        stats["by_day"][day] = {
                            "sent": 0,
                            "accepted": 0,
                            "failed": 0,
                            "follow_ups": 0
                        }
                    
                    stats["by_day"][day][connection.status] += 1
                    if connection.follow_up_sent:
                        stats["by_day"][day]["follow_ups"] += 1
                
                return stats
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Verbindungs-Statistiken: {str(e)}")
            return {} 