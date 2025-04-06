from typing import Optional, List, Dict
import json
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page
import asyncio
import random
import logging

from app.core.config import settings
from app.models.post import Post, PostStatus
from app.models.interaction import Interaction, InteractionType
from app.models.target_contact import TargetContact, ContactStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False

    async def init(self):
        """Initialisiert den Browser und die Seite"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS
            )
            self.page = await self.browser.new_page()
            if settings.BROWSER_USER_AGENT:
                await self.page.set_extra_http_headers({
                    "User-Agent": settings.BROWSER_USER_AGENT
                })

    async def login(self):
        """Führt den Login bei LinkedIn durch"""
        try:
            await self.init()
            if not self.is_logged_in:
                await self.page.goto("https://www.linkedin.com/login")
                await self.page.fill('input[id="username"]', settings.LINKEDIN_EMAIL)
                await self.page.fill('input[id="password"]', settings.LINKEDIN_PASSWORD)
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_load_state("networkidle")
                self.is_logged_in = True
                logger.info("LinkedIn Login erfolgreich")
        except Exception as e:
            logger.error(f"Fehler beim LinkedIn-Login: {str(e)}")
            raise

    async def create_draft_post(self, title: str, content: str, hashtags: List[str]) -> bool:
        """Erstellt einen Draft-Post auf LinkedIn"""
        try:
            await self.login()
            # Gehe zur LinkedIn Startseite
            await self.page.goto("https://www.linkedin.com/feed/")
            # Klicke auf "Post erstellen"
            await self.page.click('button[aria-label="Post erstellen"]')
            # Warte auf den Editor
            await self.page.wait_for_selector('div[aria-label="Editor für Textbeiträge"]')
            # Füge den Content ein
            full_content = f"{title}\n\n{content}\n\n{' '.join(hashtags)}"
            await self.page.fill('div[aria-label="Editor für Textbeiträge"]', full_content)
            # Klicke auf "Als Entwurf speichern"
            await self.page.click('button:has-text("Als Entwurf speichern")')
            await self.page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Draft-Posts: {str(e)}")
            return False

    async def interact_with_post(self, post_url: str, action: str, comment_text: Optional[str] = None) -> bool:
        """Interagiert mit einem Post (Like oder Kommentar)"""
        try:
            await self.login()
            await self.page.goto(post_url)
            await self.page.wait_for_load_state("networkidle")
            
            if action == "like":
                like_button = await self.page.query_selector('button[aria-label="Gefällt mir"]')
                if like_button:
                    await like_button.click()
            elif action == "comment" and comment_text:
                # Öffne Kommentarbereich
                await self.page.click('button[aria-label="Kommentar hinzufügen"]')
                # Warte auf den Kommentar-Editor
                await self.page.wait_for_selector('div[aria-label="Editor für Kommentare"]')
                # Füge den Kommentar ein
                await self.page.fill('div[aria-label="Editor für Kommentare"]', comment_text)
                # Sende den Kommentar
                await self.page.click('button[aria-label="Kommentar posten"]')
            
            await self.page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            logger.error(f"Fehler bei der Post-Interaktion: {str(e)}")
            return False

    async def connect_with_profile(self, profile_url: str, message: Optional[str] = None) -> bool:
        """Sendet eine Vernetzungsanfrage an ein Profil"""
        try:
            await self.login()
            await self.page.goto(profile_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Finde den "Vernetzen" Button
            connect_button = await self.page.query_selector('button:has-text("Vernetzen")')
            if connect_button:
                await connect_button.click()
                
                if message:
                    # Warte auf "Notiz hinzufügen" Button
                    add_note_button = await self.page.wait_for_selector('button:has-text("Notiz hinzufügen")')
                    await add_note_button.click()
                    
                    # Fülle die Nachricht aus
                    await self.page.fill('textarea[name="message"]', message)
                
                # Sende die Anfrage
                await self.page.click('button:has-text("Senden")')
                await self.page.wait_for_load_state("networkidle")
                return True
            return False
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit Profil: {str(e)}")
            return False

    async def search_posts_by_hashtag(self, hashtag: str, limit: int = 10) -> List[dict]:
        """Sucht nach Posts mit einem bestimmten Hashtag"""
        try:
            await self.login()
            await self.page.goto(f"https://www.linkedin.com/search/results/content/?keywords=%23{hashtag}")
            await self.page.wait_for_load_state("networkidle")
            
            posts = []
            post_elements = await self.page.query_selector_all("div.feed-shared-update-v2")
            
            for i, post in enumerate(post_elements):
                if i >= limit:
                    break
                    
                try:
                    # Extrahiere Post-URL
                    post_link = await post.query_selector("a.app-aware-link")
                    post_url = await post_link.get_attribute("href") if post_link else None
                    
                    # Extrahiere Post-Text
                    post_text = await post.query_selector("span.break-words")
                    text = await post_text.inner_text() if post_text else ""
                    
                    if post_url:
                        posts.append({
                            "url": post_url,
                            "text": text
                        })
                except Exception as e:
                    logger.warning(f"Fehler beim Extrahieren eines Posts: {str(e)}")
                    continue
            
            return posts
        except Exception as e:
            logger.error(f"Fehler bei der Hashtag-Suche: {str(e)}")
            return []

    async def close(self):
        """Schließt den Browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            self.is_logged_in = False 