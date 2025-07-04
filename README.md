# GCP Logger

A lightweight, production-ready logging package for Google Cloud Platform applications. Built on top of [loguru](https://github.com/Delgan/loguru), it automatically detects GCP environments and provides structured JSON logging for cloud services while maintaining human-readable logs for local development.

## Features

- 🚀 **Auto-detection** of all major GCP services (Cloud Run, Cloud Functions, App Engine, GKE, Compute Engine)
- 📊 **Structured JSON logging** for GCP with proper severity levels
- 🎨 **Beautiful colored logs** for local development
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
pip install gcp-logger
```

## Quick Start

```python
from gcp_logger import get_logger

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
  "labels": {},
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
from gcp_logger import GCPLogger

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

## Advanced Usage

### Manual Environment Detection
```python
from gcp_logger import is_running_on_cloud

if is_running_on_cloud():
    print("Running on GCP!")
else:
    print("Running locally")
```

### Direct Logger Configuration
```python
from gcp_logger import GCPLogger

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

- Python 3.8+
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

### v0.1.0
- Initial release
- Support for all major GCP services
- Structured JSON logging for cloud environments
- Beautiful local development logs
- Thread-safe singleton pattern
- Comprehensive test coverage