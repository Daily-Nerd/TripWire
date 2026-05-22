#!/usr/bin/env python3
"""Validate TripWire release automation configuration.

This script checks the Release Please state/config and the release workflows for
regressions that have previously broken publishing.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib  # type: ignore[no-redef]

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate workflow YAML") from exc

ROOT = Path(__file__).resolve().parents[2]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
HEX_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    print(f"::error::{message}")
    raise SystemExit(1)


def load_json(relative: str) -> object:
    path = ROOT / relative
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001 - show actionable file context
        fail(f"{relative} is not valid JSON: {exc}")


def load_yaml(relative: str) -> object:
    path = ROOT / relative
    try:
        return yaml.safe_load(path.read_text())
    except Exception as exc:  # noqa: BLE001 - show actionable file context
        fail(f"{relative} is not valid YAML: {exc}")


def load_text(relative: str) -> str:
    return (ROOT / relative).read_text()


def validate_manifest() -> str:
    manifest = load_json(".release-please-manifest.json")
    if not isinstance(manifest, dict):
        fail(".release-please-manifest.json must be a JSON object")
    if set(manifest) != {"."}:
        fail(".release-please-manifest.json must contain exactly one key: '.'")
    version = manifest["."]
    if not isinstance(version, str) or not VERSION_RE.match(version):
        fail(".release-please-manifest.json value for '.' must be a version string like 1.2.3")
    return version


def validate_pyproject(version: str) -> None:
    pyproject = tomllib.loads(load_text("pyproject.toml"))
    project = pyproject.get("project")
    if not isinstance(project, dict):
        fail("pyproject.toml is missing [project]")
    pyproject_version = project.get("version")
    if pyproject_version != version:
        fail(
            "pyproject.toml version must match .release-please-manifest.json: "
            f"{pyproject_version!r} != {version!r}"
        )


def validate_release_please_config() -> None:
    config = load_json("release-please-config.json")
    if not isinstance(config, dict):
        fail("release-please-config.json must be a JSON object")

    if config.get("bootstrap-sha") == "":
        fail('release-please-config.json must not contain empty "bootstrap-sha"')
    for sha_key in ("bootstrap-sha", "last-release-sha"):
        value = config.get(sha_key)
        if value is not None and (not isinstance(value, str) or not HEX_SHA_RE.match(value)):
            fail(f'release-please-config.json field "{sha_key}" must be a full 40-character SHA')

    packages = config.get("packages")
    if not isinstance(packages, dict) or set(packages) != {"."}:
        fail('release-please-config.json must contain packages with exactly the root package "."')

    package = packages["."]
    if not isinstance(package, dict):
        fail('release-please-config.json packages["."] must be an object')
    expected = {
        "package-name": "tripwire-py",
        "release-type": "python",
        "changelog-path": "CHANGELOG.md",
    }
    for key, expected_value in expected.items():
        if package.get(key) != expected_value:
            fail(f'release-please-config.json packages["."].{key} must be {expected_value!r}')

    extra_files = package.get("extra-files")
    if not isinstance(extra_files, list) or "pyproject.toml" not in extra_files:
        fail('release-please-config.json packages["."].extra-files must include pyproject.toml')


def validate_workflows() -> None:
    release_workflow = load_yaml(".github/workflows/release.yml")
    release_please_workflow = load_yaml(".github/workflows/release-please.yml")
    if not isinstance(release_workflow, dict):
        fail("release.yml must parse to a YAML object")
    if not isinstance(release_please_workflow, dict):
        fail("release-please.yml must parse to a YAML object")

    release_text = load_text(".github/workflows/release.yml")
    release_please_text = load_text(".github/workflows/release-please.yml")

    required_release_snippets = [
        "Install from Test PyPI in clean environment",
        "python -m venv .venv_test",
        "--index-url https://test.pypi.org/simple/",
        "Resolve release tag",
        "fail_on_unmatched_files: true",
        "dist/*.whl",
        "dist/*.tar.gz",
    ]
    for snippet in required_release_snippets:
        if snippet not in release_text:
            fail(f"release.yml missing required release hardening snippet: {snippet}")

    forbidden_release_please_snippets = [
        "uses: ./.github/workflows/release.yml",
        "tripwire-release:",
        "steps.release.outputs.tag_name ||",
    ]
    for snippet in forbidden_release_please_snippets:
        if snippet in release_please_text:
            fail(f"release-please.yml must not directly call release.yml or use stale output expression: {snippet}")



def main() -> None:
    version = validate_manifest()
    validate_pyproject(version)
    validate_release_please_config()
    validate_workflows()
    print(f"✓ release configuration is valid for tripwire-py {version}")


if __name__ == "__main__":
    main()
