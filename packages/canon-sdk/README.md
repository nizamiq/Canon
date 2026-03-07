# Canon SDK

Python SDK for the Canon Prompt Registry.

## Installation

```bash
pip install canon-sdk
```

## Quick Start

```python
from canon_sdk import CanonClient

# Initialize client
client = CanonClient("https://canon.nizamiq.com", api_token="your-token")

# Get a prompt
prompt = client.get_prompt("welcome-email")
print(prompt.current_version)

# Get the production version
production = client.get_prompt_by_tag("welcome-email", "production")
print(production.get_tagged_version("production").content)
```

## Features

- **Prompt Retrieval**: Get prompts by name, version, or tag
- **Prompt Management**: Create, update, and version prompts
- **Caching**: Optional in-memory caching for improved performance
- **Retry Logic**: Automatic retry with exponential backoff
- **Type Safety**: Full type hints and Pydantic models
- **Error Handling**: Comprehensive exception hierarchy

## Usage Examples

### List Prompts

```python
# List all prompts
prompts = client.list_prompts()

# Search prompts
results = client.list_prompts(search="email")

# Paginate
page2 = client.list_prompts(page=2, page_size=50)
```

### Create and Manage Prompts

```python
# Create a new prompt
prompt = client.create_prompt(
    name="welcome-email",
    content="Welcome {{name}}!",
    description="Welcome email template",
)

# Create a new version
prompt = client.create_version(
    "welcome-email",
    content="Updated welcome message for {{name}}",
)

# Tag a version as production
client.update_tags("welcome-email", version=2, tags=["production"])
```

### Caching

```python
# Enable caching (default)
client = CanonClient("https://canon.nizamiq.com", enable_caching=True)

# First call hits the API
prompt = client.get_prompt("my-prompt")

# Second call uses cache
prompt = client.get_prompt("my-prompt")  # Fast!

# Clear cache when needed
client.clear_cache()
```

## Error Handling

```python
from canon_sdk.exceptions import (
    CanonNotFoundError,
    CanonAuthError,
    CanonValidationError,
)

try:
    prompt = client.get_prompt("nonexistent")
except CanonNotFoundError:
    print("Prompt not found")
except CanonAuthError:
    print("Authentication failed")
except CanonValidationError as e:
    print(f"Validation error: {e.message}")
```

## Configuration

```python
client = CanonClient(
    base_url="https://canon.nizamiq.com",
    api_token="your-api-token",
    timeout=30.0,           # Request timeout
    max_retries=3,          # Max retry attempts
    enable_caching=True,    # Enable caching
    cache_ttl=300.0,        # Cache TTL in seconds
)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=canon_sdk --cov-report=html

# Type checking
mypy src/canon_sdk

# Linting
ruff check src/canon_sdk
```

## License

MIT
