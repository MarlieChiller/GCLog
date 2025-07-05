import pytest
from gcp_logger import GCPLogger


@pytest.fixture(autouse=True)
def reset_logger_state():
    """Reset logger state before each test."""
    GCPLogger._instance = None
    GCPLogger._configured = False
    yield
    GCPLogger._instance = None
    GCPLogger._configured = False
