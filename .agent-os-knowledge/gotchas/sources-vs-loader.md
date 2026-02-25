# Gotcha: sources= vs loader= Parameter

## Severity: Critical

## The Problem

A common API misuse is passing an `EnvFileLoader` instance to the `sources=` parameter instead of the `loader=` parameter.

## Wrong Usage

```python
from tripwire import TripWire
from tripwire.core.loader import EnvFileLoader, DotenvFileSource
from tripwire.plugins.sources import VaultEnvSource

# Create sources
dotenv = DotenvFileSource(Path(".env"))
vault = VaultEnvSource(url="...", token="...")

# WRONG: Wrapping in EnvFileLoader and passing to sources=
loader = EnvFileLoader([dotenv, vault])
env = TripWire(sources=[loader])  # ValueError!
```

## Error Message

```
ValueError: Invalid sources parameter: item at index 0 is an EnvFileLoader,
but sources= expects a list of EnvSource instances.

COMMON MISTAKE:
  loader = EnvFileLoader([source1, source2])
  env = TripWire(sources=[loader])  # Wrong!

CORRECT USAGE (choose one pattern):
  Pattern 1: Pass sources directly
     env = TripWire(sources=[source1, source2])

  Pattern 2: Pass loader to loader= parameter
     loader = EnvFileLoader([source1, source2])
     env = TripWire(loader=loader)
```

## Correct Usage

### Pattern 1: Direct Sources (RECOMMENDED)

```python
from tripwire import TripWire
from tripwire.core.loader import DotenvFileSource
from tripwire.plugins.sources import VaultEnvSource
from pathlib import Path

# Create sources
dotenv = DotenvFileSource(Path(".env"))
vault = VaultEnvSource(url="...", token="...")

# CORRECT: Pass sources directly
env = TripWire(sources=[dotenv, vault])
```

### Pattern 2: Custom Loader (Advanced)

```python
from tripwire import TripWire
from tripwire.core.loader import EnvFileLoader, DotenvFileSource
from pathlib import Path

# Create loader with sources
loader = EnvFileLoader([
    DotenvFileSource(Path(".env")),
    DotenvFileSource(Path(".env.local"))
])

# CORRECT: Pass loader to loader= parameter
env = TripWire(loader=loader)
```

## Why This Happens

- `sources=` expects `List[EnvSource]` (individual source instances)
- `loader=` expects `EnvFileLoader` (which wraps multiple sources)
- TripWire creates an EnvFileLoader internally when you use `sources=`
- Passing EnvFileLoader to `sources=` is double-wrapping

## Detection

TripWire validates at initialization and raises `ValueError` with clear guidance.

## File References

- `src/tripwire/core/tripwire_v2.py` - Validation code (lines 209-225)
- `src/tripwire/core/loader.py` - EnvFileLoader, EnvSource types