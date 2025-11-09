"""User status resource for FinAut API client."""

from typing import Dict, Any, List, Optional
from datetime import date


class UserStatusResource:
    """Handle user status-related API operations."""

    def __init__(self, client):
        """Initialize user status resource with API client."""
        self.client = client
        self.endpoint = "userstatus"

    def list(
        self,
        persnr: Optional[str] = None,
        employee_alias: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List user statuses with optional filters.

        Args:
            persnr: Norwegian social security number
            employee_alias: Employee alias
            page: Page number for pagination

        Returns:
            Dictionary containing status list and pagination info
        """
        params = {}
        if persnr:
            params['persnr'] = persnr
        if employee_alias:
            params['employee_alias'] = employee_alias
        if page:
            params['page'] = page

        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, status_id: int) -> Dict[str, Any]:
        """
        Get a specific user status by ID.

        Args:
            status_id: Status ID

        Returns:
            Status details dictionary
        """
        return self.client.get(f"{self.endpoint}/{status_id}/")

    def create(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user status.

        Args:
            status_data: Dictionary containing status information:
                - appname: Authorization scheme code (required, max 10 chars, e.g., "afr", "krd")
                - user: User URL (required)
                - status: Status type (required) - only 'hvilende' or 'utmeldt' allowed
                - reason: Reason for status change (required)
                - status_date: Date of status change (YYYY-MM-DD)
                - status_set_by: User who set the status (required)
                - comment: Status comment (optional)

        Returns:
            Created status details

        Example:
            status_data = {
                "appname": "afr",  # Short code, NOT a URL
                "user": "https://api.norsktest.no/finautapi/v1/user/123/",
                "status": "hvilende",
                "reason": "hvilende",
                "status_set_by": "https://api.norsktest.no/finautapi/v1/user/1/",
                "status_date": "2024-01-01",
                "comment": "Temporary leave"
            }
        """
        return self.client.post(f"{self.endpoint}/", json=status_data)

    def set_inactive(
        self,
        user_id: int,
        appname: str,
        status_date: Optional[str] = None,
        comment: Optional[str] = None,
        status_set_by_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set a user's status to inactive (hvilende) in an authorization scheme.

        Note: The API only allows creating 'hvilende' or 'utmeldt' statuses.
        Setting to 'aktiv' is not supported through this endpoint.

        Args:
            user_id: User ID
            appname: Authorization scheme code (e.g., "afr", "krd", "gos")
            status_date: Date of status change (YYYY-MM-DD)
            comment: Optional comment
            status_set_by_id: ID of the user setting the status (defaults to user_id)

        Returns:
            Created status details
        """
        # Use status_set_by_id if provided, otherwise use the user_id
        set_by_id = status_set_by_id or user_id
        
        status_data = {
            "appname": appname,  # Short code like "afr", "krd", not a URL
            "user": f"{self.client.base_url}user/{user_id}/",
            "status": "hvilende",
            "reason": "hvilende",  # Required by API
            "status_set_by": f"{self.client.base_url}user/{set_by_id}/",
            "status_date": status_date or date.today().isoformat(),
        }
        if comment:
            status_data["comment"] = comment

        return self.create(status_data)

    def set_withdrawn(
        self,
        user_id: int,
        appname: str,
        status_date: Optional[str] = None,
        comment: Optional[str] = None,
        status_set_by_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set a user's status to withdrawn (utmeldt) from an authorization scheme.

        Args:
            user_id: User ID
            appname: Authorization scheme code (e.g., "afr", "krd", "gos")
            status_date: Date of status change (YYYY-MM-DD)
            comment: Optional comment
            status_set_by_id: ID of the user setting the status (defaults to user_id)

        Returns:
            Created status details
        """
        # Use status_set_by_id if provided, otherwise use the user_id
        set_by_id = status_set_by_id or user_id
        
        status_data = {
            "appname": appname,  # Short code like "afr", "krd", not a URL
            "user": f"{self.client.base_url}user/{user_id}/",
            "status": "utmeldt",
            "reason": "utmeldt",  # Required by API
            "status_set_by": f"{self.client.base_url}user/{set_by_id}/",
            "status_date": status_date or date.today().isoformat(),
        }
        if comment:
            status_data["comment"] = comment

        return self.create(status_data)

    def get_latest(self, persnr: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest user status.

        Args:
            persnr: Norwegian SSN to filter by

        Returns:
            Latest status details
        """
        endpoint = "latestuserstatus"
        params = {'persnr': persnr} if persnr else {}
        return self.client.get(f"{endpoint}/", params=params)