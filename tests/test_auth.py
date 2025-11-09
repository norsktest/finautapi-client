"""Tests for the OAuth2 authentication handler."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import responses

from finautapi_client.auth import OAuth2Handler, BasicAuthHandler
from finautapi_client.exceptions import AuthenticationError


class TestOAuth2Handler:
    """Test OAuth2 authentication handler."""

    def test_handler_initialization(self):
        """Test OAuth2 handler initialization."""
        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        assert handler.client_id == 'test_id'
        assert handler.client_secret == 'test_secret'
        assert handler.token_url == 'https://api.example.com/token'
        assert handler._access_token is None
        assert handler._token_expires is None
        assert handler._refresh_buffer == 60

    @responses.activate
    def test_token_refresh(self):
        """Test token refresh functionality."""
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={
                'access_token': 'new_token_456',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': 'read write'
            },
            status=200
        )

        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        # First access should trigger refresh
        token = handler.access_token

        assert token == 'new_token_456'
        assert handler._access_token == 'new_token_456'
        assert handler._token_expires is not None

        # Check that token expires in roughly 1 hour
        expected_expiry = datetime.now() + timedelta(seconds=3600)
        actual_expiry = handler._token_expires
        # Allow 1 second difference for test execution time
        assert abs((expected_expiry - actual_expiry).total_seconds()) < 1

    @responses.activate
    def test_token_reuse_when_valid(self):
        """Test that valid tokens are reused without refresh."""
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={
                'access_token': 'token_789',
                'expires_in': 3600
            },
            status=200
        )

        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        # First access
        token1 = handler.access_token
        # Second access (should reuse)
        token2 = handler.access_token

        assert token1 == token2 == 'token_789'
        # Should only make one request
        assert len(responses.calls) == 1

    @responses.activate
    def test_token_refresh_on_expiry(self):
        """Test token refresh when expired."""
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={'access_token': 'first_token', 'expires_in': 3600},
            status=200
        )
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={'access_token': 'second_token', 'expires_in': 3600},
            status=200
        )

        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        # Get first token
        token1 = handler.access_token
        assert token1 == 'first_token'

        # Manually expire the token
        handler._token_expires = datetime.now() - timedelta(seconds=1)

        # Should trigger refresh
        token2 = handler.access_token
        assert token2 == 'second_token'
        assert len(responses.calls) == 2

    @responses.activate
    def test_authentication_error_on_401(self):
        """Test authentication error handling."""
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={'error': 'invalid_client'},
            status=401
        )

        handler = OAuth2Handler(
            client_id='invalid_id',
            client_secret='invalid_secret',
            token_url='https://api.example.com/token'
        )

        with pytest.raises(AuthenticationError) as exc:
            _ = handler.access_token

        assert 'Failed to obtain access token' in str(exc.value)

    @responses.activate
    def test_authentication_error_on_invalid_response(self):
        """Test error handling for invalid token response."""
        responses.add(
            responses.POST,
            'https://api.example.com/token',
            json={'invalid': 'response'},  # Missing access_token
            status=200
        )

        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        with pytest.raises(AuthenticationError) as exc:
            _ = handler.access_token

        assert 'Invalid token response' in str(exc.value)

    def test_get_headers(self):
        """Test authorization header generation."""
        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        # Manually set token for testing
        handler._access_token = 'test_token_123'
        handler._token_expires = datetime.now() + timedelta(hours=1)

        headers = handler.get_headers()

        assert headers == {'Authorization': 'Bearer test_token_123'}

    def test_invalidate_token(self):
        """Test token invalidation."""
        handler = OAuth2Handler(
            client_id='test_id',
            client_secret='test_secret',
            token_url='https://api.example.com/token'
        )

        # Set a token
        handler._access_token = 'old_token'
        handler._token_expires = datetime.now() + timedelta(hours=1)

        # Invalidate
        handler.invalidate_token()

        assert handler._access_token is None
        assert handler._token_expires is None
        assert handler._needs_refresh() is True


class TestBasicAuthHandler:
    """Test basic authentication handler."""

    def test_basic_auth_initialization(self):
        """Test basic auth handler initialization."""
        handler = BasicAuthHandler(
            username='test_user',
            password='test_pass'
        )

        assert handler.username == 'test_user'
        assert handler.password == 'test_pass'

    def test_basic_auth_headers(self):
        """Test basic auth header generation."""
        handler = BasicAuthHandler(
            username='test_user',
            password='test_pass'
        )

        headers = handler.get_headers()

        # Basic auth should be base64 encoded
        import base64
        expected = base64.b64encode(b'test_user:test_pass').decode()

        assert headers == {'Authorization': f'Basic {expected}'}