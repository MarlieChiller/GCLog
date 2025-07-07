# GCLog

[![Tests](https://github.com/MarlieChiller/gcp_logger/workflows/Tests/badge.svg)](https://github.com/MarlieChiller/gcp_logger/actions)
[![codecov](https://codecov.io/gh/MarlieChiller/GCLog/graph/badge.svg?token=O1ZHUDHDYU)](https://codecov.io/gh/MarlieChiller/GCLog)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/gclog.svg)](https://pypi.org/project/gclog/)

A lightweight, production-ready logging package for Google Cloud Platform applications. Built on top of [loguru](https://github.com/Delgan/loguru), it automatically detects GCP environments and provides structured JSON logging for cloud services while maintaining human-readable logs for local development.

## Why?

I found that my logs in a fastapi app were using the Google Cloud Platforms' default log level irrespective of the
actual log level that was being emitted by the app itself. This meant my GCP logs were reporting things incorrectly, 
decreasing visibility and making it harder to debug issues. This issue came up time and again, and I didn't want to have 
to write a log formatter for every service, so I wrote this package to fix this problem once and for all.

## Features

- 🚀 **Auto-detection** of all major GCP services (Cloud Run, Cloud Functions, App Engine, GKE, Compute Engine)
- 📊 **Structured JSON logging** for GCP with proper severity levels
- 🎨 **Beautiful colored logs** for local development
- 🔄 **Request-scoped contextual logging** with automatic async propagation
- ⚡ **Thread-safe singleton** pattern for consistent logging across your application
- 🛡️ **Zero external dependencies** beyond loguru and requests
- 🧪 **Fully tested** with comprehensive test coverage

## Supported GCP Services

- **Cloud Run** - Detected via `K_REVISION` environment variable
- **Cloud Functions** - Detected via `FUNCTION_NAME` environment variable  
- **App Engine** - Detected via `GAE_APPLICATION` environment variable
- **Cloud Run Jobs** - Detected via `CLOUD_RUN_JOB` environment variable
- **Google Kubernetes Engine (GKE)** - Detected via `KUBERNETES_SERVICE_HOST` environment variable
- **Compute Engine** - Detected via metadata server API

## Installation

```bash
pip install gclog
```

## Quick Start

```python
from gclog import get_logger

# Get a configured logger instance
logger = get_logger()

# Use it like any loguru logger
logger.info("Application started")
logger.warning("This is a warning", extra={"user_id": "12345"})
logger.error("Something went wrong", extra={"error_code": "E001"})

# Exception logging with full traceback
try:
    result = 1 / 0
except Exception:
    logger.exception("Division by zero error")
```

## Log Output

### Local Development
```
2025-01-15 10:30:45.123 | INFO     | myapp:main:15 - Application started | {}
2025-01-15 10:30:45.124 | WARNING  | myapp:main:16 - This is a warning | {'user_id': '12345'}
2025-01-15 10:30:45.125 | ERROR    | myapp:main:17 - Something went wrong | {'error_code': 'E001'}
```

### GCP Cloud Environment
```json
{
  "severity": "INFO",
  "message": "Application started",
  "time": "2025-01-15T10:30:45.123000",
  "extra": {},
  "file": {"name": "main.py", "path": "/app/main.py"},
  "function": "main",
  "line": 15,
  "module": "myapp",
  "process": {"id": 1, "name": "python"},
  "thread": {"id": 140567890, "name": "MainThread"},
  "elapsed": 0.001
}
```

## Configuration

### Log Level
Set the log level using the `LOG_LEVEL` environment variable:

```bash
export LOG_LEVEL=INFO
```

Or pass it directly:
```python
from gclog import GCPLogger

logger = GCPLogger(level="DEBUG")
```

### Custom Labels
Add custom context to your logs:

```python
logger.info("User action", extra={
    "user_id": "user123",
    "action": "login",
    "ip_address": "192.168.1.1"
})
```

## Contextual Logging

GCLog supports request-scoped contextual logging that automatically propagates context across async boundaries. This is particularly useful for web applications where you want request-specific data (like user IDs, request IDs, etc.) to appear in all log messages for that request.

### Basic Contextual Logging

```python
from gclog import get_logger, set_contextual_logger, clear_contextual_logger

# Create a logger with bound context
log = get_logger()
contextual_logger = log.bind(user_id="123", request_id="req_456")

# Set it as the contextual logger for this request
set_contextual_logger(contextual_logger)

# Now all calls to get_logger() will return the contextual logger
def some_function():
    logger = get_logger()  # Automatically gets the contextual logger
    logger.info("Processing data")  # Includes user_id and request_id

# Don't forget to clear context when done
clear_contextual_logger()
```

### FastAPI Middleware Example

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from gclog import get_logger, set_contextual_logger, clear_contextual_logger
import uuid

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract relevant context from the request
        request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
        
        # Create contextual logger with request-level information
        base_logger = get_logger()
        contextual_logger = base_logger.bind(
            request_id=request_id,
            path=request.url.path,
            method=request.method
        )
        set_contextual_logger(contextual_logger)
        
        try:
            response = await call_next(request)
            return response
        finally:
            clear_contextual_logger()

# In your endpoints, add specific context as needed
@app.get("/users/{user_id}/data")
def get_user_data(user_id: str):
    log = get_logger()
    # Add endpoint-specific context
    log = log.bind(user_id=user_id)
    log.info("Fetching user data")  # Includes request_id, path, method, user_id
    return {"data": "..."}
```

### Key Benefits

- **Automatic Propagation**: Context flows through async function calls without manual passing
- **Request Isolation**: Each concurrent request maintains separate context
- **Zero Code Changes**: Existing `get_logger()` calls automatically get contextual logger
- **Clean Architecture**: No need to thread context through function parameters

## Advanced Usage

### Manual Environment Detection
```python
from gclog import is_running_on_cloud

if is_running_on_cloud():
    print("Running on GCP!")
else:
    print("Running locally")
```

### Direct Logger Configuration
```python
from gclog import GCPLogger

# This returns the global loguru logger instance
logger = GCPLogger(level="WARNING")

# All subsequent calls return the same configured instance
logger2 = GCPLogger()  # Same as logger
```

## Local Development

When not running on GCP, the logger:
- Uses colored output for better readability
- Sends INFO and below to stdout
- Sends WARNING and above to stderr
- Includes full diagnostic information

## Error Handling

The logger includes robust error handling:
- Graceful fallback if GCP detection fails
- Automatic fallback to basic logging if configuration fails
- Thread-safe initialization prevents race conditions

## Requirements

- Python 3.9+
- loguru
- requests (for GCP metadata server detection)

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.2.0
- **feat**: Add contextual logger support for request-scoped logging
- **feat**: New functions `set_contextual_logger()` and `clear_contextual_logger()`
- **feat**: Automatic async context propagation using Python's `contextvars`
- **feat**: Request isolation for concurrent requests
- **enhancement**: `get_logger()` now returns contextual logger when available
- **docs**: Add comprehensive FastAPI middleware example
- **test**: Full test coverage including async isolation tests

### v0.1.1
- **feat**: Add conditional extra data formatting for cleaner logs
- **improvement**: Extra data section only appears when data is present
- **docs**: Update examples and documentation

### v0.1.0
- Initial release
- Support for all major GCP services
- Structured JSON logging for cloud environments
- Beautiful local development logs
- Thread-safe singleton pattern
- Comprehensive test coverage