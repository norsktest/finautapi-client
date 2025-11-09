#!/usr/bin/env python
"""
Example: Basic Authentication with FinAut API

This example demonstrates how to authenticate with the FinAut API using
OAuth2 Client Credentials flow.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import AuthenticationError


def main():
    """Demonstrate basic authentication with the API."""

    # Get credentials from environment variables or use test values
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - Basic Authentication Example")
    print("=" * 60)
    print(f"\nConnecting to: {API_HOST}")

    try:
        # Initialize the client
        client = FinAutAPIClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            host=API_HOST,
            debug=True  # Enable debug output to see requests
        )

        # Test the connection
        print("\nTesting connection...")
        if client.test_connection():
            print("✓ Successfully connected to the API!")
        else:
            print("✗ Failed to connect to the API")
            return

        # The client automatically handles token refresh
        print("\n✓ OAuth2 token obtained and will be automatically refreshed")

        # Try to list companies to verify authentication works
        print("\nFetching accessible companies...")
        companies = client.companies.list()

        if companies.get('results'):
            print(f"\n✓ Found {len(companies['results'])} accessible companies:")
            for company in companies['results'][:3]:  # Show first 3
                print(f"  - {company.get('company_name', 'Unknown')} (ID: {company.get('id')})")
        else:
            print("No companies found (this might be normal for your account)")

    except AuthenticationError as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nPlease check your credentials:")
        print(f"  CLIENT_ID: {CLIENT_ID[:10]}..." if len(CLIENT_ID) > 10 else CLIENT_ID)
        print(f"  CLIENT_SECRET: {'*' * 10}")
        print(f"  API_HOST: {API_HOST}")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)