#!/usr/bin/env python
"""
Example: Create a User in a Franchise

This example demonstrates how to create a user in a department that has franchises.
It first finds a department with franchises, then creates a user in that franchise.
"""

import os
import sys
import json
from pathlib import Path
from datetime import date

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import ValidationError, FinAutAPIException


def main():
    """Create a user in a franchise."""

    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - Create User in Franchise Example")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST,
        debug=True  # Set to True to see detailed requests
    )

    try:
        # 1. Find a department with franchises
        print("\n1. Finding departments with franchises...")
        departments = client.departments.list()

        dept_with_franchise = None
        franchise_url = None

        for dept in departments.get('results', []):
            if dept.get('franchises'):
                dept_with_franchise = dept
                franchise_url = dept['franchises'][0]  # Use first franchise
                break

        if not dept_with_franchise:
            print("No departments with franchises found.")
            return

        print(f"✓ Found department with franchises:")
        print(f"  Department: {dept_with_franchise.get('department_name')}")
        print(f"  Department URL: {dept_with_franchise.get('id')}")
        print(f"  Number of franchises: {len(dept_with_franchise.get('franchises', []))}")
        print(f"  Using franchise: {franchise_url}")

        # 2. Get the company URL from the department
        company_url = dept_with_franchise.get('company')
        print(f"  Company URL: {company_url}")

        # 3. Create user data with franchise
        print("\n2. Creating user in franchise...")

        # Generate a unique SSN for this test (you'd use a real one in production)
        import random
        random_ssn = f"55110089847"

        user_data = {
            "persnr": random_ssn,  # Using random SSN for testing
            "first_name": "Franchise",
            "last_name": "User",
            "email": f"franchise.user.{random.randint(1000,9999)}@example.com",
            "mobile": "98765432",
            "employee_alias": f"FRCH{random.randint(100,999)}",
            "work_for": {
                "department": dept_with_franchise.get('id'),
                "company": company_url,
                "franchise": franchise_url  # Add franchise to work_for
            },
            "userroles": [
                f"{client.base_url}userrole/afr_ka/"  # AFR Kandidat role
            ]
        }

        print(f"  SSN: {user_data['persnr']}")
        print(f"  Name: {user_data['first_name']} {user_data['last_name']}")
        print(f"  Email: {user_data['email']}")
        print(f"  Department: {dept_with_franchise.get('department_name')}")
        print(f"  Franchise: {franchise_url}")

        # 4. Create the user
        new_user = client.users.create(user_data)

        print(f"\n✓ User created successfully in franchise!")
        print(f"  User URL: {new_user.get('id')}")

        # Extract and display the user ID
        user_id = client.extract_id_from_url(new_user['id'])
        print(f"  User ID: {user_id}")

        # Display work_for information
        if new_user.get('work_for'):
            work_for = new_user['work_for']
            print(f"\nEmployment details:")
            print(f"  Company: {work_for.get('company')}")
            print(f"  Department: {work_for.get('department')}")
            print(f"  Franchise: {work_for.get('franchise')}")

        print("\n✓ User successfully created in franchise!")

    except ValidationError as e:
        print(f"\n✗ Validation error: {e}")
        print("\nNote: The SSN might already exist or franchise might not accept new users.")

    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("You don't have permission to create users in this franchise.")
        elif e.status_code == 404:
            print("Department or franchise not found.")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)