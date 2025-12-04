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
    """Demonstrate getting competency_results """
    # Get credentials from environment
    CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
    CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
    API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

    print("=" * 60)
    print("FinAut API - Competency result example...")
    print("=" * 60)

    # Initialize the client
    client = FinAutAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        host=API_HOST,
        debug=True
    )
    
    """    result = client.competency_result.create({
        'goal': 'finautapi/v1/goals/1/',
        'user': 'encrypted_user_id',
        'finished': '2025-11-12',
        'courseinfo': 'AutoCAD Basics - Introduction Course',
        #'content_responsible': 'John Smith, Training Manager',
        #'reward_type': 'finautapi/v1/reward_types/1/',
        #'value': 1.0,
        'external_system': 'Moodle LMS',
        'external_id': 'moodle_course_12345'
    }) """
    
    print("=" * 60)
    print("Printing the results this user has access too")
    print("=" * 60)
    
    try:
        all_competency_results = client.competency_results.list(page=1)
        print(f"   Page size: {len(all_competency_results.get('results', []))}")

        print("=" * 60)
        print("Printing data from first two results")
        
        for res in all_competency_results.get('results', [])[:2]:
            print(f"Result ID: {res.get('id')}")
            print(f"User ID: {res.get('user').get('id')}")
            print(f"User: first_name: {res.get('user').get('first_name')}, last_name: {res.get('user').get('last_name')}")
            
        print("=" * 60)
        print("Checking rate limit status...")

        # Get rate limit info from response headers
        response = client.request('GET', 'competency_result/', params={'page': 1})
        for k, v in response.headers.items():
            print(k, v)
        #print(response.headers)
        rate_limit_limit = response.headers.get('X-RateLimit-Limit')
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        rate_limit_reset = response.headers.get('X-RateLimit-Reset')

        if rate_limit_limit:
            print(f"Rate Limit - Total: {rate_limit_limit}")
            print(f"Rate Limit - Remaining: {rate_limit_remaining}")
            print(f"Rate Limit - Reset: {rate_limit_reset}")
        else:
            print("Rate limit headers not available")


    except FinAutAPIException as e:
        print(f"\n✗ API error: {e}")
        if e.status_code == 403:
            print("\nYou don't have permission for this action.")
            print("Make sure your API user has the 'finautapi_full_access' permission.")
        elif e.status_code == 404:
            print("\nResource not found")
            print("Please verify that the endpoint is correct")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        

if __name__ == "__main__":
    main()