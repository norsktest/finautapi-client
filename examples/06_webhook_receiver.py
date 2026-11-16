#!/usr/bin/env python
"""
Example: Webhook receiver

FinAut POSTs a JSON record to your webhook URL when an exam result, a
competency result or a user status is saved for one of your users. This
receiver checks the signature, then hands the record on.

Ask Norsk Test to set a signing secret on your webhook and send it to you
over a separate channel. Every delivery then carries:

    X-FinAut-Signature: sha256=<hex HMAC-SHA256 of the raw body>
    X-Correlation-Id:   <unique id of this delivery>

Run it (standard library only; behind HTTPS in production):

    FINAUT_WEBHOOK_SECRET=... python 06_webhook_receiver.py

Answer 2xx quickly. FinAut waits 10 seconds and records the status code;
do slow work after answering.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add parent directory to path for development (remove in production)
sys.path.insert(0, str(Path(__file__).parent.parent))

from finautapi_client.webhooks import (
    CORRELATION_HEADER,
    SIGNATURE_HEADER,
    verify_signature,
)

SECRET = os.environ.get('FINAUT_WEBHOOK_SECRET', '')
PORT = int(os.environ.get('PORT', '5000'))
records = {}  # (webhook path, record id) -> record; use a database in production


def handle_record(path, record, correlation_id):
    """Your integration goes here.

    Store it as an upsert keyed on the record's own id: the same record
    arrives again when it is updated, and when Norsk Test resends
    deliveries (with a new correlation id).
    """
    records[(path, record.get('id'))] = record
    print(f'{correlation_id}: {json.dumps(record, ensure_ascii=False)[:200]}')


class WebhookHandler(BaseHTTPRequestHandler):
    """Verify, de-duplicate and process one delivery."""

    def do_POST(self):  # noqa: N802 (http.server's naming)
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        correlation_id = self.headers.get(CORRELATION_HEADER, '')

        # 1. Check the signature on the raw bytes, before parsing them.
        if not verify_signature(body, self.headers.get(SIGNATURE_HEADER), SECRET):
            return self._reply(401, {'error': 'invalid signature'})

        try:
            record = json.loads(body)
        except ValueError:
            return self._reply(400, {'error': 'invalid JSON'})

        handle_record(self.path, record, correlation_id)
        return self._reply(200, {'status': 'ok'})

    def _reply(self, status, payload):
        data = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    """Serve until interrupted."""
    if not SECRET:
        sys.exit('Set FINAUT_WEBHOOK_SECRET to the secret Norsk Test gave you.')
    print(f'Listening on http://localhost:{PORT}/ (Ctrl+C to stop)')
    HTTPServer(('', PORT), WebhookHandler).serve_forever()


if __name__ == '__main__':
    main()
