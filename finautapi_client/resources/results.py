"""Result resource for FinAut API client."""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta


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
        List monitored exam results for your users (one page).

        The API needs persnr or from_date; without either it returns an
        empty list. employee_alias only narrows a from_date query.

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
        persnr: Optional[str] = None,
        employee_alias: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all monitored exam results for one of your users.

        Args:
            persnr: Norwegian national identity number
            employee_alias: Your company's identifier for the user

        The API filters on persnr directly. It only honours employee_alias
        together with from_date, so that lookup asks for everything since
        2000-01-01.

        Returns:
            List of result dictionaries
        """
        if persnr:
            params = {'persnr': persnr}
        elif employee_alias:
            params = {'employee_alias': employee_alias, 'from_date': '2000-01-01'}
        else:
            raise ValueError("Give persnr or employee_alias")
        return self.client.get_all(f"{self.endpoint}/", params)

    def get_recent_results(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get monitored exam results finished in the last N days, for all
        your users.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            List of recent result dictionaries
        """
        from_date = (date.today() - timedelta(days=days)).isoformat()
        return self.client.get_all(f"{self.endpoint}/", {'from_date': from_date})
