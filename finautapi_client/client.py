"""Main FinAut API client implementation."""

from typing import Optional, Dict, Any
from urllib.parse import urljoin
import requests
from .auth import OAuth2Handler
from .exceptions import (
    FinAutAPIException,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    RateLimitError,
)
from .resources import (
    UserResource,
    CompanyResource,
    DepartmentResource,
    UserStatusResource,
    ResultResource,
    CompetencyResultResource,
    EmploymentResource,
)


class FinAutAPIClient:
    """Main client for interacting with the FinAut API."""

    DEFAULT_TIMEOUT = 30
    DEFAULT_HOST = "https://api.norsktest.no"
    API_VERSION = "v1"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        host: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        """
        Initialize FinAut API client.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            host: API host URL (default: https://api.norsktest.no)
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Verify SSL certificates (default: True)
            debug: Enable debug mode (default: False)
        """
        self.host = (host or self.DEFAULT_HOST).rstrip('/')
        self.base_url = f"{self.host}/finautapi/{self.API_VERSION}/"
        self.token_url = f"{self.host}/o/token/"
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.debug = debug

        # Initialize OAuth2 handler
        self.auth = OAuth2Handler(client_id, client_secret, self.token_url)

        # Initialize resource handlers
        self.users = UserResource(self)
        self.companies = CompanyResource(self)
        self.departments = DepartmentResource(self)
        self.userstatus = UserStatusResource(self)
        self.results = ResultResource(self)
        self.competency_results = CompetencyResultResource(self)
        self.employment = EmploymentResource(self)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            json: JSON payload for request body
            data: Form data for request body
            headers: Additional headers
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            Various FinAutAPIException subclasses based on response status
        """
        # Build full URL
        url = urljoin(self.base_url, endpoint.lstrip('/'))

        # Prepare headers
        request_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json' if json else 'application/x-www-form-urlencoded',
        }
        request_headers.update(self.auth.get_headers())
        if headers:
            request_headers.update(headers)

        # Debug logging
        if self.debug:
            print(f"[DEBUG] {method} {url}")
            if params:
                print(f"[DEBUG] Params: {params}")
            if json:
                print(f"[DEBUG] JSON: {json}")

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )

            # Debug response
            if self.debug:
                print(f"[DEBUG] Response: {response.status_code}")
                print(f"[DEBUG] Body: {response.text[:500]}")

            # Handle errors
            self._handle_response_errors(response)

            return response

        except requests.exceptions.Timeout:
            raise FinAutAPIException("Request timed out")
        except requests.exceptions.ConnectionError as e:
            raise FinAutAPIException(f"Connection error: {str(e)}")

    def _handle_response_errors(self, response: requests.Response) -> None:
        """
        Handle HTTP error responses.

        Args:
            response: Response object to check

        Raises:
            Various FinAutAPIException subclasses based on status code
        """
        if response.status_code < 400:
            return

        # Try to get error message from response
        try:
            error_data = response.json()
            message = error_data.get('detail', error_data.get('message', str(error_data)))
        except:
            message = response.text or f"HTTP {response.status_code}"

        # Map status codes to exceptions
        if response.status_code == 401:
            # Token might be expired, try to invalidate it
            self.auth.invalidate_token()
            raise AuthenticationError(message, response, response.status_code)
        elif response.status_code == 403:
            raise PermissionDeniedError(message, response, response.status_code)
        elif response.status_code == 404:
            raise NotFoundError(message, response, response.status_code)
        elif response.status_code == 422:
            raise ValidationError(message, response, response.status_code)
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise RateLimitError(message, response, retry_after)
        elif response.status_code >= 500:
            raise ServerError(message, response, response.status_code)
        else:
            raise FinAutAPIException(message, response, response.status_code)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request and return JSON response."""
        response = self.request('GET', endpoint, params=params, **kwargs)
        return response.json()

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request and return JSON response."""
        response = self.request('POST', endpoint, json=json, **kwargs)
        return response.json() if response.text else {}

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request and return JSON response."""
        response = self.request('PUT', endpoint, json=json, **kwargs)
        return response.json() if response.text else {}

    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request and return JSON response."""
        response = self.request('PATCH', endpoint, json=json, **kwargs)
        return response.json() if response.text else {}

    def delete(self, endpoint: str, **kwargs) -> None:
        """Make a DELETE request."""
        self.request('DELETE', endpoint, **kwargs)

    def test_connection(self) -> bool:
        """
        Test connection to the API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get the API root
            self.get("")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Connection test failed: {e}")
            return False