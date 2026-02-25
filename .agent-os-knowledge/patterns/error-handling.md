# Actionable Error Handling Pattern

## Description

TripWire provides actionable, developer-friendly error messages with specific fix suggestions. Errors include context, expected values, and remediation steps.

## Implementation

### Primary Location
`src/tripwire/exceptions.py`

### Exception Hierarchy

```python
TripWireError                     # Base exception
  MissingVariableError            # Required variable not set
  ValidationError                 # Validation failed
  TypeCoercionError               # Type conversion failed
  EnvFileNotFoundError            # .env file missing
  SecretDetectedError             # Secret found in unsafe location
  DriftError                      # Config drifted from expected
  GitAuditError                   # Base for git operations
    NotGitRepositoryError         # Not a git repo
    GitCommandError               # Git command failed
  TripWireMultiValidationError    # Multiple validation errors
```

### Actionable Error Messages

```python
class MissingVariableError(TripWireError):
    def __init__(self, variable_name: str, description: Optional[str] = None):
        # Multi-line helpful message
        lines = [
            f"\n[X] Missing required environment variable: {variable_name}",
            "",
        ]
        if description:
            lines.append(f"Description: {description}")

        lines.extend([
            "To fix this, choose one option:",
            "",
            "  1. Add to .env file:",
            f"     {variable_name}=your-value-here",
            "",
            "  2. Set in your shell:",
            f"     export {variable_name}=your-value-here",
            "",
            "  3. Copy from example (if available):",
            "     cp .env.example .env",
            "",
            "[Tip] Run 'tripwire init' to create starter files",
        ])
```

### Multi-Validation Error (Batch Reporting)

```python
class TripWireMultiValidationError(TripWireError):
    """Reports all validation errors at once."""

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        self.error_count = len(errors)
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Output format:

        TripWire found 3 environment variable error(s):

          1. DATABASE_URL
             ├─ Error: Invalid format: expected postgresql
             ├─ Received: 'mysql://...'
             └─ Fix: Use format: postgresql://user:pass@host:port/db

          2. PORT
             ├─ Error: Out of range: must be >= 1 and <= 65535
             ├─ Received: 70000
             └─ Fix: Decrease PORT value
        """

    def _get_fix_suggestion(self, error: ValidationError) -> str:
        """Context-specific fix suggestions based on error type."""
        reason = error.reason.lower()

        if "invalid format" in reason:
            if "postgresql" in reason:
                return "Use format: postgresql://user:pass@host:port/db"
            elif "email" in reason:
                return "Use format: user@example.com"
            # ...

        if "min_length" in reason:
            return f"Provide a longer value for {error.variable_name}"
```

### Validation Error with Context

```python
class ValidationError(TripWireError):
    def __init__(
        self,
        variable_name: str,
        value: Any,
        reason: str,
        expected: Optional[str] = None,
    ):
        self.variable_name = variable_name
        self.value = value
        self.reason = reason
        self.expected = expected

        message = f"Validation failed for {variable_name}: {reason}"
        if expected:
            message += f"\nExpected: {expected}"
        message += f"\nReceived: {value}"
```

### Type Coercion Error

```python
class TypeCoercionError(TripWireError):
    def __init__(
        self,
        variable_name: str,
        value: Any,
        target_type: type,
        original_error: Optional[Exception] = None,
    ):
        message = f"Cannot coerce {variable_name} to {target_type.__name__}: {value}"
        if original_error:
            message += f"\nReason: {original_error}"
```

## Error Collection Mode

```python
# Fail-fast mode (default) - stops at first error
env = TripWire(collect_errors=False)

# Collection mode - reports all errors at once
env = TripWire(collect_errors=True)
# After all requires(), errors are auto-raised via atexit
# Or manually: env.finalize()
```

## When to Use

- Always include context (variable name, actual value)
- Provide specific fix suggestions
- Use multi-validation for better UX

## Anti-Patterns

```python
# BAD: Generic error
raise ValueError("Invalid value")

# GOOD: Actionable error with context
raise ValidationError(
    variable_name="PORT",
    value=70000,
    reason="Out of range: must be >= 1 and <= 65535",
    expected="Integer between 1 and 65535"
)
```

## File References

- `src/tripwire/exceptions.py` - All exception classes
- `src/tripwire/core/tripwire_v2.py` - Error usage in TripWire
- `tests/test_exceptions.py` - Test examples
