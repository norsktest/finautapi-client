"""Helpers for receiving FinAut webhooks.

When Norsk Test has set a signing secret on your webhook, every delivery
carries an ``X-FinAut-Signature`` header: ``sha256=`` followed by the hex
HMAC-SHA256 of the raw request body, keyed with that secret. Verify it on
the raw bytes, before parsing the JSON.
"""

import hashlib
import hmac
from typing import Optional, Union

#: The header FinAut puts the signature in.
SIGNATURE_HEADER = 'X-FinAut-Signature'
#: The header with the delivery's unique id; log it, and quote it to Norsk Test.
#: A resent delivery gets a new one; key your data on the record's own id.
CORRELATION_HEADER = 'X-Correlation-Id'


def compute_signature(body: bytes, secret: Union[str, bytes]) -> str:
    """Return the ``sha256=<hex>`` signature FinAut sends for ``body``."""
    key = secret.encode('utf-8') if isinstance(secret, str) else secret
    return 'sha256=' + hmac.new(key, body, hashlib.sha256).hexdigest()


def verify_signature(body: bytes, signature: Optional[str],
                     secret: Union[str, bytes]) -> bool:
    """True if ``signature`` (the ``X-FinAut-Signature`` header value) is
    valid for the raw request ``body``.

    A missing header is never valid: once you have a secret, reject
    unsigned deliveries.
    """
    if not signature or not secret:
        return False
    return hmac.compare_digest(compute_signature(body, secret), signature)
