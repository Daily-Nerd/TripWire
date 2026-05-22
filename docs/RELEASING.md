# Releasing TripWire

TripWire uses Release Please to prepare release pull requests and a separate GitHub Actions release workflow to build, verify, and publish distributions.

## Normal release flow

1. Merge regular feature and fix PRs into `main` using conventional commit style commit titles.
2. Release Please runs on pushes to `main` and opens or updates a release PR.
3. Review the release PR changelog and version bump.
4. Merge the release PR when ready.
5. Release Please creates the `vX.Y.Z` tag and GitHub Release.
6. The `Release` workflow runs for the tag and publishes:
   - build artifacts,
   - TestPyPI package,
   - PyPI package via Trusted Publishing,
   - GitHub Release assets.

## Conventional commits

Release Please calculates SemVer bumps from conventional commit messages:

- `fix: ...` -> patch release
- `feat: ...` -> minor release
- `type(scope)!: ...` or a `BREAKING CHANGE:` footer -> major release

Use neutral public wording in commit titles and PR descriptions. Do not include private operational context, credentials, internal hostnames, or personal details in public repo content.

## Release Please files

### `.release-please-manifest.json`

This file is Release Please version state only. Keep the shape simple:

```json
{
  ".": "1.2.3"
}
```

Do not put package metadata, changelog settings, release type, or component names in this file.

### `release-please-config.json`

This file contains Release Please configuration, including:

- package name,
- release type,
- changelog sections,
- extra version files,
- release search/bootstrap controls.

Do not leave `"bootstrap-sha": ""` in the config. If Release Please needs to be anchored after a recovery release, use a real full commit SHA and document why in the PR.

## Required GitHub configuration

### Secrets

- `TEST_PYPI_API_TOKEN`: API token used by the TestPyPI upload step.

### Environments

- `pypi`: GitHub environment used by the PyPI Trusted Publishing job.

### PyPI Trusted Publishing

The PyPI project must trust this repository/workflow for OIDC publishing. The release workflow requests `id-token: write` only for the PyPI publish job.

## Recovery: release PR merged but package was not published

Use this flow if a release PR was merged but the publish workflow failed before PyPI upload.

1. Fix the release workflow in a normal PR.
2. Merge the fix.
3. Manually dispatch the `Release` workflow:
   - `version`: the intended release version, for example `1.0.2`
   - `prerelease`: `false` for normal releases
4. Watch all release jobs until complete.
5. Verify:
   - `https://pypi.org/project/tripwire-py/<version>/` exists,
   - `https://github.com/Daily-Nerd/TripWire/releases/tag/v<version>` exists,
   - release assets include wheel and sdist.

The release workflow intentionally allows manual runs for existing tags so a failed release can be recovered after a workflow-only fix.

## Recovery: Release Please opens a wrong major-version PR

If Release Please opens a PR that backfills old history and proposes an unintended major version:

1. Do not merge the PR.
2. Check whether the version in `.release-please-manifest.json` has a matching Git tag and GitHub Release.
3. If the previous release was recovered manually, anchor Release Please to the recovered release PR/tag point using `last-release-sha` in `release-please-config.json`.
4. Close the incorrect Release Please PR.
5. Let Release Please run again on the next push to `main`.

## Manual verification commands

Check PyPI:

```bash
curl -fsSL https://pypi.org/pypi/tripwire-py/<version>/json >/dev/null
```

Check GitHub release:

```bash
curl -fsSL \
  -H "Authorization: Bearer ${GH_TOKEN:-${GITHUB_TOKEN:-}}" \
  -H 'Accept: application/vnd.github+json' \
  https://api.github.com/repos/Daily-Nerd/TripWire/releases/tags/v<version> >/dev/null
```

Check Release Please state:

```bash
python .github/scripts/validate_release_config.py
```
