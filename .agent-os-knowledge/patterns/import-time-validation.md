# Import-Time Validation Pattern

## Description

TripWire validates environment variables at module import time, causing applications to fail fast during startup rather than at runtime when a misconfigured variable is accessed.

## Core Value Proposition

**Fail fast at import time, not in production.**

## Implementation

### Primary Location
`src/tripwire/core/tripwire_v2.py` - `TripWire.require()` and `TripWire.optional()`

### Code Example

```python
# In your config.py or settings.py - validated at import time
from tripwire import env

# Required variable - fails immediately if missing
DATABASE_URL: str = env.require("DATABASE_URL", format="postgresql")

# With validation constraints
PORT: int = env.require("PORT", min_val=1, max_val=65535)

# Optional with default
DEBUG: bool = env.optional("DEBUG", default=False)

# With format validation
EMAIL: str = env.require("ADMIN_EMAIL", format="email")

# With pattern validation
API_KEY: str = env.require("API_KEY", pattern=r"^sk-[a-z0-9]+$")

# With choices
LOG_LEVEL: str = env.require("LOG_LEVEL", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
```

### Validation Pipeline

The `require()` method follows this pipeline:

1. **Type Inference**: Infer type from annotation using inference engine
2. **Registration**: Register variable metadata in registry (for documentation)
3. **Retrieval**: Get value from `os.environ` with type coercion
4. **Validation**: Build and execute validation pipeline (Chain of Responsibility)
5. **Return**: Validated and type-coerced value

### Error Collection Mode

Two modes available:

```python
# Fail-fast mode (default) - stops at first error
env = TripWire(collect_errors=False)

# Collection mode - reports all errors at once
env = TripWire(collect_errors=True)
```

## When to Use

- Application configuration modules
- Settings files loaded at startup
- Any module where you need guaranteed env vars

## Anti-Patterns

```python
# WRONG: Using os.getenv directly bypasses validation
import os
database_url = os.getenv("DATABASE_URL")  # No validation!

# CORRECT: Use TripWire
from tripwire import env
DATABASE_URL: str = env.require("DATABASE_URL", format="postgresql")
```

## File References

- `src/tripwire/core/tripwire_v2.py` - Main implementation (lines 260-438)
- `src/tripwire/exceptions.py` - Error classes
- `src/tripwire/validation.py` - Type coercion functions