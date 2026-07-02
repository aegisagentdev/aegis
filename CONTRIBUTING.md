# Contributing to Hood Trade

## Setup

```bash
git clone https://github.com/hooddev/hoodtrade
cd hoodtrade
python -m venv .venv && source .venv/bin/activate
pip install -e '.[ai,dev]'
```

## Running checks

```bash
ruff check src tests        # lint
ruff format --check src tests  # formatting
pytest -q                   # tests
```

## Adding a new check

1. Create a file in `src/hoodtrade/checks/` (e.g. `mycheck.py`).
2. Define a class with an `id` attribute and an `async def run(self, ctx: Context) -> list[CheckResult]` method.
3. Register it in `src/hoodtrade/checks/__init__.py` inside `default_checks()`.
4. Add tests in `tests/test_mycheck.py`.

### Check conventions

- A check **must not raise** on ordinary on-chain conditions. Missing data, reverts, unexpected formats — those are *findings* (return a `CheckResult` with an appropriate severity), not exceptions. Only infra failures (RPC timeout, network error) should propagate; the engine catches and logs them.
- Use `ctx.cache` to share state between checks. Contract checks run first and populate `token_code_size`, `token_symbol`, etc. Downstream checks read these and short-circuit if the upstream data is absent.
- Pick a stable, uppercase `id` like `CONTRACT-HONEYPOT` or `POOL-DEPTH`. This id appears in JSON output and is used for filtering.

### Severity guide

| Severity | When to use | Score range |
|----------|-------------|-------------|
| `OK`     | Check passed, no issue | 0 |
| `INFO`   | Informational, no action needed | 0-5 |
| `WARN`   | Notable risk, user should be aware | 10-25 |
| `DANGER` | Blocking issue, likely unsafe | 40-100 |

## Pull requests

- One feature or fix per PR.
- All tests must pass (`pytest -q`).
- All lint must pass (`ruff check src tests`).
- Include tests for new checks.
