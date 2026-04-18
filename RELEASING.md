# Releasing pytest-ves

## Audience

Project maintainers (currently: thc1006). External contributors do not
need to read this file; see `CONTRIBUTING.md` instead.

## Pre-flight

- [ ] Local `main` is up to date with `origin/main`
- [ ] GitHub Actions CI green on the current tip
- [ ] `uv sync --all-extras && uv run coverage run -m pytest && uv run coverage report` reports 100%
- [ ] `uv run ruff check . && uv run mypy src` both clean
- [ ] `uv run pytest -m integration tests/integration/test_http_roundtrip.py` green (11 tests)

## Version scheme

[Semantic Versioning](https://semver.org/) 2.0.0.

| Change | Bump |
|---|---|
| New builder / fixture, new public helper, additive schema bump | minor |
| Bug fix, test-only, doc-only, CI-only | patch |
| Remove / rename public API, change fixture name, drop Python version | major |
| Bump vendored ONAP schema to a breaking upstream revision | major |
| Bump vendored ONAP schema to an additive upstream revision | minor |

## Release steps

1. **Bump both version strings** (they must match; a pre-commit hook
   guards drift):
   - `pyproject.toml` → `[project] version = "X.Y.Z"`
   - `src/pytest_ves/__init__.py` → `__version__ = "X.Y.Z"`

2. **Cut the CHANGELOG section**: move everything from `## [Unreleased]`
   into a new `## [X.Y.Z] — YYYY-MM-DD` section. Keep the empty
   `## [Unreleased]` header.

3. **Rebuild once locally** to catch last-minute packaging issues:
   ```bash
   rm -rf dist/
   uv build
   python -c "import zipfile; z = zipfile.ZipFile('dist/pytest_ves-X.Y.Z-py3-none-any.whl'); print(sorted(z.namelist()))"
   ```
   Sanity-check that the wheel includes:
   - `pytest_ves/schemas/CommonEventFormat_30.2.1_ONAP.json`
   - `pytest_ves-X.Y.Z.dist-info/licenses/LICENSE`
   - `pytest_ves-X.Y.Z.dist-info/licenses/NOTICE`

4. **Commit the release** (no AI signature in commit message; see
   user feedback in memory):
   ```bash
   git add pyproject.toml src/pytest_ves/__init__.py CHANGELOG.md
   git commit -m "release: X.Y.Z"
   ```

5. **Tag** (signed where possible):
   ```bash
   git tag -a vX.Y.Z -m "pytest-ves X.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```

6. **Create the GitHub Release**:
   ```bash
   gh release create vX.Y.Z --notes-file <(awk '/^## \[X.Y.Z\]/,/^## \[/' CHANGELOG.md | head -n -1)
   ```
   This fires `publish.yml` → `gate` (runs full CI) → `publish` (`uv build`
   + PyPI trusted publishing).

## PyPI trusted publishing setup (one-off)

Before the first release, configure trusted publishing on PyPI so no
API token is stored anywhere:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with:
   - PyPI project name: `pytest-ves`
   - Owner: `thc1006`
   - Repository: `pytest-ves`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. On GitHub → Settings → Environments → create `pypi` env.
4. Verify `publish.yml` uses `pypa/gh-action-pypi-publish@release/v1`
   with no explicit password (it reads the OIDC token automatically).

## Post-release

- [ ] Check https://pypi.org/project/pytest-ves/X.Y.Z/ renders readme cleanly.
- [ ] `pip install pytest-ves==X.Y.Z` in a fresh venv as a smoke test.
- [ ] Update `../o-ran-smo-ves-dashboards/scripts/requirements.txt` to
      un-comment `pytest-ves>=X.Y,<Y+1` if this is the first PyPI
      release, then commit that change in the dashboards repo.

## Hotfix from an older minor line

Unlikely for a project this small but documented for completeness:

```bash
git checkout -b release/X.Y vX.Y.0         # branch from the tag
# ...apply fix, bump PATCH, update changelog...
git tag vX.Y.Z
git push origin release/X.Y vX.Y.Z
```

A hotfix release goes through the same `publish.yml` gate as a normal
release.

## Yanking a bad release

If a release is published with a defect that makes it dangerous to use:

1. `pip` users: `gh release edit vX.Y.Z --notes "YANKED: <reason>"`
2. PyPI: go to https://pypi.org/project/pytest-ves/X.Y.Z/ and yank the
   release (admins only).
3. Publish X.Y.(Z+1) with the fix.
4. Add a `### Yanked` section to the offending CHANGELOG entry.

## Why there is no `release.sh`

Because release decisions should be human-paced: a script can encode
the mechanical steps but not "should we actually ship this today".
The checklist above is the minimal thing a human goes through.
