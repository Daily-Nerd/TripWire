# Secret Detection Pattern

## Description

TripWire detects secrets and sensitive data in environment files and git history using pattern-based detection (45+ patterns) and entropy analysis.

## Implementation

### Primary Location
`src/tripwire/secrets.py`

### Core Components

```python
# SecretType enum - categories of secrets
class SecretType(Enum):
    AWS_ACCESS_KEY = "AWS Access Key"
    GITHUB_TOKEN = "GitHub Token"
    STRIPE_KEY = "Stripe API Key"
    # ... 45+ types including:
    # - Cloud providers (AWS, Azure, GCP, DigitalOcean)
    # - CI/CD (CircleCI, Travis, Jenkins, GitLab)
    # - Communication (Slack, Discord, Twilio)
    # - Payments (Stripe, PayPal, Square)
    # - Package managers (NPM, PyPI)
    # - Generic credentials

# SecretPattern - detection configuration
@dataclass
class SecretPattern:
    secret_type: SecretType
    pattern: str          # Regex pattern
    description: str
    severity: str         # critical, high, medium, low
    min_entropy: Optional[float] = None

# SecretMatch - detection result
@dataclass
class SecretMatch:
    secret_type: SecretType
    variable_name: str
    value: str            # Redacted
    line_number: int
    severity: str
    recommendation: str   # Actionable remediation steps
```

### Detection Pipeline

```python
def detect_secrets_in_value(variable_name: str, value: str, line_number: int = 0) -> List[SecretMatch]:
    """Detection order:
    1. Skip placeholders
    2. Context-aware detection (AWS secrets, etc.)
    3. Platform-specific pattern matching (pre-compiled)
    4. Generic credential detection (if no platform pattern matched)
    5. High-entropy detection (fallback)
    """
```

### Pattern Examples

```python
# AWS Access Key
SecretPattern(
    secret_type=SecretType.AWS_ACCESS_KEY,
    pattern=r"AKIA[0-9A-Z]{16}",
    description="AWS Access Key ID",
    severity="critical",
)

# GitHub Token (with ReDoS protection)
SecretPattern(
    secret_type=SecretType.GITHUB_TOKEN,
    pattern=r"gh[pousr]_[0-9a-zA-Z]{36,255}",  # Upper bound prevents ReDoS
    description="GitHub Token",
    severity="critical",
)

# Generic credential detection
# Uses variable name context + entropy + character complexity
```

### Entropy-Based Detection

```python
def calculate_entropy(data: str) -> float:
    """Calculate Shannon entropy (0.0 to 8.0 for byte data)."""
    # Higher entropy = more randomness = likely secret

def is_high_entropy(value: str, threshold: float = 4.5) -> bool:
    """Check if value has high entropy (likely random/secret)."""
    # Ignores short values (<20 chars)
    # Ignores common placeholders
```

### Security Measures

```python
# Resource limits prevent DOS attacks
MAX_ENTROPY_STRING_LENGTH = 10_000  # 10KB max
MAX_SECRET_VALUE_LENGTH = 10_000    # 10KB max

# Pre-compiled patterns for performance (10-20x speedup)
_COMPILED_SECRET_PATTERNS = [
    (p.secret_type, re.compile(p.pattern, re.IGNORECASE | re.MULTILINE), ...)
    for p in SECRET_PATTERNS
]
```

### Value Redaction

```python
def redact_value(value: str, show_chars: int = 4) -> str:
    """Redact secret for safe display."""
    # "sk-1234567890abcdef" -> "sk-1...cdef"
```

## When to Use

- Pre-commit hooks: `tripwire security scan --strict`
- CI/CD pipelines: `tripwire security scan --depth 50`
- Security incidents: `tripwire security audit --all`

## Adding New Secret Patterns

1. Add `SecretType` enum in `secrets.py`
2. Create `SecretPattern` with regex
3. Add to `BUILTIN_PATTERNS` list
4. Add remediation recommendation to `get_recommendation()`
5. Add tests in `tests/test_secrets.py`

## File References

- `src/tripwire/secrets.py` - Full implementation (1111 lines)
- `src/tripwire/git_audit.py` - Git history scanning
- `src/tripwire/cli/commands/security/` - CLI commands
- `tests/test_secrets.py` - Test examples
