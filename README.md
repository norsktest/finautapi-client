# FinAut API Python Client

A Python client library for interacting with the FinAut API - Norwegian authorization/certification system.

## Features

- 🔐 **OAuth2 Authentication** - Automatic token management with refresh
- 🚀 **Simple Interface** - Pythonic API design for easy integration
- 📦 **Resource-based Design** - Organized by API resources (users, companies, results, etc.)
- ⚡ **Minimal Dependencies** - Only requires `requests` and `python-dateutil`
- 🛡️ **Error Handling** - Comprehensive exception handling with detailed error messages
- 📝 **Full Type Hints** - Better IDE support and code documentation
- 🔄 **Webhook Support** - Example receiver for processing webhooks

## Installation

### From PyPI (when published)
```bash
pip install finautapi-client
```

### From Source
```bash
git clone https://github.com/norsktest/finautapi-client.git
cd finautapi-client
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"  # Includes testing and linting tools
```

## Quick Start

```python
from finautapi_client import FinAutAPIClient

# Initialize the client
client = FinAutAPIClient(
    client_id='your_client_id',
    client_secret='your_client_secret',
    host='https://api.norsktest.no'  # Optional, this is the default
)

# List users
users = client.users.list()
print(f"Found {users['count']} users")

# Search for a specific user
user = client.users.search_by_persnr('12345678901')
if user:
    print(f"User: {user['first_name']} {user['last_name']}")

# Create a new user (requires work_for and userroles)
new_user = client.users.create({
    'persnr': '01234567890',
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'test@example.com',
    'work_for': {
        'department': 'https://api.norsktest.no/finautapi/v1/departments/123/',
        'company': 'https://api.norsktest.no/finautapi/v1/companies/456/'
    },
    'userroles': [
        'https://api.norsktest.no/finautapi/v1/userrole/afr_ka/'
    ]
})
```

## Configuration

### Environment Variables

The client supports configuration via environment variables:

```bash
export FINAUT_CLIENT_ID="your_client_id"
export FINAUT_CLIENT_SECRET="your_client_secret"
export FINAUT_API_HOST="https://api.norsktest.no"
```

### Client Options

```python
client = FinAutAPIClient(
    client_id='...',
    client_secret='...',
    host='https://api.norsktest.no',
    timeout=30,           # Request timeout in seconds
    verify_ssl=True,      # Verify SSL certificates
    debug=False          # Enable debug output
)
```

## Resources

The client provides access to the following API resources:

### Users
```python
# List users with filters
users = client.users.list(persnr='12345678901', page=1)

# Get specific user
user = client.users.get(user_id=123)

# Create user
user = client.users.create({...})

# Update user
user = client.users.update(user_id=123, user_data={...})

# Partial update
user = client.users.partial_update(user_id=123, user_data={...})

# Search helpers
user = client.users.search_by_persnr('12345678901')
user = client.users.search_by_employee_alias('EMP001')
```

### Companies & Departments
```python
# List companies
companies = client.companies.list()

# Get company details
company = client.companies.get(company_id=456)

# List departments
departments = client.departments.list()

# Get department
department = client.departments.get(department_id=789)
```

### User Status
```python
# List user statuses
statuses = client.userstatus.list(persnr='12345678901')

# Note: Setting user as 'aktiv' is NOT supported through the API
# Active status is set through other processes (certification completion, etc.)

# Set user as inactive (hvilende)
status = client.userstatus.set_inactive(
    user_id=123,
    appname='afr',  # Use appname code: 'afr', 'krd', 'gos', etc.
    status_date='2024-01-01',
    comment='Temporary leave',
    status_set_by_id=1  # ID of user making the change
)

# Withdraw user (utmeldt)
status = client.userstatus.set_withdrawn(
    user_id=123,
    appname='afr',  # Short code, NOT a URL
    status_date='2024-01-01',
    comment='User withdrawn',
    status_set_by_id=1
)

# Get latest status
latest = client.userstatus.get_latest(persnr='12345678901')
```

