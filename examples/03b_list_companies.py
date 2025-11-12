#!/usr/bin/env python
"""
Example: List Companies and Departments

This example demonstrates how to list companies and departments that
your API user has access to, and how to retrieve detailed information
about specific companies and their organizational structure.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import FinAutAPIException


def main():
    """Demonstrate listing companies and departments."""

    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - List Companies and Departments Example")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST,
        debug=True  # Enable debug output to see requests
    )

    try:
        # 1. List all accessible companies
        print("\n1. Listing all accessible companies...")
        companies = client.companies.list()

        print(f"   Total companies: {companies.get('count', 0)}")
        print(f"   Page size: {len(companies.get('results', []))}")

        # Display companies with details
        for company in companies.get('results', []):
            company_id = client.extract_id_from_url(company.get('id'))
            print(f"   - {company.get('navn')} (ID: {company_id})")
            print(f"     Organization #: {company.get('orgnr')}")
            if company.get('departments'):
                print(f"     Departments: {len(company.get('departments'))}")

        # 2. Get detailed information about a specific company
        if companies.get('results'):
            first_company = companies['results'][0]
            company_id = client.extract_id_from_url(first_company['id'])

            print(f"\n2. Getting detailed information for company {company_id}...")
            company_details = client.companies.get(company_id)

            print(f"   Company details:")
            print(f"     Name: {company_details.get('navn')}")
            print(f"     Organization #: {company_details.get('orgnr')}")
            print(f"     Website: {company_details.get('hjemmeside', 'N/A')}")
            print(f"     Departments: {len(company_details.get('departments', []))}")

            # 3. List departments for this company
            if company_details.get('departments'):
                print(f"\n3. Departments for {company_details.get('navn')}:")

                for dept_url in company_details['departments'][:5]:  # Show first 5
                    dept_id = client.extract_id_from_url(dept_url)
                    try:
                        dept = client.departments.get(dept_id)
                        print(f"   - {dept.get('departmentname')} (ID: {dept_id})")
                        if dept.get('franchises'):
                            print(f"     Franchises: {len(dept.get('franchises'))}")
                    except FinAutAPIException as e:
                        print(f"   - Department {dept_id} (unable to fetch details: {e})")

        # 4. List all accessible departments
        print("\n4. Listing all accessible departments...")
        departments = client.departments.list()

        print(f"   Total departments: {departments.get('count', 0)}")
        print(f"   Page size: {len(departments.get('results', []))}")

        # Display first few departments
        for dept in departments.get('results', [])[:5]:
            dept_id = client.extract_id_from_url(dept.get('id'))
            print(f"   - {dept.get('departmentname')} (ID: {dept_id})")
            print(f"     Company: {dept.get('company')}")
            if dept.get('franchises'):
                print(f"     Franchises: {len(dept.get('franchises'))}")

        # 5. Get detailed information about a specific department
        if departments.get('results'):
            first_dept = departments['results'][0]
            dept_id = client.extract_id_from_url(first_dept['id'])

            print(f"\n5. Getting detailed information for department {dept_id}...")
            dept_details = client.departments.get(dept_id)

            print(f"   Department details:")
            print(f"     Name: {dept_details.get('departmentname')}")
            print(f"     Company: {dept_details.get('company')}")
            print(f"     Franchises: {len(dept_details.get('franchises', []))}")

            # Show franchise information if available
            if dept_details.get('franchises'):
                print(f"\n   Franchise structure:")
                for franchise_url in dept_details['franchises'][:3]:  # Show first 3
                    print(f"     - {franchise_url}")

        # 6. Pagination example for companies
        print("\n6. Pagination example for companies...")
        print("   Fetching all companies across multiple pages:")

        all_companies = []
        page = 1
        while True:
            print(f"   Fetching page {page}...")
            page_data = client.companies.list(page=page)
            results = page_data.get('results', [])
            all_companies.extend(results)

            if not page_data.get('next'):
                break
            page += 1
            if page > 3:  # Limit for example
                print("   (Stopping at page 3 for this example)")
                break

        print(f"   Total companies fetched: {len(all_companies)}")

    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("\nYou don't have permission to access companies/departments.")
            print("Make sure your API user has the appropriate permissions.")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


def demonstrate_organizational_structure():
    """Show how to navigate the organizational structure."""
    print("\n" + "-" * 60)
    print("Organizational Structure Overview")
    print("-" * 60)

    print("\nThe FinAut API organizes entities hierarchically:")
    print("  Company (Bedrift)")
    print("    └─ Department (Avdeling)")
    print("         └─ Franchise (Franchiseavtale/Avtale)")
    print("              └─ Users are employed at departments")

    print("\nNavigating the structure:")
    print("  1. List companies: client.companies.list()")
    print("  2. Get company details: client.companies.get(company_id)")
    print("  3. Get company's departments: company['departments']")
    print("  4. Get department details: client.departments.get(dept_id)")
    print("  5. Get department's franchises: department['franchises']")

    print("\nCommon use cases:")
    print("  - Find which companies your API user can access")
    print("  - Get department IDs for creating new users")
    print("  - Navigate franchise structures for multi-location organizations")
    print("  - Build organizational hierarchies in your system")


def demonstrate_using_ids_for_user_creation():
    """Show how to use company/department info for user creation."""
    print("\n" + "-" * 60)
    print("Using Company/Department Info for User Creation")
    print("-" * 60)

    print("\nWhen creating users, you need department and company URLs:")
    print("  1. List companies to find the target company")
    print("  2. Get company details to see its departments")
    print("  3. Select appropriate department ID")
    print("  4. Use in user creation:")

    print("\n  new_user = client.users.create({")
    print("      'persnr': '01234567890',")
    print("      'first_name': 'Test',")
    print("      'last_name': 'User',")
    print("      'email': 'test@example.com',")
    print("      'work_for': {")
    print("          'department': 'https://api.norsktest.no/finautapi/v1/departments/123/',")
    print("          'company': 'https://api.norsktest.no/finautapi/v1/companies/456/'")
    print("      },")
    print("      'userroles': [...]")
    print("  })")

    print("\nTip: Use client.extract_id_from_url() to get numeric IDs from URLs")
    print("     and construct URLs using f-strings when needed.")


if __name__ == "__main__":
    main()
    demonstrate_organizational_structure()
    demonstrate_using_ids_for_user_creation()
    print("\n" + "=" * 60)
