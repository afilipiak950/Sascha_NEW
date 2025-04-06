from typing import List, Optional
import openai
from datetime import datetime
import json
import logging
import asyncio

from app.core.config import settings
from app.models.post import Post

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4"  # Oder ein anderes verfügbares Modell
        self.max_retries = 3
        self.temperature = 0.7

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generiert Text mit GPT basierend auf einem Prompt"""
        try:
            for attempt in range(self.max_retries):
                try:
                    response = await openai.ChatCompletion.acreate(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "Du bist ein professioneller LinkedIn-Content-Ersteller."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.temperature,
                        max_tokens=max_tokens if max_tokens else 500,
                        n=1,
                        stop=None
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except openai.error.RateLimitError:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Rate limit erreicht, Versuch {attempt + 1} von {self.max_retries}")
                        await asyncio.sleep(2 ** attempt)  # Exponentielles Backoff
                        continue
                    raise
                    
        except Exception as e:
            logger.error(f"Fehler bei der Text-Generierung: {str(e)}")
            return "Fehler bei der Text-Generierung. Bitte versuchen Sie es später erneut."

    async def analyze_sentiment(self, text: str) -> dict:
        """Analysiert die Stimmung eines Textes"""
        try:
            prompt = f"""
            Analysiere die Stimmung des folgenden Textes und gib eine JSON-Antwort zurück:
            
            Text: {text}
            
            Format:
            {{"sentiment": "positiv|neutral|negativ", "confidence": 0.0-1.0}}
            """
            
            response = await self.generate_text(prompt)
            return eval(response)  # Konvertiert den String in ein Dictionary
            
        except Exception as e:
            logger.error(f"Fehler bei der Stimmungsanalyse: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0}

    async def generate_hashtags(self, text: str, count: int = 5) -> list:
        """Generiert relevante Hashtags für einen Text"""
        try:
            prompt = f"""
            Generiere {count} relevante LinkedIn-Hashtags für den folgenden Text.
            Die Hashtags sollten professionell und branchenrelevant sein.
            
            Text: {text}
            
            Antworte nur mit einer Liste von Hashtags im Format: ["hashtag1", "hashtag2", ...]
            """
            
            response = await self.generate_text(prompt)
            return eval(response)  # Konvertiert den String in eine Liste
            
        except Exception as e:
            logger.error(f"Fehler bei der Hashtag-Generierung: {str(e)}")
            return []

    async def improve_text(self, text: str, target: str = "engagement") -> str:
        """Verbessert einen Text für mehr Engagement"""
        try:
            prompt = f"""
            Verbessere den folgenden Text für mehr {target} auf LinkedIn.
            Der Text sollte professionell und authentisch bleiben.
            
            Original: {text}
            
            Verbesserungen sollten:
            - Die Kernbotschaft beibehalten
            - Die Lesbarkeit verbessern
            - Call-to-Actions hinzufügen
            - Mehr Engagement generieren
            """
            
            return await self.generate_text(prompt)
            
        except Exception as e:
            logger.error(f"Fehler bei der Text-Verbesserung: {str(e)}")
            return text  # Gib den Original-Text zurück, wenn ein Fehler auftritt

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
        """Analysiert die Engagement-Metriken eines Posts und gib Verbesserungsvorschläge."""
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