"""Department resource for FinAut API client."""

from typing import Dict, Any, List, Optional


class DepartmentResource:
    """Handle department-related API operations."""

    def __init__(self, client):
        """Initialize department resource with API client."""
        self.client = client
        self.endpoint = "departments"

    def list(self, page: Optional[int] = None) -> Dict[str, Any]:
        """
        List all accessible departments.

        Args:
            page: Page number for pagination

        Returns:
            Dictionary containing department list and pagination info
        """
        params = {'page': page} if page else {}
        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, department_id: int) -> Dict[str, Any]:
        """
        Get a specific department by ID.

        Args:
            department_id: Department ID

        Returns:
            Department details dictionary
        """
        return self.client.get(f"{self.endpoint}/{department_id}/")

    def get_franchises(self, department_id: int) -> List[str]:
        """
        Get list of franchise URLs for a department.

        Args:
            department_id: Department ID

        Returns:
            List of franchise URLs
        """
        department = self.get(department_id)
        return department.get('franchises', [])