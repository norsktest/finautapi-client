"""User resource for FinAut API client."""

from typing import Dict, Any, List, Optional


class UserResource:
    """Handle user-related API operations."""

    def __init__(self, client):
        """Initialize user resource with API client."""
        self.client = client
        self.endpoint = "user"

    def list(
        self,
        persnr: Optional[str] = None,
        encoded_userid: Optional[str] = None,
        employee_alias: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List users with optional filters.

        Args:
            persnr: Norwegian social security number (fødselsnummer)
            encoded_userid: Encrypted user ID
            employee_alias: Employee alias/identifier
            page: Page number for pagination

        Returns:
            Dictionary containing user list and pagination info
        """
        params = {}
        if persnr:
            params['persnr'] = persnr
        if encoded_userid:
            params['encoded_userid'] = encoded_userid
        if employee_alias:
            params['employee_alias'] = employee_alias
        if page:
            params['page'] = page

        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, user_id: int) -> Dict[str, Any]:
        """
        Get a specific user by ID.

        Args:
            user_id: User ID

        Returns:
            User details dictionary
        """
        return self.client.get(f"{self.endpoint}/{user_id}/")

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user information:
                - persnr: Norwegian SSN (required)
                - first_name: First name (required)
                - last_name: Last name (required)
                - email: Email address
                - mobile: Mobile phone number
                - employee_alias: Employee identifier
                - work_for: Employment info (dict with department and company URLs)
                - userroles: List of user role URLs

        Returns:
            Created user details

        Example:
            user_data = {
                "persnr": "01234567890",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "mobile": "12345678",
                "employee_alias": "EMP001",
                "work_for": {
                    "department": "https://api.norsktest.no/finautapi/v1/departments/123/",
                    "company": "https://api.norsktest.no/finautapi/v1/companies/456/"
                },
                "userroles": [
                    "https://api.norsktest.no/finautapi/v1/userrole/afr_ka/"
                ]
            }
        """
        return self.client.post(f"{self.endpoint}/", json=user_data)

    def update(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing user (full update).

        Args:
            user_id: User ID
            user_data: Complete user data dictionary

        Returns:
            Updated user details
        """
        return self.client.put(f"{self.endpoint}/{user_id}/", json=user_data)

    def partial_update(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partially update an existing user.

        Args:
            user_id: User ID
            user_data: Partial user data to update

        Returns:
            Updated user details
        """
        return self.client.patch(f"{self.endpoint}/{user_id}/", json=user_data)

    def search_by_persnr(self, persnr: str) -> Optional[Dict[str, Any]]:
        """
        Search for a user by Norwegian SSN.

        Args:
            persnr: Norwegian social security number

        Returns:
            User details if found, None otherwise
        """
        result = self.list(persnr=persnr)
        if result.get('results'):
            return result['results'][0]
        return None

    def search_by_employee_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """
        Search for a user by employee alias.

        Args:
            alias: Employee alias

        Returns:
            User details if found, None otherwise
        """
        result = self.list(employee_alias=alias)
        if result.get('results'):
            return result['results'][0]
        return None