"""Basic hello world test to verify pytest setup."""


def hello_world() -> str:
    """Return a friendly greeting."""
    return "Hello, World!"


def test_hello_world():
    """Test that hello_world returns the expected greeting."""
    assert hello_world() == "Hello, World!"


def test_hello_world_not_empty():
    """Test that hello_world doesn't return an empty string."""
    assert hello_world() != ""
    assert len(hello_world()) > 0

