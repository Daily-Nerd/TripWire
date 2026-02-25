# Testing Patterns

## Description

TripWire uses pytest with fixtures for test isolation, monkeypatching for environment manipulation, and specific patterns for testing env var behavior.

## Implementation

### Primary Location
`tests/conftest.py`, `tests/test_*.py`

### Core Fixtures

```python
# tests/conftest.py

@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Save and restore environment state after test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def temp_env_file(tmp_path: Path) -> Path:
    """Create temporary .env file path."""
    return tmp_path / ".env"

@pytest.fixture
def sample_env_file(temp_env_file: Path) -> Path:
    """Create .env file with test data."""
    content = """API_KEY=test-api-key-12345
DATABASE_URL=postgresql://user:pass@localhost:5432/testdb
DEBUG=true
PORT=8000
"""
    temp_env_file.write_text(content)
    return temp_env_file

@pytest.fixture
def sample_env_vars(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set sample environment variables."""
    env_vars = {
        "API_KEY": "test-api-key-12345",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
        "DEBUG": "true",
        "PORT": "8000",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def isolated_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Clear ALL environment variables for isolated testing."""
    for key in list(os.environ.keys()):
        monkeypatch.delenv(key, raising=False)
    yield
```

### Testing TripWire Require

```python
class TestRequireMethod:
    def test_require_existing_variable(self, sample_env_vars: dict[str, str]) -> None:
        """Test requiring an existing environment variable."""
        result = env.require("API_KEY")
        assert result == "test-api-key-12345"

    def test_require_missing_variable(self, isolated_env: None) -> None:
        """Test requiring a missing variable raises error."""
        # Use fail-fast mode for testing error behavior
        env_test = TripWireV2(collect_errors=False, auto_load=False)
        with pytest.raises(MissingVariableError, match="MISSING_VAR"):
            env_test.require("MISSING_VAR")

    def test_require_with_default(self, isolated_env: None) -> None:
        """Test default value when variable missing."""
        result = env.require("MISSING_VAR", default="default-value")
        assert result == "default-value"
```

### Testing Type Coercion

```python
class TestTypeCoercion:
    def test_coerce_to_int(self, sample_env_vars: dict[str, str]) -> None:
        result = env.require("PORT", type=int)
        assert result == 8000
        assert isinstance(result, int)

    def test_coerce_to_bool_true(self, sample_env_vars: dict[str, str]) -> None:
        result = env.require("DEBUG", type=bool)
        assert result is True

    def test_invalid_coercion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env_test = TripWireV2(collect_errors=False, auto_load=False)
        monkeypatch.setenv("PORT", "not-a-number")
        with pytest.raises(TypeCoercionError):
            env_test.require("PORT", type=int)
```

### Testing Validation

```python
class TestFormatValidation:
    def test_email_format_valid(self, sample_env_vars: dict[str, str]) -> None:
        result = env.require("ADMIN_EMAIL", format="email")
        assert result == "admin@example.com"

    def test_email_format_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        env_test = TripWireV2(collect_errors=False, auto_load=False)
        monkeypatch.setenv("ADMIN_EMAIL", "not-an-email")
        with pytest.raises(ValidationError, match="Invalid format"):
            env_test.require("ADMIN_EMAIL", format="email")
```

### Testing with Temporary Files

```python
def test_load_env_file(tmp_path: Path) -> None:
    """Test loading from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("MY_VAR=my_value\n")

    instance = TripWire(env_file=env_file, auto_load=True)
    assert instance._loaded_files == [env_file]
```

### Testing CLI Commands

```python
from click.testing import CliRunner
from tripwire.cli import main

def test_cli_check():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--path", "."])
    assert result.exit_code == 0
```

### Test Organization

```
tests/
  conftest.py              # Shared fixtures
  test_core.py             # TripWire class tests
  test_validation.py       # Validation function tests
  test_type_inference.py   # Type inference tests
  test_secrets.py          # Secret detection tests
  test_cli_commands.py     # CLI tests
  test_integration.py      # Integration tests
  cli/                     # CLI-specific tests
  core/                    # Core component tests
  plugins/                 # Plugin tests
```

## Key Patterns

1. **Use `isolated_env` for missing variable tests** - Ensures clean environment
2. **Use `monkeypatch.setenv()` for setting test values** - Auto-cleanup
3. **Create fresh `TripWireV2` instances** - Avoids global state pollution
4. **Use `collect_errors=False` for testing error behavior** - Fail-fast mode
5. **Use `tmp_path` for file-based tests** - Auto-cleanup

## Anti-Patterns

```python
# BAD: Modifying os.environ directly
os.environ["MY_VAR"] = "value"  # Won't be cleaned up

# GOOD: Use monkeypatch
monkeypatch.setenv("MY_VAR", "value")  # Auto-cleanup
```

## File References

- `tests/conftest.py` - Shared fixtures
- `tests/test_core.py` - Core tests
- `tests/test_validation.py` - Validation tests
- `tests/README_TEST_GUIDE.md` - Test documentation
