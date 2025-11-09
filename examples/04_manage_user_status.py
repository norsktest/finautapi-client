#
#  This example is not ready yet.
#

# #!/usr/bin/env python
# """
# Example: Manage User Status

# This example demonstrates how to manage user statuses in authorization schemes,
# including activating, deactivating, and withdrawing users.
# """

# import os
# import sys
# from pathlib import Path
# from datetime import date, timedelta

# # Add parent directory to path for development (remove in production)
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from finautapi_client import FinAutAPIClient
# from finautapi_client.exceptions import ValidationError, FinAutAPIException


# def main():
#     """Demonstrate managing user statuses."""

#     # Get credentials from environment
#     CLIENT_ID = os.environ.get('FINAUT_CLIENT_ID', 'your_client_id_here')
#     CLIENT_SECRET = os.environ.get('FINAUT_CLIENT_SECRET', 'your_client_secret_here')
#     API_HOST = os.environ.get('FINAUT_API_HOST', 'https://api.norsktest.no')

#     print("=" * 60)
#     print("FinAut API - Manage User Status Example")
#     print("=" * 60)

#     # Initialize the client
#     client = FinAutAPIClient(
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         host=API_HOST,
#         debug=True
#     )

#     # Example IDs - you'll need to use real IDs from your system
#     USER_ID = 590499  # Replace with actual user ID
#     APPNAME = "afr"  # Authorization scheme code
#     PERSNR = "55110098692"  # Replace with actual personal number

#     try:
#         # 1. List current user statuses
#         print("\n1. Listing user statuses...")

#         # You can filter by SSN or employee alias
#         statuses = client.userstatus.list(persnr=PERSNR)

#         if statuses.get('results'):
#             print(f"   Found {len(statuses['results'])} status records:")
#             for status in statuses['results'][:5]:
#                 print(f"   - Status: {status.get('status')} "
#                       f"Date: {status.get('status_date')} "
#                       f"Ordning: {status.get('ordning')}")
#         else:
#             print("   No status records found")

#         # 2. Note: Setting user as active is not supported through the API
#         print(f" 2. Note: Setting user as 'aktiv' is not supported")
#         print("   The API only allows creating 'hvilende' or 'utmeldt' statuses.")
#         print("   Active status is typically set through other means (certification, etc).")

#         # 3. Set user as inactive (hvilende)
#         print(f"\n3. Setting user {USER_ID} as inactive...")

#         future_date = (date.today() + timedelta(days=30)).isoformat()

#         try:
#             inactive_status = client.userstatus.set_inactive(
#                 user_id=USER_ID,
#                 appname=APPNAME,
#                 status_date=future_date,
#                 comment="Temporary leave - returning in 30 days",
#                 status_set_by_id=1  # ID of the user setting the status (e.g., admin user)
#             )
#             print(f"   ✓ User set to inactive")
#             print(f"     Effective date: {inactive_status.get('status_date')}")
#         except ValidationError as e:
#             print(f"   ✗ Could not set user inactive: {e}")

#         # 4. Withdraw user from authorization scheme
#         print(f"\n4. Withdrawing user {USER_ID} from ordning...")

#         try:
#             withdrawn_status = client.userstatus.set_withdrawn(
#                 user_id=USER_ID,
#                 appname=APPNAME,
#                 status_date=date.today().isoformat(),
#                 comment="User requested withdrawal",
#                 status_set_by_id=1  # ID of the user setting the status
#             )
#             print(f"   ✓ User withdrawn from ordning")
#             print(f"     Status: {withdrawn_status.get('status')}")
#         except ValidationError as e:
#             print(f"   ✗ Could not withdraw user: {e}")

#         # 5. Get latest status for a user
#         print("\n5. Getting latest user status...")

#         latest = client.userstatus.get_latest(persnr="01234567890")

#         if latest.get('results'):
#             for status in latest['results']:
#                 print(f"   Latest status for ordning {status.get('ordning')}:")
#                 print(f"     Status: {status.get('status')}")
#                 print(f"     Date: {status.get('status_date')}")
#                 print(f"     Comment: {status.get('comment', 'N/A')}")

#         # 6. Create custom status record
#         print("\n6. Creating custom status record...")

#         custom_status = {
#             "appname": APPNAME,  # Short code like "afr", "krd"
#             "user": f"{client.base_url}user/{USER_ID}/",
#             "status": "utmeldt",  # Only 'hvilende' or 'utmeldt' allowed
#             "reason": "utmeldt",  # Required field
#             "status_set_by": f"{client.base_url}user/1/",  # Required
#             "status_date": date.today().isoformat(),
#             "comment": "Manual withdrawal via API"
#         }

#         try:
#             new_status = client.userstatus.create(custom_status)
#             print(f"   ✓ Custom status created")
#             print(f"     ID: {new_status.get('id')}")
#         except Exception as e:
#             print(f"   ✗ Could not create custom status: {e}")

#     except FinAutAPIException as e:
#         print(f"\n✗ API error: {e}")
#         if e.status_code == 403:
#             print("\nYou don't have permission to manage user statuses.")
#         elif e.status_code == 404:
#             print("\nUser or ordning not found. Please check the IDs.")

#     except Exception as e:
#         print(f"\n✗ Unexpected error: {e}")


# def explain_status_types():
#     """Explain the different status types."""
#     print("\n" + "-" * 60)
#     print("Status Types Explained")
#     print("-" * 60)

#     print("\nFinAut supports three status types:")
#     print("\n1. 'aktiv' (Active)")
#     print("   - User is actively participating in the authorization scheme")
#     print("   - Can take exams and receive certifications")

#     print("\n2. 'hvilende' (Inactive/Resting)")
#     print("   - User is temporarily inactive")
#     print("   - Maintains their progress but cannot take new exams")
#     print("   - Often used for maternity leave, sick leave, etc.")

#     print("\n3. 'utmeldt' (Withdrawn)")
#     print("   - User has been withdrawn from the authorization scheme")
#     print("   - No longer participates in the program")
#     print("   - Historical data is preserved")

#     print("\nImportant notes:")
#     print("- Status changes are date-based")
#     print("- You can set future-dated status changes")
#     print("- Each status change creates a new record (history is preserved)")
#     print("- Comments are optional but recommended for audit trail")


# if __name__ == "__main__":
#     main()
#     explain_status_types()
#     print("\n" + "=" * 60)