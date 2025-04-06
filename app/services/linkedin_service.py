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

logger = logging.getLogger(__name__)

class LinkedInService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False

    async def initialize(self):
        """Initialisiert den Browser und meldet sich bei LinkedIn an."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self.login()

    async def login(self):
        """Meldet sich bei LinkedIn an."""
        try:
            await self.page.goto("https://www.linkedin.com/login")
            await self.page.fill("#username", settings.LINKEDIN_EMAIL)
            await self.page.fill("#password", settings.LINKEDIN_PASSWORD)
            await self.page.click("button[type='submit']")
            await self.page.wait_for_selector(".feed-identity-module", timeout=10000)
            self.is_logged_in = True
            logger.info("Erfolgreich bei LinkedIn angemeldet")
        except Exception as e:
            logger.error(f"Fehler beim LinkedIn-Login: {str(e)}")
            raise

    async def create_draft_post(self, post: Post) -> bool:
        """Erstellt einen LinkedIn-Post als Entwurf."""
        try:
            await self.page.goto("https://www.linkedin.com/post/new/")
            await self.page.wait_for_selector(".ql-editor")
            
            # Text eingeben
            await self.page.fill(".ql-editor", post.content)
            
            # Hashtags hinzufügen
            if post.hashtags:
                hashtags = post.hashtags.split()
                for hashtag in hashtags:
                    await self.page.fill(".ql-editor", f" {hashtag}")
            
            # Als Entwurf speichern
            await self.page.click("button[aria-label='Als Entwurf speichern']")
            await self.page.wait_for_selector(".feed-shared-update-v2", timeout=5000)
            
            # Post-ID extrahieren
            post_url = await self.page.url()
            post.linkedin_post_id = post_url.split("/")[-1]
            post.status = PostStatus.DRAFT
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Entwurfs: {str(e)}")
            post.status = PostStatus.FAILED
            return False

    async def like_post(self, post_url: str) -> bool:
        """Liked einen LinkedIn-Post."""
        try:
            await self.page.goto(post_url)
            await self.page.wait_for_selector("button[aria-label='Like']")
            await self.page.click("button[aria-label='Like']")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Liken des Posts: {str(e)}")
            return False

    async def comment_on_post(self, post_url: str, comment: str) -> bool:
        """Kommentiert einen LinkedIn-Post."""
        try:
            await this.page.goto(post_url)
            await this.page.wait_for_selector(".comments-comment-texteditor")
            await this.page.fill(".comments-comment-texteditor", comment)
            await this.page.click("button[aria-label='Post']")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Kommentieren des Posts: {str(e)}")
            return False

    async def send_connection_request(self, profile_url: str) -> bool:
        """Sendet eine Verbindungsanfrage an ein Profil."""
        try:
            await this.page.goto(profile_url)
            await this.page.wait_for_selector("button[aria-label='Connect']")
            await this.page.click("button[aria-label='Connect']")
            
            # Zufällige Verzögerung zwischen 2-5 Sekunden
            await asyncio.sleep(random.uniform(2, 5))
            
            # "Send" Button klicken
            await this.page.click("button[aria-label='Send now']")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der Verbindungsanfrage: {str(e)}")
            return False

    async def follow_profile(self, profile_url: str) -> bool:
        """Folgt einem LinkedIn-Profil."""
        try:
            await this.page.goto(profile_url)
            await this.page.wait_for_selector("button[aria-label='Follow']")
            await this.page.click("button[aria-label='Follow']")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Folgen des Profils: {str(e)}")
            return False

    async def search_target_contacts(self, keywords: List[str], industry: Optional[str] = None) -> List[Dict]:
        """Sucht nach potenziellen Zielkontakten basierend auf Keywords."""
        try:
            search_url = "https://www.linkedin.com/search/results/people/?"
            params = {
                "keywords": " ".join(keywords),
                "origin": "GLOBAL_SEARCH_HEADER"
            }
            if industry:
                params["industry"] = industry
                
            await this.page.goto(search_url + "&".join(f"{k}={v}" for k, v in params.items()))
            await this.page.wait_for_selector(".search-results-container")
            
            # Extrahiere Profilinformationen
            profiles = []
            for profile in await this.page.query_selector_all(".entity-result__item"):
                name = await profile.query_selector(".entity-result__title-text")
                title = await profile.query_selector(".entity-result__primary-subtitle")
                company = await profile.query_selector(".entity-result__secondary-subtitle")
                
                profiles.append({
                    "name": await name.inner_text() if name else "",
                    "title": await title.inner_text() if title else "",
                    "company": await company.inner_text() if company else "",
                    "profile_url": await profile.get_attribute("href")
                })
            
            return profiles
        except Exception as e:
            logger.error(f"Fehler bei der Kontaktsuche: {str(e)}")
            return []

    async def close(self):
        """Schließt den Browser und beendet die Session."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            self.is_logged_in = False 