# Plugin Architecture Pattern

## Description

TripWire uses a protocol-based plugin system for extensible environment sources (Vault, AWS Secrets Manager, Azure Key Vault, etc.).

## Implementation

### Primary Location
`src/tripwire/plugins/base.py`, `src/tripwire/plugins/registry.py`

### Core Components

```python
# PluginMetadata - immutable plugin information
@dataclass(frozen=True)
class PluginMetadata:
    name: str                    # Unique identifier (e.g., "vault")
    version: str                 # Semantic version
    author: str
    description: str
    homepage: str | None = None
    license: str | None = None
    min_tripwire_version: str = "0.10.0"
    tags: list[str] = field(default_factory=list)

# EnvSourcePlugin - protocol (structural typing)
class EnvSourcePlugin(Protocol):
    @property
    def metadata(self) -> PluginMetadata: ...

    def load(self) -> dict[str, str]: ...

    def validate_config(self, config: dict[str, Any]) -> bool: ...

# PluginInterface - abstract base class (optional)
class PluginInterface(ABC):
    def __init__(self, metadata: PluginMetadata):
        self._metadata = metadata

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    @abstractmethod
    def load(self) -> dict[str, str]: ...

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> bool: ...
```

### Usage Pattern (CORRECT)

```python
from tripwire import TripWire
from tripwire.plugins.sources import VaultEnvSource
from tripwire.core.loader import DotenvFileSource
from pathlib import Path

# Pattern 1: Pass sources directly (RECOMMENDED)
dotenv = DotenvFileSource(Path(".env"))
vault = VaultEnvSource(url="https://vault.example.com", token="hvs.xxx", path="myapp/config")

env = TripWire(sources=[dotenv, vault])  # Sources merge into os.environ
```

### Usage Pattern (WRONG)

```python
# ANTI-PATTERN: Passing EnvFileLoader to sources=
loader = EnvFileLoader([dotenv, vault])
env = TripWire(sources=[loader])  # ValueError!

# CORRECT alternative: Use loader= parameter
env = TripWire(loader=loader)
```

### Plugin Implementation Example

```python
class VaultEnvSource(PluginInterface):
    def __init__(self, url: str, token: str, mount_point: str = "secret", path: str = ""):
        metadata = PluginMetadata(
            name="vault",
            version="1.0.0",
            author="TripWire Team",
            description="HashiCorp Vault integration"
        )
        super().__init__(metadata)
        self.url = url
        self.token = token
        self.mount_point = mount_point
        self.path = path

    def load(self) -> dict[str, str]:
        # Fetch secrets from Vault
        # Return as key-value dict
        return {"DATABASE_URL": "postgresql://..."}

    def validate_config(self, config: dict[str, Any]) -> bool:
        required = ["url", "token"]
        return all(key in config for key in required)
```

### Multi-Source Loading

```python
# Sources MERGE into os.environ (not replace)
# Later sources override overlapping keys
# Left-to-right priority (last = highest)

env = TripWire(sources=[
    DotenvFileSource(Path(".env")),           # Base config
    DotenvFileSource(Path(".env.local")),     # Local overrides
    VaultEnvSource(...),                       # Cloud secrets (highest priority)
])
```

### Plugin Discovery

```python
# Automatic discovery from entry points
TripWire.discover_plugins()

# Then use registered plugins
from tripwire.plugins import PluginRegistry
VaultPlugin = PluginRegistry.get_plugin("vault")
```

## When to Use

- Integrating with secret managers (Vault, AWS, Azure)
- Custom environment sources
- Separating credential loading from application code

## Adding New Plugins

1. Extend `PluginInterface` in `plugins/sources/`
2. Implement `load()` and `validate_config()`
3. Add plugin metadata
4. Handle errors with `PluginAPIError`, `PluginValidationError`
5. Add tests

## Security Considerations

- Never hardcode credentials
- HTTPS required for cloud services
- Never log secrets in error messages
- Use `PluginSandbox` for untrusted plugins

## File References

- `src/tripwire/plugins/base.py` - Protocol and base class
- `src/tripwire/plugins/registry.py` - Plugin registry
- `src/tripwire/plugins/errors.py` - Plugin-specific errors
- `src/tripwire/plugins/sources/` - Built-in plugin implementations
- `src/tripwire/core/loader.py` - EnvFileLoader, DotenvFileSource
