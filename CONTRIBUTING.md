# Contributing to pytest-ves

Thanks for considering a contribution. This project is small and opinionated;
please read the relevant ADRs under `docs/adr/` before proposing architectural
changes.

## Local development

```bash
# install uv if needed: https://docs.astral.sh/uv/
uv sync --all-extras
uv run pytest
uv run ruff check .
uv run mypy src
```

## Running integration tests

Integration tests require Docker and are opt-in:

```bash
uv run pytest -m integration
```

They exercise the vendored schema against a live ONAP VES Collector container
and the O-RAN SC `smo-ves` stack. See `tests/integration/README.md`.

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
