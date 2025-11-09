"""Result resource for FinAut API client."""

from typing import Dict, Any, List, Optional
from datetime import date


class ResultResource:
    """Handle exam/assessment result-related API operations."""

    def __init__(self, client):
        """Initialize result resource with API client."""
        self.client = client
        self.endpoint = "results"

    def list(
        self,
        from_date: Optional[str] = None,
        persnr: Optional[str] = None,
        employee_alias: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List results with optional filters.

        Args:
            from_date: Filter results from this date (YYYY-MM-DD)
            persnr: Norwegian social security number
            employee_alias: Employee alias
            page: Page number for pagination

        Returns:
            Dictionary containing result list and pagination info
        """
        params = {}
        if from_date:
            params['from_date'] = from_date
        if persnr:
            params['persnr'] = persnr
        if employee_alias:
            params['employee_alias'] = employee_alias
        if page:
            params['page'] = page

        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, result_id: int) -> Dict[str, Any]:
        """
        Get a specific result by ID.

        Args:
            result_id: Result ID

        Returns:
            Result details dictionary
        """
        return self.client.get(f"{self.endpoint}/{result_id}/")

    def get_user_results(
        self,
        user_id: Optional[int] = None,
        persnr: Optional[str] = None,
        employee_alias: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all results for a specific user.

        Args:
            user_id: User ID
            persnr: Norwegian SSN
            employee_alias: Employee alias

        Note: Provide at least one identifier.

        Returns:
            List of result dictionaries
        """
        if not any([user_id, persnr, employee_alias]):
            raise ValueError("Must provide at least one user identifier")

        # Get all results with filter
        all_results = []
        page = 1
        while True:
            response = self.list(
                persnr=persnr,
                employee_alias=employee_alias,
                page=page
            )
            results = response.get('results', [])

            # Filter by user_id if provided
            if user_id:
                user_url = f"{self.client.base_url}user/{user_id}/"
                results = [r for r in results if r.get('user') == user_url]

            all_results.extend(results)

            if not response.get('next'):
                break
            page += 1

        return all_results

    def get_recent_results(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get results from the last N days.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            List of recent result dictionaries
        """
        from datetime import datetime, timedelta

        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        all_results = []
        page = 1
        while True:
            response = self.list(from_date=from_date, page=page)
            results = response.get('results', [])
            all_results.extend(results)

            if not response.get('next'):
                break
            page += 1

        return all_results