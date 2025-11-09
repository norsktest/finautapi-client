#!/usr/bin/env python
"""
Example: Create a New User

This example demonstrates how to create a new user in the FinAut system
with employment and role information.
"""

import os
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import ValidationError, FinAutAPIException


def main():
    """Demonstrate creating a new user."""

    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - Create User Example")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST,
        debug=False  # Set to True to see request details
    )

    # Example user data
    # NOTE: You'll need to adjust the department and company IDs to match
    # actual entities you have access to in your FinAut instance
    user_data = {
        "persnr": "01234567890",  # Norwegian SSN (11 digits)
        "first_name": "Test",
        "last_name": "Bruker",
        "email": "test.bruker@example.com",
        "mobile": "12345678",
        "employee_alias": "EMP001",
        "employment": [
            {
                # You'll need to replace 123 with an actual department ID
                "department": f"{client.base_url}departments/123/",
                "start_date": date.today().isoformat(),
            }
        ],
        "userroles": [
            {
                # You'll need to replace 456 with an actual company ID
                "company": f"{client.base_url}companies/456/",
                "usertype": "KA"  # Kandidat (candidate)
                # Other options: BA (Bedriftsansvarlig), TL (Tillitsvalgt)
            }
        ]
    }

    try:
        # First, check if user already exists
        print(f"\nChecking if user already exists (SSN: {user_data['persnr']})...")
        existing_user = client.users.search_by_persnr(user_data['persnr'])

        if existing_user:
            print(f"✓ User already exists:")
            print(f"  ID: {existing_user['id']}")
            print(f"  Name: {existing_user.get('first_name')} {existing_user.get('last_name')}")
            print(f"  Email: {existing_user.get('email')}")

            # Example: Update the existing user
            print("\nUpdating existing user's email...")
            updated_data = {"email": "updated.email@example.com"}
            updated_user = client.users.partial_update(existing_user['id'], updated_data)
            print(f"✓ Email updated to: {updated_user.get('email')}")

        else:
            # Create new user
            print("\nCreating new user...")
            print(f"  Name: {user_data['first_name']} {user_data['last_name']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Employee Alias: {user_data['employee_alias']}")

            new_user = client.users.create(user_data)

            print(f"\n✓ User created successfully!")
            print(f"  User ID: {new_user['id']}")
            print(f"  URL: {new_user['url']}")

            # You can also retrieve the user to verify
            print("\nVerifying created user...")
            verified_user = client.users.get(new_user['id'])
            print(f"✓ User verified: {verified_user['first_name']} {verified_user['last_name']}")

    except ValidationError as e:
        print(f"\n✗ Validation error: {e}")
        print("\nCommon validation issues:")
        print("  - SSN must be exactly 11 digits")
        print("  - Department ID must exist and you must have access")
        print("  - Company ID must exist and you must have access")
        print("  - Email must be valid format")

    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("\nYou don't have permission to create users.")
            print("Make sure your API user has the 'finautapi_full_access' permission.")
        elif e.status_code == 404:
            print("\nOne of the referenced resources (department/company) was not found.")
            print("Please verify the IDs in the user_data.")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


def demonstrate_bulk_creation():
    """Example of creating multiple users."""
    print("\n" + "-" * 60)
    print("Bulk User Creation Example")
    print("-" * 60)

    # This would be your list of users to create
    users_to_create = [
        {
            "persnr": "11111111111",
            "first_name": "User",
            "last_name": "One",
            "email": "user.one@example.com",
        },
        {
            "persnr": "22222222222",
            "first_name": "User",
            "last_name": "Two",
            "email": "user.two@example.com",
        },
    ]

    print(f"\nWould create {len(users_to_create)} users...")
    print("(Not executing in this example)")


if __name__ == "__main__":
    main()
    demonstrate_bulk_creation()
    print("\n" + "=" * 60)