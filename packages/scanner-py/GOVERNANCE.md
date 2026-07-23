# Governance

## Overview

Hood Trade is maintained by a small core team. This document describes how decisions are
made and how contributions are accepted.

## Decision Making

- **Minor changes** (bug fixes, typos, small improvements): merged by any maintainer after
  CI passes and a brief review.
- **New checks**: require one review from a maintainer. The review focuses on false-positive
  rate, severity calibration, and test coverage.
- **Architecture changes** (engine logic, verdict model, AI layer): require discussion in
  an issue before implementation. At least one maintainer must approve.
- **Breaking changes** (config format, CLI flags, output schema): announced in an issue,
  documented in CHANGELOG, and shipped in a minor version bump.

## Roles

| Role | Responsibilities |
|------|-----------------|
| **Maintainer** | Merge PRs, triage issues, release versions, set direction |
| **Contributor** | Open PRs, report issues, propose checks |
| **User** | Use the tool, report bugs, request features |

## Release Process

1. All tests pass (`pytest -q`)
2. All lint passes (`ruff check src tests`)
3. CHANGELOG updated with version entry
4. Version bumped in `pyproject.toml` and `__init__.py`
5. Tag created: `git tag v0.X.0`
6. Push tag to trigger release workflow (when applicable)

## Conflict Resolution

If maintainers disagree, the decision defaults to the project lead after 48 hours of
discussion. The goal is rough consensus, not unanimity.
