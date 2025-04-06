from typing import Optional, List, Dict
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.core.config import settings
from app.models.post import Post
from app.models.interaction import Interaction, InteractionType, InteractionStatus

class LinkedInService:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.setup_browser()

    def setup_browser(self):
        """Browser mit den konfigurierten Einstellungen einrichten"""
        options = webdriver.ChromeOptions()
        if settings.BROWSER_HEADLESS:
            options.add_argument("--headless")
        if settings.BROWSER_USER_AGENT:
            options.add_argument(f"user-agent={settings.BROWSER_USER_AGENT}")
        if settings.PROXY_ENABLED and settings.PROXY_URL:
            options.add_argument(f'--proxy-server={settings.PROXY_URL}')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def login(self, email: str, password: str) -> bool:
        """Bei LinkedIn anmelden"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # E-Mail eingeben
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            # Passwort eingeben
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Anmelden klicken
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Warten auf erfolgreiche Anmeldung
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module"))
            )
            
            self.is_logged_in = True
            return True
        except Exception as e:
            print(f"Login fehlgeschlagen: {str(e)}")
            return False

    def create_post(self, post: Post) -> bool:
        """Einen neuen LinkedIn-Beitrag erstellen"""
        if not self.is_logged_in:
            return False
        
        try:
            # Zum Beitrag-Erstellungsbereich navigieren
            self.driver.get("https://www.linkedin.com/post/new/")
            
            # Beitragsinhalt eingeben
            content_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor"))
            )
            content_field.send_keys(post.content)
            
            # Hashtags hinzufügen
            if post.hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in post.hashtags])
                content_field.send_keys(f"\n\n{hashtag_text}")
            
            # Beitrag veröffentlichen
            post_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            post_button.click()
            
            # Warten auf erfolgreiche Veröffentlichung
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".post-success-message"))
            )
            
            return True
        except Exception as e:
            print(f"Beitragserstellung fehlgeschlagen: {str(e)}")
            return False

    def like_post(self, post_url: str) -> bool:
        """Einen Beitrag liken"""
        if not self.is_logged_in:
            return False
        
        try:
            self.driver.get(post_url)
            
            # Like-Button finden und klicken
            like_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.react-button__trigger"))
            )
            like_button.click()
            
            return True
        except Exception as e:
            print(f"Like fehlgeschlagen: {str(e)}")
            return False

    def comment_on_post(self, post_url: str, comment: str) -> bool:
        """Einen Kommentar zu einem Beitrag hinzufügen"""
        if not self.is_logged_in:
            return False
        
        try:
            self.driver.get(post_url)
            
            # Kommentarfeld finden und ausfüllen
            comment_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".comments-comment-texteditor"))
            )
            comment_field.send_keys(comment)
            
            # Kommentar veröffentlichen
            post_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            post_button.click()
            
            return True
        except Exception as e:
            print(f"Kommentar fehlgeschlagen: {str(e)}")
            return False

    def send_connection_request(self, profile_url: str, message: Optional[str] = None) -> bool:
        """Eine Verbindungsanfrage senden"""
        if not self.is_logged_in:
            return False
        
        try:
            self.driver.get(profile_url)
            
            # Verbinden-Button finden und klicken
            connect_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Verbinden']"))
            )
            connect_button.click()
            
            # Optional: Personalisierte Nachricht hinzufügen
            if message:
                add_note_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Notiz hinzufügen']"))
                )
                add_note_button.click()
                
                message_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "custom-message"))
                )
                message_field.send_keys(message)
            
            # Anfrage senden
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Senden']")
            send_button.click()
            
            return True
        except Exception as e:
            print(f"Verbindungsanfrage fehlgeschlagen: {str(e)}")
            return False

    def search_profiles(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Nach Profilen suchen"""
        if not self.is_logged_in:
            return []
        
        try:
            # Suchanfrage konstruieren
            search_query = " ".join(keywords)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            
            # Filter hinzufügen
            if "industry" in filters:
                search_url += f"&industry={filters['industry']}"
            if "location" in filters:
                search_url += f"&location={filters['location']}"
            
            self.driver.get(search_url)
            
            # Profile extrahieren
            profiles = []
            profile_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-result__info"))
            )
            
            for element in profile_elements:
                try:
                    name = element.find_element(By.CSS_SELECTOR, ".actor-name").text
                    title = element.find_element(By.CSS_SELECTOR, ".subline-level-1").text
                    profile_url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    profiles.append({
                        "name": name,
                        "title": title,
                        "url": profile_url
                    })
                except NoSuchElementException:
                    continue
            
            return profiles
        except Exception as e:
            print(f"Profilsuche fehlgeschlagen: {str(e)}")
            return []

    def close(self):
        """Browser schließen"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False 