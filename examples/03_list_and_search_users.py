#!/usr/bin/env python
"""
Example: List and Search Users

This example demonstrates how to list users and search for specific users
using various filters like SSN, employee alias, or encrypted user ID.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import FinAutAPIException


def main():
    """Demonstrate listing and searching users."""

    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - List and Search Users Example")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST
    )

    try:
        # 1. List all users (paginated)
        print("\n1. Listing all accessible users (first page)...")
        all_users = client.users.list()

        print(f"   Total users: {all_users.get('count', 0)}")
        print(f"   Page size: {len(all_users.get('results', []))}")

        # Display first few users
        for user in all_users.get('results', [])[:5]:
            print(f"   - {user.get('first_name')} {user.get('last_name')} "
                  f"(ID: {user.get('id')}, Email: {user.get('email')})")

        # 2. Search by Norwegian SSN (fødselsnummer)
        print("\n2. Searching by SSN...")
        test_ssn = "01234567890"
        user_by_ssn = client.users.search_by_persnr(test_ssn)

        if user_by_ssn:
            print(f"   ✓ Found user: {user_by_ssn.get('first_name')} {user_by_ssn.get('last_name')}")
            print(f"     ID: {user_by_ssn.get('id')}")
            print(f"     Email: {user_by_ssn.get('email')}")
        else:
            print(f"   No user found with SSN: {test_ssn}")

        # 3. Search by employee alias
        print("\n3. Searching by employee alias...")
        test_alias = "EMP001"
        user_by_alias = client.users.search_by_employee_alias(test_alias)

        if user_by_alias:
            print(f"   ✓ Found user: {user_by_alias.get('first_name')} {user_by_alias.get('last_name')}")
            print(f"     ID: {user_by_alias.get('id')}")
            print(f"     Alias: {user_by_alias.get('employee_alias')}")
        else:
            print(f"   No user found with alias: {test_alias}")

        # 4. Get specific user by ID
        if all_users.get('results'):
            first_user_url = all_users['results'][0]['id']
            first_user_id = client.extract_id_from_url(first_user_url)
            print(f"
4. Getting specific user by ID ({first_user_id})...")
            specific_user = client.users.get(first_user_id)

            print(f"   User details:")
            print(f"     Name: {specific_user.get('first_name')} {specific_user.get('last_name')}")
            print(f"     Email: {specific_user.get('email')}")
            print(f"     Mobile: {specific_user.get('mobile')}")
            print(f"     Employee Alias: {specific_user.get('employee_alias')}")

            # Show employment information
            if specific_user.get('employment'):
                print(f"     Employment records: {len(specific_user['employment'])}")

            # Show user roles
            if specific_user.get('userroles'):
                print(f"     User roles: {len(specific_user['userroles'])}")
                for role in specific_user['userroles']:
                    print(f"       - Type: {role.get('usertype')} at {role.get('company')}")

        # 5. Pagination example
        print("\n5. Pagination example...")
        print("   Fetching all users across multiple pages:")

        all_users_list = []
        page = 1
        while True:
            print(f"   Fetching page {page}...")
            page_data = client.users.list(page=page)
            results = page_data.get('results', [])
            all_users_list.extend(results)

            if not page_data.get('next'):
                break
            page += 1
            if page > 5:  # Limit for example
                print("   (Stopping at page 5 for this example)")
                break

        print(f"   Total users fetched: {len(all_users_list)}")

    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("\nYou don't have permission to list users.")
            print("Make sure your API user has the appropriate permissions.")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


def demonstrate_advanced_filtering():
    """Show advanced filtering capabilities."""
    print("\n" + "-" * 60)
    print("Advanced Filtering Examples")
    print("-" * 60)

    print("\nThe API supports the following filters:")
    print("  - persnr: Norwegian social security number")
    print("  - encoded_userid: Encrypted user ID from external system")
    print("  - employee_alias: Employee identifier from HR system")
    print("  - page: Page number for pagination")

    print("\nExample filter combinations:")
    print("  client.users.list(persnr='12345678901')")
    print("  client.users.list(employee_alias='EMP001')")
    print("  client.users.list(encoded_userid='abc123def456')")
    print("  client.users.list(page=2)")


if __name__ == "__main__":
    main()
    demonstrate_advanced_filtering()
    print("\n" + "=" * 60)