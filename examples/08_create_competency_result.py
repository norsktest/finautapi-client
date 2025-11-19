import os
import sys
import json
from pathlib import Path
from datetime import date
import random

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import ValidationError, FinAutAPIException


def main(): 
    """Demonstrate creating competency_results """
    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - create compentency result example...")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST,
        debug=True
    )
    
    goal = random.randint(500, 1000)
    value = random.randint(500, 1000)
    
    try:
        
        print("=" * 60)
        print("Creating competency result...")
        print("=" * 60) 
        
        competency_result = client.competency_results.create({
            'goal': goal, 
            'user': 'test_encrypted_user_id',
            'finished': '2025-11-19',
            'value': value
        })
        
        if competency_result:
            print(f"Goal: {competency_result.get('goal')}")
            print(f"user: {competency_result.get('user')}")
            print(f"finished: {competency_result.get('finished')}")
            print(f"value: {competency_result.get('value')}")
            
            
    
    except ValidationError as e:
        print(f"\n✗ Validation error: {e}")
        print("\nCommon validation issues:")
        print("  - Courseinfo is required")
        print("  - content_responsible is required")
        print("  - External_system is required")
        print("  - External_id mustis required")
        
        
    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("\nYou don't have permission to create competncy results.")
            print("Make sure your API user has the required permission.")
        elif e.status_code == 404:
            print("Please verify that all required fields are set")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
        
    
if __name__ == "__main__":
    main()