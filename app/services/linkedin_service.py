from typing import Optional, List, Dict
import json
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
import asyncio
import random
import logging
import aiohttp
from urllib.parse import urlencode
from app.core.config import settings
from app.models.post import Post, PostStatus
from app.models.interaction import Interaction, InteractionType
from app.models.target_contact import TargetContact, ContactStatus
from app.core.exceptions import LinkedInAuthError, LinkedInConnectionError, LinkedInAPIError, LinkedInRateLimitError
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInService:
    """LinkedIn Service für die Authentifizierung und API-Interaktionen"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self._auth_state: Dict = {}

    async def initialize(self):
        """Initialisiert den Browser und die OAuth2-Authentifizierung"""
        try:
            # Browser initialisieren
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS,
                proxy={
                    'server': settings.PROXY_URL
                } if settings.PROXY_ENABLED and settings.PROXY_URL else None
            )
            self.page = await self.browser.new_page()
            
            # User-Agent setzen
            if settings.BROWSER_USER_AGENT:
                await self.page.set_extra_http_headers({
                    "User-Agent": settings.BROWSER_USER_AGENT
                })
            
            logger.info("Browser erfolgreich initialisiert")
            
            # OAuth2-Authentifizierung durchführen
            if settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET:
                await self._oauth2_authenticate()
            else:
                await self._cookie_authenticate()
                
        except Exception as e:
            logger.error(f"Fehler bei der Initialisierung: {str(e)}")
            raise LinkedInConnectionError("Initialisierung fehlgeschlagen") from e

    async def _oauth2_authenticate(self):
        """Führt die OAuth2-Authentifizierung durch"""
        try:
            # OAuth2-Parameter
            auth_params = {
                'response_type': 'code',
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
                'state': self._generate_state(),
                'scope': 'r_liteprofile w_member_social r_emailaddress w_member_social'
            }
            
            # Authorization URL konstruieren
            auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
            
            # Zur Authentifizierungsseite navigieren
            await self.page.goto(auth_url)
            
            try:
                # Auf Anmeldeformular warten und ausfüllen
                await self.page.wait_for_selector('#username', timeout=10000)
                await self.page.fill('#username', settings.LINKEDIN_EMAIL)
                await self.page.fill('#password', settings.LINKEDIN_PASSWORD)
                await self.page.click('button[type="submit"]')
                
                # Auf OAuth-Zustimmungsseite warten und bestätigen
                await self.page.wait_for_selector('button[aria-label="Allow"]', timeout=10000)
                await self.page.click('button[aria-label="Allow"]')
                
                # Auf Redirect mit Code warten
                response = await self.page.wait_for_response(
                    lambda resp: settings.LINKEDIN_REDIRECT_URI in resp.url,
                    timeout=20000
                )
                
                # Authorization Code extrahieren
                redirect_url = response.url
                auth_code = self._extract_auth_code(redirect_url)
                
                # Access Token anfordern
                await self._exchange_code_for_token(auth_code)
                
                self.is_logged_in = True
                logger.info("OAuth2-Authentifizierung erfolgreich")
                
            except PlaywrightTimeoutError:
                raise LinkedInAuthError("Timeout bei der OAuth2-Authentifizierung")
                
        except Exception as e:
            logger.error(f"OAuth2-Authentifizierung fehlgeschlagen: {str(e)}")
            raise LinkedInAuthError("OAuth2-Authentifizierung fehlgeschlagen") from e

    async def _cookie_authenticate(self):
        """Führt die Cookie-basierte Authentifizierung durch"""
        try:
            await self.page.goto("https://www.linkedin.com/login")
            await self.page.fill('#username', settings.LINKEDIN_EMAIL)
            await self.page.fill('#password', settings.LINKEDIN_PASSWORD)
            await self.page.click('button[type="submit"]')
            
            # Auf erfolgreiche Anmeldung warten
            await self.page.wait_for_selector('.feed-identity-module', timeout=10000)
            
            self.is_logged_in = True
            logger.info("Cookie-Authentifizierung erfolgreich")
            
        except Exception as e:
            logger.error(f"Cookie-Authentifizierung fehlgeschlagen: {str(e)}")
            raise LinkedInAuthError("Cookie-Authentifizierung fehlgeschlagen") from e

    async def _exchange_code_for_token(self, auth_code: str):
        """Tauscht den Authorization Code gegen Access und Refresh Tokens"""
        token_params = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                data=token_params
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data.get('refresh_token')
                    logger.info("Access Token erfolgreich erhalten")
                else:
                    raise LinkedInAuthError(f"Token-Austausch fehlgeschlagen: {await response.text()}")

    async def refresh_access_token(self):
        """Erneuert den Access Token mit dem Refresh Token"""
        if not self.refresh_token:
            raise LinkedInAuthError("Kein Refresh Token verfügbar")
            
        refresh_params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                data=refresh_params
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data.get('refresh_token', self.refresh_token)
                    logger.info("Access Token erfolgreich erneuert")
                else:
                    raise LinkedInAuthError(f"Token-Erneuerung fehlgeschlagen: {await response.text()}")

    def _generate_state(self) -> str:
        """Generiert einen zufälligen State-Parameter für OAuth2"""
        import secrets
        state = secrets.token_urlsafe(32)
        self._auth_state['state'] = state
        return state

    def _extract_auth_code(self, redirect_url: str) -> str:
        """Extrahiert den Authorization Code aus der Redirect URL"""
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        
        # State überprüfen
        if 'state' in params and params['state'][0] != self._auth_state.get('state'):
            raise LinkedInAuthError("Ungültiger State-Parameter")
            
        if 'code' not in params:
            raise LinkedInAuthError("Kein Authorization Code in der Redirect URL gefunden")
            
        return params['code'][0]

    async def check_connection(self) -> bool:
        """Überprüft die Verbindung zu LinkedIn"""
        try:
            if not self.is_logged_in:
                await self.initialize()
            
            # API-Endpunkt für Profilabfrage
            profile_url = f"{settings.LINKEDIN_API_URL}/me"
            headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(profile_url, headers=headers) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        # Token erneuern und erneut versuchen
                        await self.refresh_access_token()
                        async with session.get(profile_url, headers={"Authorization": f"Bearer {self.access_token}"}) as retry:
                            return retry.status == 200
                    else:
                        return False
                        
        except Exception as e:
            logger.error(f"Verbindungsprüfung fehlgeschlagen: {str(e)}")
            return False

    async def create_draft_post(self, title: str, content: str, hashtags: List[str]) -> bool:
        """Erstellt einen Draft-Post auf LinkedIn"""
        try:
            await self.initialize()
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
            await self.initialize()
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
            await self.initialize()
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
            await self.initialize()
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
        """Schließt den Browser und beendet die Session"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
                self.is_logged_in = False
                logger.info("Browser erfolgreich geschlossen")
        except Exception as e:
            logger.error(f"Fehler beim Schließen des Browsers: {str(e)}")
            raise LinkedInConnectionError("Browser konnte nicht geschlossen werden") from e

    async def publish_post(self, content: str, title: str = "", hashtags: List[str] = None, image_path: Optional[str] = None) -> bool:
        """Veröffentlicht einen Post direkt auf LinkedIn."""
        if not self.is_logged_in:
            logger.error("Nicht bei LinkedIn angemeldet")
            return False
        
        try:
            # Zur Post-Erstellungsseite navigieren
            await self.page.goto("https://www.linkedin.com/feed/")
            await self.page.click('button[aria-label="Post erstellen"]')
            
            # Warten auf den Editor
            editor = await self.page.wait_for_selector('div[aria-label="Editor für Textbeiträge"]')
            
            # Post-Inhalt zusammenstellen
            full_content = f"{title}\n\n{content}"
            if hashtags:
                hashtag_text = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
                full_content += f"\n\n{hashtag_text}"
            
            # Text eingeben
            await editor.fill(full_content)
            
            # Bild hinzufügen, falls vorhanden
            if image_path:
                await self.page.click('button[aria-label="Medien hinzufügen"]')
                file_input = await self.page.wait_for_selector('input[type="file"]')
                await file_input.set_input_files(image_path)
                await self.page.wait_for_selector('.share-box-footer__main-actions')
            
            # Post veröffentlichen
            await self.page.click('button:has-text("Posten")')
            
            # Warten auf Bestätigung
            try:
                await self.page.wait_for_selector('.artdeco-toast-item__message', timeout=10000)
                logger.info("Post erfolgreich veröffentlicht")
                return True
            except TimeoutError:
                logger.error("Timeout beim Warten auf Veröffentlichungsbestätigung")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Veröffentlichen des Posts: {str(e)}")
            return False

    async def login(self):
        """Meldet sich bei LinkedIn an."""
        try:
            # Hole Credentials aus Umgebungsvariablen
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            client_id = os.getenv('LINKEDIN_CLIENT_ID')
            client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')

            if not all([email, password, client_id, client_secret]):
                raise LinkedInAuthError("LinkedIn-Credentials fehlen in der .env-Datei")

            # Navigiere zur Login-Seite
            await self.page.goto("https://www.linkedin.com/login")
            
            # Warte auf Login-Formular
            await self.page.wait_for_selector("#username")
            
            # Fülle Anmeldedaten ein
            await self.page.fill("#username", email)
            await self.page.fill("#password", password)
            
            # Klicke auf Anmelden
            await self.page.click("button[type='submit']")
            
            # Warte auf erfolgreiche Anmeldung
            try:
                await self.page.wait_for_selector(".feed-identity-module", timeout=10000)
                self.is_logged_in = True
                logger.info("Erfolgreich bei LinkedIn angemeldet")
            except TimeoutError:
                raise LinkedInAuthError("Login-Timeout: Konnte Feed nicht laden")
                
        except Exception as e:
            logger.error(f"Fehler beim LinkedIn-Login: {str(e)}")
            self.is_logged_in = False
            raise LinkedInAuthError(f"Login fehlgeschlagen: {str(e)}") 