#!/usr/bin/env python
"""
Example: Webhook Receiver

This example demonstrates how to receive and process webhook notifications
from the FinAut API. This would typically run as a web service in your
infrastructure to receive real-time updates.

NOTE: This example uses Flask for simplicity, but you can use any web framework.
"""

import os
import json
import hmac
import hashlib
from datetime import datetime

# For this example, we'll use Flask (install with: pip install flask)
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("This example requires Flask. Install it with: pip install flask")
    exit(1)


# Create Flask application
app = Flask(__name__)

# Configuration (use environment variables in production)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your_webhook_secret_here')
DEBUG_MODE = os.environ.get('DEBUG', 'true').lower() == 'true'


def verify_webhook_signature(payload, signature, secret):
    """
    Verify webhook signature using HMAC-SHA256.

    NOTE: The FinAut API currently does NOT implement webhook signatures,
    but this is included as a best practice for when it's added.

    Args:
        payload: Raw request body
        signature: Signature from X-Hub-Signature header
        secret: Webhook secret key

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        # No signature provided (current FinAut behavior)
        print("⚠️  WARNING: No webhook signature provided (not implemented in FinAut yet)")
        return True  # Allow for now, but log warning

    # Expected format: sha256=<signature>
    if not signature.startswith('sha256='):
        return False

    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@app.route('/webhook/result', methods=['POST'])
def handle_result_webhook():
    """Handle exam result webhook notifications."""

    # Get correlation ID for tracking
    correlation_id = request.headers.get('X-Correlation-Id', 'unknown')

    if DEBUG_MODE:
        print(f"\n{'='*60}")
        print(f"Received Result Webhook - {datetime.now()}")
        print(f"Correlation ID: {correlation_id}")
        print(f"{'='*60}")

    # Verify signature (when implemented)
    signature = request.headers.get('X-Hub-Signature')
    if not verify_webhook_signature(request.data, signature, WEBHOOK_SECRET):
        print(f"❌ Invalid webhook signature for correlation ID: {correlation_id}")
        return jsonify({'error': 'Invalid signature'}), 401

    # Parse webhook data
    try:
        data = request.json
    except Exception as e:
        print(f"❌ Failed to parse webhook data: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400

    # Process the result
    process_result_update(data, correlation_id)

    # Return success response
    return jsonify({
        'status': 'success',
        'correlation_id': correlation_id,
        'processed_at': datetime.now().isoformat()
    }), 200


@app.route('/webhook/status', methods=['POST'])
def handle_status_webhook():
    """Handle user status change webhook notifications."""

    correlation_id = request.headers.get('X-Correlation-Id', 'unknown')

    if DEBUG_MODE:
        print(f"\n{'='*60}")
        print(f"Received Status Webhook - {datetime.now()}")
        print(f"Correlation ID: {correlation_id}")
        print(f"{'='*60}")

    # Verify signature (when implemented)
    signature = request.headers.get('X-Hub-Signature')
    if not verify_webhook_signature(request.data, signature, WEBHOOK_SECRET):
        print(f"❌ Invalid webhook signature for correlation ID: {correlation_id}")
        return jsonify({'error': 'Invalid signature'}), 401

    # Parse webhook data
    try:
        data = request.json
    except Exception as e:
        print(f"❌ Failed to parse webhook data: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400

    # Process the status change
    process_status_change(data, correlation_id)

    return jsonify({
        'status': 'success',
        'correlation_id': correlation_id,
        'processed_at': datetime.now().isoformat()
    }), 200


def process_result_update(data, correlation_id):
    """
    Process exam result update from webhook.

    Args:
        data: Webhook payload
        correlation_id: Correlation ID for tracking
    """
    print("\n📊 Processing Exam Result Update")
    print(f"   Correlation ID: {correlation_id}")

    # Extract key information
    user_id = data.get('user')
    exam_name = data.get('exam_name', 'Unknown')
    score = data.get('score')
    passed = data.get('passed')
    exam_date = data.get('exam_date')

    print(f"   User: {user_id}")
    print(f"   Exam: {exam_name}")
    print(f"   Score: {score}")
    print(f"   Passed: {passed}")
    print(f"   Date: {exam_date}")

    # TODO: Your business logic here
    # Examples:
    # - Update your LMS with the exam result
    # - Send notification email to user
    # - Update internal reporting database
    # - Trigger certificate generation if passed

    if passed:
        print("   ✅ User passed the exam!")
        # trigger_certificate_generation(user_id, exam_name)
    else:
        print("   ❌ User did not pass the exam")
        # schedule_retraining(user_id, exam_name)

    # Log the webhook for audit trail
    log_webhook_received('result', correlation_id, data)


def process_status_change(data, correlation_id):
    """
    Process user status change from webhook.

    Args:
        data: Webhook payload
        correlation_id: Correlation ID for tracking
    """
    print("\n🔄 Processing Status Change")
    print(f"   Correlation ID: {correlation_id}")

    # Extract key information
    user = data.get('user')
    ordning = data.get('ordning')
    status = data.get('status')
    status_date = data.get('status_date')
    comment = data.get('comment', '')

    print(f"   User: {user}")
    print(f"   Ordning: {ordning}")
    print(f"   New Status: {status}")
    print(f"   Effective Date: {status_date}")
    print(f"   Comment: {comment}")

    # TODO: Your business logic here
    # Examples:
    # - Update user access in your system
    # - Notify HR system of status change
    # - Update billing if user is withdrawn
    # - Send notification to user's manager

    if status == 'aktiv':
        print("   ✅ User activated in authorization scheme")
        # enable_user_access(user, ordning)
    elif status == 'hvilende':
        print("   ⏸️  User set to inactive/resting")
        # suspend_user_access(user, ordning)
    elif status == 'utmeldt':
        print("   ⛔ User withdrawn from scheme")
        # revoke_user_access(user, ordning)

    # Log the webhook for audit trail
    log_webhook_received('status', correlation_id, data)


def log_webhook_received(webhook_type, correlation_id, data):
    """
    Log webhook receipt for audit trail.

    In production, this would write to a database or logging service.
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': webhook_type,
        'correlation_id': correlation_id,
        'data': data
    }

    if DEBUG_MODE:
        print(f"\n📝 Webhook logged:")
        print(json.dumps(log_entry, indent=2, default=str))

    # TODO: In production, save to database
    # save_to_database(log_entry)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'FinAut Webhook Receiver',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with information."""
    return jsonify({
        'service': 'FinAut Webhook Receiver Example',
        'endpoints': {
            '/webhook/result': 'Receive exam result webhooks',
            '/webhook/status': 'Receive user status change webhooks',
            '/health': 'Health check endpoint'
        },
        'note': 'This is an example webhook receiver. Configure URLs in FinAut admin.'
    }), 200


def main():
    """Run the webhook receiver service."""
    print("=" * 60)
    print("FinAut Webhook Receiver Example")
    print("=" * 60)
    print(f"\n🚀 Starting webhook receiver on http://localhost:5000")
    print("\nEndpoints:")
    print("  POST http://localhost:5000/webhook/result - For exam results")
    print("  POST http://localhost:5000/webhook/status - For status changes")
    print("  GET  http://localhost:5000/health - Health check")
    print("\n⚠️  IMPORTANT: The FinAut API currently does NOT implement")
    print("    webhook signatures. This example includes signature")
    print("    verification as a best practice for when it's added.")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 60)

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)


if __name__ == "__main__":
    main()