# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**finautapi-client** is a Python client library for the FinAut API, the Norwegian authorization/certification system. It provides a Pythonic interface to interact with users, companies, departments, exam results, competencies, and employment records via REST API with OAuth2 authentication.

**Key characteristics:**
- Minimal dependencies (only `requests` and `python-dateutil`)
- Full type hints for IDE support
- OAuth2 Client Credentials flow with automatic token refresh
- Resource-based architecture for different API endpoints
- Comprehensive exception handling with specific error types

## Architecture

### Core Components

**Client Layer** (`finautapi_client/client.py`)
- `FinAutAPIClient`: Main entry point; initializes all resources and handles HTTP requests
- Manages base URL construction (`/finautapi/v1/`), timeouts, SSL verification, and debug mode
- All resource methods delegate to the client's `request()` method which handles authentication and error responses

**Authentication** (`finautapi_client/auth.py`)
- `OAuth2Handler`: Handles Client Credentials flow with automatic token refresh
- Refreshes tokens 60 seconds before expiration (configurable via `_refresh_buffer`)
- `BasicAuthHandler`: For development/testing only (not used in production)

**Resource Classes** (`finautapi_client/resources/`)
- Each resource (users, companies, departments, userstatus, results, competency_results, employment) extends the base pattern
- Resources use the client's HTTP methods (`get()`, `post()`, `patch()`, `put()`, `delete()`)
- Query parameters and filters vary by resource; refer to individual resource classes

**Exception Hierarchy** (`finautapi_client/exceptions.py`)
- `FinAutAPIException`: Base class
- Specific subclasses: `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ValidationError` (422), `RateLimitError` (429), `ServerError` (5xx)
- Errors are raised automatically based on HTTP response status code

### Request Flow

1. Resource method (e.g., `users.create()`) prepares endpoint and payload
2. Calls `client.post(endpoint, json=payload)`
3. `client.request()` method:
   - Builds full URL via `urljoin()`
   - Gets OAuth token from `OAuth2Handler.access_token` (auto-refreshes if needed)
   - Makes HTTP request with `requests` library
   - Calls `_handle_response_errors()` which raises exceptions on 4xx/5xx
   - Returns response object

## Development Workflow

### Setup & Installation

```bash
# Install in development mode
pip install -e ".[dev]"
```

This installs the package and all dev dependencies (pytest, pytest-cov, responses, black, flake8, pylint, mypy).

### Building & Testing

```bash
# Run full test suite
pytest

# Run tests with coverage report
pytest --cov=finautapi_client

# Run a single test
pytest tests/test_client.py::test_authentication

# Format code with Black
black finautapi_client tests examples

# Lint code
flake8 finautapi_client
pylint finautapi_client

# Type checking
mypy finautapi_client
```

### Running Examples

Located in `examples/` directory:
- `01_basic_authentication.py` - Connection testing
- `02_create_user.py` - Create/update users
- `02b_create_user_in_franchise.py` - Franchise-specific user creation
- `03_list_and_search_users.py` - Listing and searching
- `03b_list_companies.py` - Companies and departments
- `04_manage_user_status.py` - User status management (active/inactive/withdrawn)
- `05_handle_exam_results.py` - Results handling
- `06_webhook_receiver.py` - webhook receiver that checks signatures (standard library only)

Run with: `cd examples && python 01_basic_authentication.py`

**Warning:** User creation examples create real data in the test environment. Clean up after testing.

## Key Implementation Details

### OAuth2 Token Management
- Tokens are requested with `grant_type=client_credentials` and scope `read write`
- Expiration is tracked; refresh happens automatically 60 seconds before expiration
- On 401 responses, the token is invalidated (`auth.invalidate_token()`) and the exception is raised
- The client retries the request on the next call with a fresh token

### URL Construction
- Base URL: `{host}/finautapi/v1/` where host defaults to `https://api.norsktest.no`
- Endpoints are relative paths appended to base URL via `urljoin()`
- Numeric IDs can be extracted from API URLs via `FinAutAPIClient.extract_id_from_url()`

### Debug Mode
- Enabled via `client = FinAutAPIClient(..., debug=True)`
- Logs request method, URL, params, JSON payload, and response status/body
- Response body is truncated to 1750 characters to avoid massive output
- Token refresh messages are always printed (including in non-debug mode)

### Error Handling Strategy
- All HTTP errors (4xx/5xx) raise specific exceptions with message, response object, and status code
- Callers should catch specific exception types (e.g., `ValidationError`, `NotFoundError`)
- Response body is preserved in exception object for debugging

### Testing with Mocked Requests
- Tests use the `responses` library to mock HTTP requests
- Common pattern: `@responses.activate` decorator to enable mocking, then register mock responses before assertions

## Git & Branching

- Main branch: `master`
- Current feature branch shown in git status
- Commit messages should be descriptive (looking at recent commits for style guide)
- No auto-generated commits; review changes with `git status` and `git diff` before committing

## Common Gotchas

1. **URL vs Code for appnames**: Some methods (like `userstatus.set_inactive()`) expect short codes (`'afr'`, `'krd'`, etc.), NOT full URLs
2. **User creation with franchise**: Department and company are provided as URLs in work_for object
3. **Webhook signatures**: deliveries carry `X-FinAut-Signature` (sha256 HMAC of the raw body) when Norsk Test has set a secret on the webhook; `finautapi_client.verify_signature()` checks it
4. **Inactive vs Withdrawn**: Two separate status setters with different semantics; 'aktiv' status cannot be set via API
5. **Token refresh delay**: If a token expires between requests, a 401 will be raised; the client will refresh on retry

## File Structure Reference

```
finautapi_client/
├── __init__.py                    # Exports main classes
├── client.py                      # FinAutAPIClient main class
├── auth.py                        # OAuth2 and Basic auth handlers
├── exceptions.py                  # Exception classes
├── persnr.py                      # Helper for Norwegian personal numbers
├── webhooks.py                    # verify_signature() for webhook receivers
└── resources/
    ├── __init__.py
    ├── users.py                   # UserResource
    ├── companies.py               # CompanyResource
    ├── departments.py             # DepartmentResource
    ├── userstatus.py              # UserStatusResource
    ├── results.py                 # ResultResource
    ├── competency_result.py        # CompetencyResultResource
    └── employment.py              # EmploymentResource

tests/
├── test_client.py                 # Main client tests
├── test_auth.py                   # Auth handler tests
├── test_competency_result.py      # competency_results vs the server's contract
├── test_results.py                # get_all() paging and result helpers
├── test_webhooks.py               # signature verification
└── __init__.py

examples/
├── 01_basic_authentication.py
├── 02_create_user.py
├── 02b_create_user_in_franchise.py
├── 03_list_and_search_users.py
├── 03b_list_companies.py
├── 04_manage_user_status.py
├── 05_handle_exam_results.py
├── 06_webhook_receiver.py
└── 07_record_competency_result.py
```

## Security Notes

- Store credentials in environment variables (`FINAUT_CLIENT_ID`, `FINAUT_CLIENT_SECRET`, `FINAUT_API_HOST`), never in code
- Always use HTTPS for API communications
- Verify webhook signatures with `verify_signature()` on the raw body before parsing
- Debug mode prints request parameters (which can include persnr) but only the last 4 characters of the access token
