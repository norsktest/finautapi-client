"""
FinAut API Python Client Library

A Python client library for interacting with the FinAut API.
"""

__version__ = "0.1.0"
__author__ = "Norsk Test AS"
__email__ = "support@norsktest.no"

from .client import FinAutAPIClient
from .exceptions import (
    FinAutAPIException,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    RateLimitError,
)

__all__ = [
    "FinAutAPIClient",
    "FinAutAPIException",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "ServerError",
    "RateLimitError",
]