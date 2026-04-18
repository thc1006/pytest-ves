# Contributing to pytest-ves

Thanks for considering a contribution. This project is small and opinionated;
please read the relevant ADRs under `docs/adr/` before proposing architectural
changes.

## Local development

```bash
# install uv if needed: https://docs.astral.sh/uv/
uv sync --all-extras

# One-time: wire pre-commit hooks so stale-formatting / version-drift /
# large-file / trailing-whitespace regressions cannot land in main.
# The hook set is defined in .pre-commit-config.yaml (12 hooks, including
# a local version-drift guard between pyproject.toml and __init__.py).
uv run pre-commit install

# Fast inner loop (no coverage):
uv run pytest
uv run ruff check .
uv run mypy src

# With coverage (use `coverage run -m pytest`, NOT `pytest --cov=...`, because
# pytest_ves itself is a pytest plugin; pytest-cov otherwise activates too
# late and misses our import-time code).
uv run coverage run -m pytest
uv run coverage report -m
uv run coverage html   # open htmlcov/index.html

# Run the full hook suite on the whole tree (what CI will do):
uv run pre-commit run --all-files
```

## Running integration tests

Integration tests are opt-in and split into two layers:

```bash
# HTTP wire-format round-trip (stdlib http.server; NO Docker required):
uv run pytest -m integration tests/integration/test_http_roundtrip.py

# Real ONAP VES Collector (requires Docker + ~1 GB image pull):
docker pull onap/org.onap.dcaegen2.collectors.ves.vescollector:1.8.0
RUN_ONAP_INTEGRATION=1 uv run pytest -m integration tests/integration/test_onap_collector.py

# Both at once (includes optional gated tests):
RUN_ONAP_INTEGRATION=1 uv run pytest -m integration
```

The default `uv run pytest` invocation excludes `-m integration` so the
inner dev loop stays fast and Docker-free. CI runs the HTTP round-trip
layer on every push; the ONAP collector layer is a manual / scheduled
workflow because the image is large and slow to pull.

## Updating the vendored VES schema

The schema is pinned by commit SHA in `NOTICE` and tracked in
`docs/schema-provenance.md`. To update:

```bash
./scripts/vendor-schema.sh
```

The script fetches the canonical schema, diffs against the existing copy, and
updates the SHA. Bump the minor version of `pytest-ves` when the schema
changes.

## Adding a new VES domain fixture

1. Add a TypedDict to `src/pytest_ves/types.py` mirroring the domain's field
   block in the ONAP schema.
2. Add a Builder dataclass to `src/pytest_ves/builders.py` with sensible
   defaults for required fields.
3. Register a pytest fixture in `src/pytest_ves/plugin.py`.
4. Cover it in `tests/test_<domain>_event.py`, asserting at minimum:
   `validate_ves(event)` passes, and the returned dict's
   `event.commonEventHeader.domain` equals the expected string.

## Not in scope

- Vendoring 3GPP / ETSI schemas (see ADR-002).
- Java / Robot Framework ports.
- Runtime VES delivery over HTTP/Kafka (that's a sister project; see
  `docs/adr/ADR-001-design.md` §12 for the CLI roadmap).

## Code of Conduct

This project follows the
[Contributor Covenant](https://www.contributor-covenant.org/) 2.1. Be kind.
