#
#  This example is not ready yet.
#

# #!/usr/bin/env python
# """
# Example: Handle Exam Results

# This example demonstrates how to retrieve and work with exam/assessment results.
# """

# import os
# import sys
# from pathlib import Path
# from datetime import datetime, timedelta

# # Add parent directory to path for development (remove in production)
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from finautapi_client import FinAutAPIClient
# from finautapi_client.exceptions import FinAutAPIException


# def main():
#     """Demonstrate working with exam results."""

#     # Get credentials from environment
#     CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
#     CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
#     API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

#     print("=" * 60)
#     print("FinAut API - Handle Exam Results Example")
#     print("=" * 60)

#     # Initialize the client
#     client = FinAutAPIClient(
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         host=API_HOST
#     )

#     try:
#         # 1. Get recent results (last 30 days)
#         print("\n1. Getting recent exam results (last 30 days)...")

#         recent_results = client.results.get_recent_results(days=30)

#         print(f"   Found {len(recent_results)} results in the last 30 days")

#         # Display first few results
#         for result in recent_results[:5]:
#             print(f"   - Exam: {result.get('exam_name', 'N/A')}")
#             print(f"     User: {result.get('user')}")
#             print(f"     Score: {result.get('score', 'N/A')}")
#             print(f"     Status: {result.get('status', 'N/A')}")
#             print(f"     Date: {result.get('exam_date', 'N/A')}")
#             print()

#         # 2. Get results for a specific user by SSN
#         print("\n2. Getting results for specific user...")

#         test_ssn = "01234567890"
#         user_results = client.results.list(persnr=test_ssn)

#         if user_results.get('results'):
#             print(f"   Found {len(user_results['results'])} results for user with SSN {test_ssn}:")

#             for result in user_results['results'][:3]:
#                 print(f"   - Result ID: {result.get('id')}")
#                 print(f"     Exam: {result.get('exam_name', 'N/A')}")
#                 print(f"     Score: {result.get('score', 'N/A')}")
#                 print(f"     Passed: {result.get('passed', 'N/A')}")
#         else:
#             print(f"   No results found for SSN: {test_ssn}")

#         # 3. Get results from a specific date
#         print("\n3. Getting results from specific date onwards...")

#         from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
#         dated_results = client.results.list(from_date=from_date)

#         print(f"   Found {dated_results.get('count', 0)} results since {from_date}")

#         # Group results by status
#         status_counts = {}
#         for result in dated_results.get('results', []):
#             status = result.get('status', 'unknown')
#             status_counts[status] = status_counts.get(status, 0) + 1

#         if status_counts:
#             print("   Results by status:")
#             for status, count in status_counts.items():
#                 print(f"     {status}: {count}")

#         # 4. Get detailed information about a specific result
#         if dated_results.get('results'):
#             first_result_id = dated_results['results'][0]['id']
#             print(f"\n4. Getting detailed result information (ID: {first_result_id})...")

#             detailed_result = client.results.get(first_result_id)

#             print(f"   Result details:")
#             print(f"     ID: {detailed_result.get('id')}")
#             print(f"     User: {detailed_result.get('user')}")
#             print(f"     Exam: {detailed_result.get('exam_name', 'N/A')}")
#             print(f"     Date: {detailed_result.get('exam_date', 'N/A')}")
#             print(f"     Score: {detailed_result.get('score', 'N/A')}")
#             print(f"     Passed: {detailed_result.get('passed', 'N/A')}")
#             print(f"     Status: {detailed_result.get('status', 'N/A')}")

#             # Additional details if available
#             if detailed_result.get('topics'):
#                 print(f"     Topics: {len(detailed_result['topics'])} topics covered")

#         # 5. Working with competency results
#         print("\n5. Working with competency results...")

#         # Example: Record a training completion
#         encrypted_userid = "example_encrypted_id_123"  # From external system

#         try:
#             competency_results = client.competency_results.list(
#                 encrypted_userid=encrypted_userid
#             )

#             if competency_results.get('results'):
#                 print(f"   Found {len(competency_results['results'])} competency results")

#                 for comp_result in competency_results['results'][:3]:
#                     print(f"   - Goal: {comp_result.get('goal')}")
#                     print(f"     Passed Date: {comp_result.get('passed_date')}")
#                     print(f"     External System: {comp_result.get('external_system', 'N/A')}")
#             else:
#                 print(f"   No competency results found for user")

#         except Exception as e:
#             print(f"   Note: {e}")

#         # Example: Record a new competency completion
#         print("\n   Recording new competency completion...")
#         print("   (This would create a new competency result record)")
#         print("   Example code:")
#         print("   ```")
#         print("   client.competency_results.record_completion(")
#         print('       encrypted_userid="user_abc123",')
#         print("       goal_id=456,")
#         print('       passed_date="2024-01-15",')
#         print('       external_system="LMS",')
#         print('       external_id="COURSE-789"')
#         print("   )")
#         print("   ```")

#     except FinAutAPIException as e:
#         print(f"\n✗ API error: {e}")
#         if e.status_code == 403:
#             print("\nYou don't have permission to view results.")
#         elif e.status_code == 404:
#             print("\nResource not found.")

#     except Exception as e:
#         print(f"\n✗ Unexpected error: {e}")


# def explain_result_types():
#     """Explain the different types of results."""
#     print("\n" + "-" * 60)
#     print("Result Types Explained")
#     print("-" * 60)

#     print("\nThe FinAut API handles two main types of results:")

#     print("\n1. Exam/Assessment Results (/results/)")
#     print("   - Traditional exam results")
#     print("   - Contains score, pass/fail status")
#     print("   - Linked to specific exam definitions")
#     print("   - May include topic-level breakdowns")

#     print("\n2. Competency Results (/competency_result/)")
#     print("   - Training completion records")
#     print("   - Linked to competency goals")
#     print("   - Can be reported from external systems (LMS)")
#     print("   - Uses encrypted user IDs for privacy")

#     print("\nFiltering Options:")
#     print("   - from_date: Get results after specific date")
#     print("   - persnr: Filter by Norwegian SSN")
#     print("   - employee_alias: Filter by employee ID")
#     print("   - encrypted_userid: For competency results")

#     print("\nPagination:")
#     print("   - Default page size is 100 results")
#     print("   - Use 'page' parameter to navigate")
#     print("   - Check 'next' field for more pages")


# if __name__ == "__main__":
#     main()
#     explain_result_types()
#     print("\n" + "=" * 60)