### Exam Results
```python
# List results with filters
results = client.results.list(
    from_date='2024-01-01',
    persnr='12345678901',
    page=1
)

# Get specific result
result = client.results.get(result_id=999)

# Get user's results
user_results = client.results.get_user_results(persnr='12345678901')

# Get recent results (last 30 days)
recent = client.results.get_recent_results(days=30)
```

### Competency Results
```python
# List competency results
results = client.competency_results.list(encrypted_userid='abc123')

# Record completion
result = client.competency_results.record_completion(
    encrypted_userid='abc123',
    goal_id=456,
    passed_date='2024-01-15',
    external_system='LMS',
    external_id='COURSE-789'
)
```

### Employment Records
```python
# Get employment record
employment = client.employment.get(employment_id=555)
```

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from finautapi_client import (
    FinAutAPIException,      # Base exception
    AuthenticationError,      # 401 - Authentication failed
    PermissionDeniedError,    # 403 - No permission
    NotFoundError,           # 404 - Resource not found
    ValidationError,         # 422 - Validation failed
    RateLimitError,          # 429 - Rate limit exceeded
    ServerError              # 5xx - Server errors
)

try:
    user = client.users.create({...})
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response.text}")
except AuthenticationError:
    print("Check your credentials")
except FinAutAPIException as e:
    print(f"API error: {e}")
```

## Webhooks

The FinAut API can send webhook notifications for events. See `examples/06_webhook_receiver.py` for a complete Flask-based webhook receiver example.

**Important:** The FinAut API currently does NOT implement webhook signature verification. This is a known security issue documented in the API's TODO.md.

## Examples

The `examples/` directory contains complete, runnable examples:

1. **01_basic_authentication.py** - Authentication and connection testing
2. Create users<sup>(*)</sup>:
   1. **02_create_user.py** - Creating and updating users
   2. **02b_create_user_in_franchise.py** - Creating users in franchise companies
3. List and search:
   1. **03_list_and_search_users.py** - Listing and searching users
   2. **03b_list_companies.py** - Listing companies and departments
4. **04_manage_user_status.py** - Managing user statuses in authorization schemes
5. **05_handle_exam_results.py** - Working with exam and competency results
6. **06_webhook_receiver.py** - Flask-based webhook receiver

**<sup>(*)</sup> Note:** Running user creation examples will create real users in the FinAut test environment. Use caution and clean up test data as needed. finautapli-client/persnr.py contains helper functions to generate valid Norwegian personal numbers for testing.

Run an example:
```bash
cd examples
python 01_basic_authentication.py
```

## Testing

Run the test suite:
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=finautapi_client

# Run specific test
pytest tests/test_client.py::test_authentication
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/norsktest/finautapi-client.git
cd finautapi-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Code Quality
```bash
# Format code
black finautapi_client

# Lint code
flake8 finautapi_client
pylint finautapi_client

# Type checking
mypy finautapi_client
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## API Documentation

- [FinAut API Documentation](https://api.norsktest.no/finautapi/v1/docs/)
- [Developer Guide](https://norsktest.gitlab.io/finautapi)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/norsktest/finautapi-client/issues
- Email: support@norsktest.no

## Changelog

### Version 0.1.0 (2025-11-09)
- Initial release
- OAuth2 authentication with automatic token refresh
- Support for users, companies, departments, status, results, and competency resources
- Comprehensive error handling
- Example scripts
- Basic test coverage

## Security Note

⚠️ **Important:** The FinAut API server currently has several security vulnerabilities documented in its TODO.md:
- Webhook authentication is not implemented
- Input validation is incomplete
- Debug statements may expose sensitive data

Please ensure you:
1. Use HTTPS for all API communications
2. Store credentials securely (never in code)
3. Implement your own webhook verification
4. Validate all data from the API
5. Keep the client library updated

## Authors

- Norsk Test AS - Initial work

## Acknowledgments

- Thanks to all contributors
- Built for the Norwegian authorization/certification system
- Powered by Django REST Framework on the server side