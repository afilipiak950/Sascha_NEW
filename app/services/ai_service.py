from typing import List, Optional
import openai
from openai import OpenAI
from datetime import datetime
import json
import logging
import asyncio

from app.core.config import settings
from app.models.post import Post

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"  # Oder ein anderes verfügbares Modell
        self.max_retries = 3
        self.temperature = 0.7

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generiert Text mit GPT basierend auf einem Prompt"""
        try:
            for attempt in range(self.max_retries):
                try:
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "Du bist ein professioneller LinkedIn-Content-Ersteller."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.temperature,
                        max_tokens=max_tokens if max_tokens else 500,
                        n=1
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Fehler beim API-Aufruf, Versuch {attempt + 1} von {self.max_retries}")
                        await asyncio.sleep(2 ** attempt)  # Exponentielles Backoff
                        continue
                    raise
                    
        except Exception as e:
            logger.error(f"Fehler bei der Text-Generierung: {str(e)}")
            return json.dumps({
                "title": "Fehler bei der Generierung",
                "content": "Bitte versuchen Sie es erneut.",
                "hashtags": [],
                "optimal_time": "12:00",
                "estimated_engagement": "0"
            })

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
        tone: str = "professionell",
        length: str = "mittel",
        optimize_engagement: bool = False,
        add_hashtags: bool = True,
        optimize_timing: bool = False
    ) -> dict:
        """Generiert LinkedIn-Post-Inhalt"""
        try:
            prompt = f"""
            Erstelle einen LinkedIn-Post zum Thema: {topic}
            
            Anforderungen:
            - Tonalität: {tone}
            - Länge: {length}
            - Engagement optimieren: {"Ja" if optimize_engagement else "Nein"}
            - Hashtags: {"Ja" if add_hashtags else "Nein"}
            - Timing optimieren: {"Ja" if optimize_timing else "Nein"}
            
            Der Post soll:
            - Eine fesselnde Überschrift haben
            - Wertvollen Inhalt bieten
            - Authentisch und nicht zu werblich klingen
            - Relevante Hashtags enthalten (max. 5)
            
            Antworte NUR mit einem validen JSON-Objekt in diesem Format (keine zusätzlichen Erklärungen):
            {{"title": "Überschrift", "content": "Haupttext", "hashtags": ["hashtag1", "hashtag2"], "optimal_time": "HH:MM", "estimated_engagement": "85"}}
            """

            response = await self.generate_text(prompt)
            
            try:
                # Versuche das JSON zu parsen
                post_data = json.loads(response.strip())
                
                # Stelle sicher, dass alle erforderlichen Felder vorhanden sind
                required_fields = ["title", "content", "hashtags", "optimal_time", "estimated_engagement"]
                if not all(field in post_data for field in required_fields):
                    raise ValueError("Fehlende Felder in der API-Antwort")
                
                # Entferne Hashtags wenn nicht gewünscht
                if not add_hashtags:
                    post_data["hashtags"] = []
                    
                return post_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Fehler beim JSON-Parsing der API-Antwort: {str(e)}\nAntwort: {response}")
                return {
                    "title": "Fehler bei der Generierung",
                    "content": "Bitte versuchen Sie es erneut.",
                    "hashtags": [],
                    "optimal_time": "12:00",
                    "estimated_engagement": "0"
                }
                
        except Exception as e:
            logger.error(f"Fehler bei der Post-Generierung: {str(e)}")
            return {
                "title": "Fehler bei der Generierung",
                "content": "Bitte versuchen Sie es erneut.",
                "hashtags": [],
                "optimal_time": "12:00",
                "estimated_engagement": "0"
            }

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