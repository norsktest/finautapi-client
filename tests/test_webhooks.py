"""Tests for webhook signature verification.

The expected value is computed the way the server signs a delivery
(finautapi.webhooks.sign): HMAC-SHA256 over the raw body bytes.
"""
import hashlib
import hmac

from finautapi_client.webhooks import compute_signature, verify_signature

BODY = rb'{"id": 1, "navn": "\u00c6rlig"}'
SECRET = 'shared-secret'
GOOD = 'sha256=' + hmac.new(SECRET.encode(), BODY, hashlib.sha256).hexdigest()


def test_compute_signature_matches_the_server():
    assert compute_signature(BODY, SECRET) == GOOD
    assert compute_signature(BODY, SECRET.encode()) == GOOD


def test_valid_signature():
    assert verify_signature(BODY, GOOD, SECRET)


def test_tampered_body_is_rejected():
    assert not verify_signature(BODY.replace(b'1', b'2'), GOOD, SECRET)


def test_wrong_secret_is_rejected():
    assert not verify_signature(BODY, GOOD, 'other-secret')


def test_missing_signature_or_secret_is_rejected():
    assert not verify_signature(BODY, None, SECRET)
    assert not verify_signature(BODY, '', SECRET)
    assert not verify_signature(BODY, GOOD, '')
