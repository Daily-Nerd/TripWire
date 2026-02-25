# CLI Command Structure Pattern

## Description

TripWire uses Click for CLI and Rich for terminal output, with a modular command architecture organized by feature area.

## Implementation

### Primary Location
`src/tripwire/cli/__init__.py`, `src/tripwire/cli/commands/`

### Directory Structure

```
src/tripwire/cli/
  __init__.py           # Main entry point, command registration
  __main__.py           # python -m tripwire.cli entry
  progress.py           # Progress tracking utilities
  commands/
    __init__.py         # Command exports
    init.py             # tripwire init
    generate.py         # tripwire generate
    check.py            # tripwire check
    validate.py         # tripwire validate
    sync.py             # tripwire sync
    docs.py             # tripwire docs
    diff.py             # tripwire diff
    analyze.py          # tripwire analyze
    install_hooks.py    # tripwire install-hooks
    schema.py           # tripwire schema (command group)
    security/           # tripwire security (command group)
      __init__.py
      scan.py           # tripwire security scan
      audit.py          # tripwire security audit
    plugin/             # tripwire plugin (command group)
      ...
  formatters/           # Output formatters
  templates/            # Output templates
  utils/                # Shared utilities
```

### Main CLI Entry Point

```python
# src/tripwire/cli/__init__.py
import click
from tripwire.branding import LOGO_SIMPLE

@click.group()
@click.option("--help", "-h", is_flag=True, ...)
@click.version_option(version="0.13.1", prog_name="tripwire", ...)
def main() -> None:
    """TripWire - Catch config errors before they explode."""
    pass

# Register individual commands
main.add_command(init.init)
main.add_command(generate.generate)
main.add_command(check.check)
# ...

# Register command groups
main.add_command(schema.schema)
main.add_command(security)
main.add_command(plugin)
```

### Command Group Pattern

```python
# src/tripwire/cli/commands/security/__init__.py
import click

@click.group(name="security")
def security() -> None:
    """Security management: scan for secrets, audit git history."""
    pass

# Add subcommands
security.add_command(scan.scan)
security.add_command(audit.audit)
```

### Individual Command Pattern

```python
# src/tripwire/cli/commands/check.py
import click
from rich.console import Console

console = Console()

@click.command()
@click.option("--path", "-p", default=".", help="Path to scan")
@click.option("--strict", is_flag=True, help="Enable strict mode")
def check(path: str, strict: bool) -> None:
    """Check environment configuration."""
    # Implementation using rich for output
    console.print("[green]Check passed![/green]")
```

### Rich Output Pattern

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Simple status
console.print("[green]Success[/green]")
console.print("[red]Error:[/red] Something went wrong")

# Tables
table = Table(title="Environment Variables")
table.add_column("Name", style="cyan")
table.add_column("Value", style="green")
table.add_row("DATABASE_URL", "postgresql://...")
console.print(table)

# Panels
console.print(Panel("Important information", title="Notice"))
```

### Schema Command Naming Convention

```python
# from-* commands CREATE schemas from sources
# tripwire schema from-code     # Extract from Python code
# tripwire schema from-env      # Extract from .env.example

# to-* commands EXPORT schemas to formats
# tripwire schema to-env        # Generate .env.example
# tripwire schema to-docs       # Generate documentation
```

### Progress Tracking

```python
from tripwire.cli.progress import audit_progress

# Use for long-running operations (>2s)
with audit_progress(total_commits=100) as tracker:
    for i in range(100):
        tracker.update(commits_processed=i+1, secrets_found=0)
    tracker.finish(total_secrets=5)
```

## When to Use

- Adding new CLI commands: Create in `commands/` directory
- Adding command groups: Create subdirectory with `__init__.py`
- Schema transformations: Follow `from-*/to-*` naming

## Adding New Commands

1. Create file in `src/tripwire/cli/commands/`
2. Use `@click.command()` decorator
3. Use `rich` library for output
4. Register in `src/tripwire/cli/__init__.py`

```python
# commands/mycommand.py
import click
from rich.console import Console

console = Console()

@click.command()
@click.option("--flag", is_flag=True, help="Some flag")
def mycommand(flag: bool) -> None:
    """My command description."""
    console.print("Hello!")

# __init__.py
main.add_command(mycommand.mycommand)
```

## File References

- `src/tripwire/cli/__init__.py` - Main CLI entry
- `src/tripwire/cli/commands/` - All commands
- `src/tripwire/cli/progress.py` - Progress utilities
- `src/tripwire/branding.py` - ASCII logos
