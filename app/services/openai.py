from typing import List, Dict, Optional
import openai
from app.core.config import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        openai.api_base = settings.OPENAI_API_URL

    def generate_post(self, topic: str, tone: str, length: str, hashtags: List[str]) -> str:
        """Einen LinkedIn-Beitrag mit GPT generieren"""
        try:
            # Prompt für die Beitragsgenerierung
            prompt = f"""Erstelle einen LinkedIn-Beitrag zum Thema "{topic}".
            Ton: {tone}
            Länge: {length}
            Hashtags: {', '.join(hashtags)}
            
            Der Beitrag sollte:
            - Professionell und informativ sein
            - Eine klare Struktur haben
            - Zum Nachdenken anregen
            - Engagement fördern
            - Die Hashtags natürlich einbinden
            
            Beitrag:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Content-Ersteller."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Beitragsgenerierung fehlgeschlagen: {str(e)}")
            return ""

    def generate_comment(self, post_content: str, tone: str) -> str:
        """Einen Kommentar zu einem Beitrag generieren"""
        try:
            prompt = f"""Erstelle einen Kommentar zu diesem LinkedIn-Beitrag:
            "{post_content}"
            
            Der Kommentar sollte:
            - Den Ton "{tone}" verwenden
            - Wertvoll und konstruktiv sein
            - Eine Frage oder einen Diskussionspunkt enthalten
            - Natürlich und authentisch wirken
            
            Kommentar:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Nutzer, der wertvolle Kommentare verfasst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Kommentargenerierung fehlgeschlagen: {str(e)}")
            return ""

    def generate_connection_message(self, profile_info: Dict[str, str], template: str) -> str:
        """Eine personalisierte Verbindungsnachricht generieren"""
        try:
            prompt = f"""Erstelle eine personalisierte LinkedIn-Verbindungsnachricht für:
            Name: {profile_info.get('name')}
            Position: {profile_info.get('title')}
            
            Verwende diese Vorlage als Basis:
            "{template}"
            
            Die Nachricht sollte:
            - Personalisiert und authentisch sein
            - Einen klaren Mehrwert bieten
            - Zum Handeln auffordern
            - Natürlich und nicht aufdringlich wirken
            
            Nachricht:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Networker, der personalisierte Verbindungsnachrichten verfasst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Nachrichtengenerierung fehlgeschlagen: {str(e)}")
            return ""

    def generate_follow_up_message(self, profile_info: Dict[str, str], template: str) -> str:
        """Eine Follow-up-Nachricht nach der Verbindung generieren"""
        try:
            prompt = f"""Erstelle eine Follow-up-Nachricht nach der LinkedIn-Verbindung für:
            Name: {profile_info.get('name')}
            Position: {profile_info.get('title')}
            
            Verwende diese Vorlage als Basis:
            "{template}"
            
            Die Nachricht sollte:
            - Freundlich und einladend sein
            - Einen konkreten nächsten Schritt vorschlagen
            - Kurz und prägnant sein
            - Natürlich und nicht aufdringlich wirken
            
            Nachricht:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener LinkedIn-Networker, der effektive Follow-up-Nachrichten verfasst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Follow-up-Nachrichtengenerierung fehlgeschlagen: {str(e)}")
            return "" 