# Chain of Responsibility Validation Pattern

## Description

TripWire uses the Chain of Responsibility pattern for validation, composing multiple validation rules into a pipeline that processes values sequentially.

## Implementation

### Primary Location
`src/tripwire/core/validation_orchestrator.py`

### Core Components

```python
# ValidationContext - carries data through the chain
@dataclass
class ValidationContext:
    name: str           # Variable name
    raw_value: str      # Original string from environment
    coerced_value: Any  # Value after type coercion
    expected_type: type # Target type

# ValidationRule - abstract base for all rules
class ValidationRule(ABC):
    def __init__(self, error_message: Optional[str] = None):
        self.error_message = error_message

    @abstractmethod
    def validate(self, context: ValidationContext) -> None:
        """Raises ValidationError if validation fails."""
        pass

# ValidationOrchestrator - manages the chain
class ValidationOrchestrator:
    def __init__(self, collect_errors: bool = False):
        self.rules: List[ValidationRule] = []
        self.collect_errors = collect_errors

    def add_rule(self, rule: ValidationRule) -> ValidationOrchestrator:
        """Builder pattern for fluent API."""
        self.rules.append(rule)
        return self

    def validate(self, context: ValidationContext) -> None:
        """Execute all rules in order."""
        for rule in self.rules:
            rule.validate(context)
```

### Built-in Validation Rules

| Rule | Purpose | Parameters |
|------|---------|------------|
| `FormatValidationRule` | email, url, postgresql, uuid, ipv4 | `format_name` |
| `PatternValidationRule` | Regex matching | `pattern` |
| `ChoicesValidationRule` | Enum/whitelist values | `choices` |
| `RangeValidationRule` | Numeric bounds | `min_val`, `max_val` |
| `LengthValidationRule` | String length bounds | `min_length`, `max_length` |
| `CustomValidationRule` | User function | `validator: Callable[[Any], bool]` |
| `URLComponentsValidationRule` | URL structure | `protocols`, `allowed_ports`, etc. |
| `DateTimeValidationRule` | Datetime format/range | `formats`, `require_timezone`, etc. |

### Pipeline Construction (Builder Pattern)

```python
# From TripWire._build_validation_pipeline()
def _build_validation_pipeline(
    self,
    format: Optional[str],
    pattern: Optional[str],
    choices: Optional[List[str]],
    min_val: Optional[Union[int, float]],
    max_val: Optional[Union[int, float]],
    min_length: Optional[int],
    max_length: Optional[int],
    validator: Optional[ValidatorFunc],
    error_message: Optional[str],
) -> ValidationOrchestrator:
    orchestrator = ValidationOrchestrator()

    # Rules added in specific order for consistent error reporting
    if format:
        orchestrator.add_rule(FormatValidationRule(format, error_message))
    if pattern:
        orchestrator.add_rule(PatternValidationRule(pattern, error_message))
    if choices:
        orchestrator.add_rule(ChoicesValidationRule(choices, error_message))
    if min_val is not None or max_val is not None:
        orchestrator.add_rule(RangeValidationRule(min_val, max_val, error_message))
    if min_length is not None or max_length is not None:
        orchestrator.add_rule(LengthValidationRule(min_length, max_length, error_message))
    if validator:
        orchestrator.add_rule(CustomValidationRule(validator, error_message))

    return orchestrator
```

## When to Use

- Adding new validation types: Create new `ValidationRule` subclass
- Custom validation logic: Use `CustomValidationRule` with a function
- Complex validation: Combine multiple rules in sequence

## Adding New Validators

```python
# 1. Create rule class
class MyCustomRule(ValidationRule):
    def validate(self, context: ValidationContext) -> None:
        if not my_validation_logic(context.coerced_value):
            raise ValidationError(
                variable_name=context.name,
                value=context.coerced_value,
                reason="My validation failed"
            )

# 2. Add to pipeline builder in TripWire._build_validation_pipeline()
```

## File References

- `src/tripwire/core/validation_orchestrator.py` - Full implementation
- `src/tripwire/core/tripwire_v2.py` - Pipeline usage (lines 996-1060)
- `src/tripwire/validation.py` - Underlying validation functions
