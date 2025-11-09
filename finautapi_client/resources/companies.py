"""Company resource for FinAut API client."""

from typing import Dict, Any, List, Optional


class CompanyResource:
    """Handle company-related API operations."""

    def __init__(self, client):
        """Initialize company resource with API client."""
        self.client = client
        self.endpoint = "companies"

    def list(self, page: Optional[int] = None) -> Dict[str, Any]:
        """
        List all accessible companies.

        Args:
            page: Page number for pagination

        Returns:
            Dictionary containing company list and pagination info
        """
        params = {'page': page} if page else {}
        return self.client.get(f"{self.endpoint}/", params=params)

    def get(self, company_id: int) -> Dict[str, Any]:
        """
        Get a specific company by ID.

        Args:
            company_id: Company ID

        Returns:
            Company details dictionary
        """
        return self.client.get(f"{self.endpoint}/{company_id}/")

    def get_departments(self, company_id: int) -> List[str]:
        """
        Get list of department URLs for a company.

        Args:
            company_id: Company ID

        Returns:
            List of department URLs
        """
        company = self.get(company_id)
        return company.get('departments', [])