"""OAuth2 authentication handler for FinAut API."""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import requests
from .exceptions import AuthenticationError


class OAuth2Handler:
    """Handles OAuth2 Client Credentials flow for FinAut API."""

    def __init__(self, client_id: str, client_secret: str, token_url: str):
        """
        Initialize OAuth2 handler.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: URL to obtain access tokens
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._refresh_buffer = 60  # Refresh token 60 seconds before expiry

    @property
    def access_token(self) -> str:
        """
        Get current access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If token refresh fails
        """
        if self._needs_refresh():
            self._refresh_token()
        return self._access_token

    def _needs_refresh(self) -> bool:
        """Check if token needs to be refreshed."""
        if not self._access_token or not self._token_expires:
            return True

        buffer_time = timedelta(seconds=self._refresh_buffer)
        return datetime.now() >= (self._token_expires - buffer_time)

    def _refresh_token(self) -> None:
        """
        Refresh the access token using client credentials.

        Raises:
            AuthenticationError: If token refresh fails
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'read write'
        }

        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data['access_token']

            # Calculate token expiry time
            expires_in = token_data.get('expires_in', 3600)
            self._token_expires = datetime.now() + timedelta(seconds=expires_in)

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(
                f"Failed to obtain access token: {str(e)}",
                response=getattr(e, 'response', None)
            )
        except (KeyError, ValueError) as e:
            raise AuthenticationError(
                f"Invalid token response: {str(e)}",
                response=response
            )

    def get_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests.

        Returns:
            Dictionary with Authorization header
        """
        return {
            'Authorization': f'Bearer {self.access_token}'
        }

    def invalidate_token(self) -> None:
        """Invalidate the current token, forcing a refresh on next use."""
        self._access_token = None
        self._token_expires = None


class BasicAuthHandler:
    """Basic authentication handler for testing/development."""

    def __init__(self, username: str, password: str):
        """
        Initialize basic auth handler.

        Args:
            username: API username
            password: API password
        """
        self.username = username
        self.password = password

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        import base64
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            'Authorization': f'Basic {encoded}'
        }