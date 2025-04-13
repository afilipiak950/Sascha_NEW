class LinkedInError(Exception):
    """Basisklasse für alle LinkedIn-bezogenen Fehler"""
    pass

class LinkedInAuthError(LinkedInError):
    """Fehler bei der LinkedIn-Authentifizierung"""
    pass

class LinkedInConnectionError(LinkedInError):
    """Fehler bei der Verbindung zu LinkedIn"""
    pass

class LinkedInAPIError(LinkedInError):
    """Fehler bei LinkedIn API-Aufrufen"""
    pass

class LinkedInRateLimitError(LinkedInError):
    """Fehler bei Überschreitung des LinkedIn API-Limits"""
    pass 