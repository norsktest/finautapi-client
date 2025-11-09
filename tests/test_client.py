"""Tests for the FinAut API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import responses
import json

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    RateLimitError,
)


class TestFinAutAPIClient:
    """Test the main client class."""

    def test_client_initialization(self):
        """Test client initialization with required parameters."""
        client = FinAutAPIClient(
            client_id='test_id',
            client_secret='test_secret'
        )

        assert client.host == 'https://api.norsktest.no'
        assert client.base_url == 'https://api.norsktest.no/finautapi/v1/'
        assert client.token_url == 'https://api.norsktest.no/o/token/'
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client.debug is False

    def test_client_custom_host(self):
        """Test client with custom host."""
        client = FinAutAPIClient(
            client_id='test_id',
            client_secret='test_secret',
            host='https://test.example.com'
        )

        assert client.host == 'https://test.example.com'
        assert client.base_url == 'https://test.example.com/finautapi/v1/'

    @responses.activate
    def test_oauth2_token_request(self):
        """Test OAuth2 token acquisition."""
        # Mock token endpoint
        responses.add(
            responses.POST,
            'https://api.norsktest.no/o/token/',
            json={
                'access_token': 'test_token_123',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': 'read write'
            },
            status=200
        )

        # Mock API endpoint
        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/test',
            json={'result': 'success'},
            status=200
        )

        client = FinAutAPIClient(
            client_id='test_id',
            client_secret='test_secret'
        )

        # Make a request that triggers token acquisition
        response = client.get('test')

        assert response == {'result': 'success'}
        assert len(responses.calls) == 2

        # Check token request
        token_request = responses.calls[0]
        assert token_request.request.url == 'https://api.norsktest.no/o/token/'
        assert 'grant_type=client_credentials' in token_request.request.body

        # Check API request has auth header
        api_request = responses.calls[1]
        assert api_request.request.headers['Authorization'] == 'Bearer test_token_123'

    @responses.activate
    def test_authentication_error(self):
        """Test authentication error handling."""
        # Mock 401 response
        responses.add(
            responses.POST,
            'https://api.norsktest.no/o/token/',
            json={'error': 'invalid_client'},
            status=401
        )

        client = FinAutAPIClient(
            client_id='invalid_id',
            client_secret='invalid_secret'
        )

        with pytest.raises(AuthenticationError) as exc:
            client.get('test')

        assert 'Failed to obtain access token' in str(exc.value)

    @responses.activate
    def test_error_handling(self):
        """Test various error response handling."""
        # Setup token first
        responses.add(
            responses.POST,
            'https://api.norsktest.no/o/token/',
            json={'access_token': 'test_token', 'expires_in': 3600},
            status=200
        )

        client = FinAutAPIClient('test_id', 'test_secret')

        # Test 403 Forbidden
        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/forbidden',
            json={'detail': 'Permission denied'},
            status=403
        )

        with pytest.raises(PermissionDeniedError) as exc:
            client.get('forbidden')
        assert exc.value.status_code == 403

        # Test 404 Not Found
        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/notfound',
            json={'detail': 'Not found'},
            status=404
        )

        with pytest.raises(NotFoundError) as exc:
            client.get('notfound')
        assert exc.value.status_code == 404

        # Test 422 Validation Error
        responses.add(
            responses.POST,
            'https://api.norsktest.no/finautapi/v1/invalid',
            json={'detail': 'Validation failed'},
            status=422
        )

        with pytest.raises(ValidationError) as exc:
            client.post('invalid', json={'bad': 'data'})
        assert exc.value.status_code == 422

        # Test 429 Rate Limit
        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/limited',
            json={'detail': 'Rate limit exceeded'},
            headers={'Retry-After': '60'},
            status=429
        )

        with pytest.raises(RateLimitError) as exc:
            client.get('limited')
        assert exc.value.retry_after == '60'

        # Test 500 Server Error
        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/error',
            json={'detail': 'Internal server error'},
            status=500
        )

        with pytest.raises(ServerError) as exc:
            client.get('error')
        assert exc.value.status_code == 500

    def test_resource_initialization(self):
        """Test that all resources are properly initialized."""
        client = FinAutAPIClient('test_id', 'test_secret')

        assert client.users is not None
        assert client.companies is not None
        assert client.departments is not None
        assert client.userstatus is not None
        assert client.results is not None
        assert client.competency_results is not None
        assert client.employment is not None

    @responses.activate
    def test_debug_mode(self, capsys):
        """Test debug mode output."""
        responses.add(
            responses.POST,
            'https://api.norsktest.no/o/token/',
            json={'access_token': 'test_token', 'expires_in': 3600},
            status=200
        )

        responses.add(
            responses.GET,
            'https://api.norsktest.no/finautapi/v1/test',
            json={'result': 'success'},
            status=200
        )

        client = FinAutAPIClient(
            client_id='test_id',
            client_secret='test_secret',
            debug=True
        )

        client.get('test')

        captured = capsys.readouterr()
        assert '[DEBUG]' in captured.out
        assert 'GET' in captured.out
        assert 'Response: 200' in captured.out