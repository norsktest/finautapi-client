"""Competency result resource for FinAut API client."""

from typing import Dict, Any, List, Optional


class CompetencyResultResource:
    """Handle competency result-related API operations."""

    def __init__(self, client):
        """Initialize competency result resource with API client."""
        self.client = client
        self.endpoint = "competency_result"

    def list(
        self,
        encrypted_userid: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List competency results with optional filters.

        Args:
            encrypted_userid: Encrypted user ID from external system
            page: Page number for pagination

        Returns:
            Dictionary containing result list and pagination info
        """
        params = {}
        if encrypted_userid:
            params['encrypted_userid'] = encrypted_userid
        if page:
            params['page'] = page

        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, result_id: int) -> Dict[str, Any]:
        """
        Get a specific competency result by ID.

        Args:
            result_id: Result ID

        Returns:
            Competency result details dictionary
        """
        return self.client.get(f"{self.endpoint}/{result_id}/")

    def create(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new competency result.

        Args:
            result_data: Dictionary containing competency result information:
                - user: Encrypted user ID (required)
                - goal: Goal ID (required)
                - passed_date: Date when competency was achieved (YYYY-MM-DD)
                - external_system: Name of external system
                - external_id: ID in external system

        Returns:
            Created competency result details

        Example:
            result_data = {
                "user": "encrypted_user_id_123",
                "goal": 456,
                "passed_date": "2024-01-15",
                "external_system": "LMS",
                "external_id": "COURSE-789"
            }
        """
        return self.client.post(f"{self.endpoint}/", json=result_data)

    def record_completion(
        self,
        encrypted_userid: str,
        goal_id: int,
        passed_date: str,
        external_system: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a competency completion for a user.

        Args:
            encrypted_userid: Encrypted user ID from external system
            goal_id: Goal ID that was completed
            passed_date: Date of completion (YYYY-MM-DD)
            external_system: Name of external system (optional)
            external_id: ID in external system (optional)

        Returns:
            Created competency result details
        """
        result_data = {
            "user": encrypted_userid,
            "goal": goal_id,
            "passed_date": passed_date,
        }
        if external_system:
            result_data["external_system"] = external_system
        if external_id:
            result_data["external_id"] = external_id

        return self.create(result_data)