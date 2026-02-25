# Type Inference Pattern

## Description

TripWire automatically infers variable types from Python type annotations using a pluggable strategy pattern, eliminating the need for explicit `type=` parameters.

## Implementation

### Primary Location
`src/tripwire/core/inference.py` - `TypeInferenceEngine`, `FrameInspectionStrategy`

### Code Example

```python
from tripwire import env

# Type inference from annotation - no need for type= parameter
PORT: int = env.require("PORT")  # Infers int from annotation
DEBUG: bool = env.require("DEBUG")  # Infers bool from annotation
TIMEOUT: float = env.require("TIMEOUT")  # Infers float from annotation

# Explicit type (override inference)
PORT = env.require("PORT", type=int)

# Type inference with validation constraints
MAX_CONNECTIONS: int = env.require("MAX_CONNECTIONS", min_val=1, max_val=1000)
```

### Strategy Pattern Implementation

```python
# From src/tripwire/core/inference.py

class TypeInferenceStrategy(ABC):
    """Abstract base class for type inference strategies."""

    @abstractmethod
    def infer(self, caller_frame: FrameType) -> Optional[type]:
        """Infer type from caller's context."""
        pass

class FrameInspectionStrategy(TypeInferenceStrategy):
    """Infer type by inspecting caller's frame for annotations."""

    def infer(self, caller_frame: FrameType) -> Optional[type]:
        # Inspects the calling frame's annotations
        # Returns the annotated type or None
        pass

class TypeInferenceEngine:
    """Engine that uses pluggable strategies for type inference."""

    def __init__(self, strategy: TypeInferenceStrategy):
        self._strategy = strategy

    def infer_or_default(
        self,
        explicit_type: Optional[type] = None,
        default: type = str
    ) -> type:
        """Infer type or return default."""
        if explicit_type:
            return explicit_type

        # Try strategy-based inference
        inferred = self._strategy.infer(...)
        return inferred if inferred else default
```

### How It Works

1. When `require()` is called, the inference engine examines the calling frame
2. It looks for type annotations on the variable being assigned
3. If found, uses that type for coercion; otherwise falls back to `str`

## When to Use

- Always prefer type annotations over explicit `type=` parameter
- Use explicit `type=` only when annotations aren't possible (e.g., dynamic contexts)

## Dependency Injection for Testing

```python
# Mock inference engine for testing
mock_engine = MockInferenceEngine(returns=int)
env = TripWire(
    inference_engine=mock_engine,
    auto_load=False
)
```

## File References

- `src/tripwire/core/inference.py` - Full implementation
- `src/tripwire/core/tripwire_v2.py` - Usage in TripWire class (lines 196-200, 332-333)
- `tests/test_type_inference.py` - Test examples