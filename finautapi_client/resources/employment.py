"""Employment resource for FinAut API client."""

from typing import Dict, Any, Optional


class EmploymentResource:
    """Handle employment record-related API operations."""

    def __init__(self, client):
        """Initialize employment resource with API client."""
        self.client = client
        self.endpoint = "employment"

    def get(self, employment_id: int) -> Dict[str, Any]:
        """
        Get a specific employment record by ID.

        Args:
            employment_id: Employment record ID

        Returns:
            Employment details dictionary
        """
        return self.client.get(f"{self.endpoint}/{employment_id}/")