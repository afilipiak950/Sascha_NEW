from typing import List, Optional
import openai
from datetime import datetime
import json
import logging

from app.core.config import settings
from app.models.post import Post

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def generate_post_content(
        self,
        topic: str,
        tone: str = "professional",
        length: str = "medium",
        hashtags: Optional[List[str]] = None
    ) -> dict:
        """Generiert LinkedIn-Post-Inhalt mit GPT."""
        try:
            # Längen-Parameter in Token-Anzahl umrechnen
            length_tokens = {
                "short": 100,
                "medium": 200,
                "long": 300
            }.get(length, 200)

            # Prompt erstellen
            prompt = f"""
            Erstelle einen LinkedIn-Post zum Thema: {topic}
            
            Anforderungen:
            - Ton: {tone}
            - Länge: {length_tokens} Wörter
            - Format: Professionell, aber persönlich
            - Struktur: Einleitung, Hauptteil, Call-to-Action
            - Hashtags: {', '.join(hashtags) if hashtags else 'Relevante Hashtags'}
            
            Der Post soll:
            - Wertvolle Insights bieten
            - Engagement fördern
            - Authentisch wirken
            - LinkedIn-Best-Practices folgen
            """

            # GPT API aufrufen
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Content-Creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=length_tokens,
                temperature=0.7
            )

            # Antwort verarbeiten
            content = response.choices[0].message.content

            # Hashtags extrahieren (falls nicht explizit angegeben)
            if not hashtags:
                hashtags = [tag for tag in content.split() if tag.startswith("#")]

            return {
                "content": content,
                "hashtags": hashtags,
                "ai_generated": True,
                "generation_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Fehler bei der Content-Generierung: {str(e)}")
            raise

    async def generate_comment(self, post_content: str) -> str:
        """Generiert einen passenden Kommentar für einen LinkedIn-Post."""
        try:
            prompt = f"""
            Erstelle einen kurzen, engagierenden Kommentar für diesen LinkedIn-Post:
            
            {post_content}
            
            Der Kommentar soll:
            - Den Hauptpunkt des Posts aufgreifen
            - Einen Mehrwert bieten
            - Zur Diskussion anregen
            - Professionell und freundlich sein
            - Maximal 2-3 Sätze lang sein
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Networker."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Fehler bei der Kommentar-Generierung: {str(e)}")
            raise

    async def analyze_post_engagement(self, post: Post) -> dict:
        """Analysiert die Engagement-Metriken eines Posts und gibt Verbesserungsvorschläge."""
        try:
            metrics = json.loads(post.engagement_metrics) if post.engagement_metrics else {}
            
            prompt = f"""
            Analysiere diese LinkedIn-Post-Metriken und gib Verbesserungsvorschläge:
            
            Post-Inhalt: {post.content}
            Metriken: {json.dumps(metrics, indent=2)}
            
            Bitte analysiere:
            1. Engagement-Rate
            2. Kommentar-Qualität
            3. Reichweite
            4. Verbesserungspotenzial
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein LinkedIn-Content-Analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )

            return {
                "analysis": response.choices[0].message.content,
                "analysis_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Fehler bei der Post-Analyse: {str(e)}")
            raise 