#!/usr/bin/env bash
# Refresh the vendored ONAP CommonEventFormat schema.
#
# Usage: ./scripts/vendor-schema.sh [ref]
#   ref   Git ref (branch / tag / SHA) of onap/dcaegen2-collectors-ves to pull
#         the schema from. Defaults to 'master'.
#
# After running, manually diff the result and bump the project minor version
# if the schema changed.

set -euo pipefail

REF="${1:-master}"
REPO="onap/dcaegen2-collectors-ves"
SCHEMA_PATH="etc/CommonEventFormat_30.2.1_ONAP.json"

OUT="src/pytest_ves/schemas/CommonEventFormat_30.2.1_ONAP.json"

echo ">>> Fetching ${SCHEMA_PATH} @ ${REF} from ${REPO}"
TMPFILE="$(mktemp)"
trap 'rm -f "${TMPFILE}"' EXIT
curl -fsSL \
  "https://raw.githubusercontent.com/${REPO}/${REF}/${SCHEMA_PATH}" \
  -o "${TMPFILE}"

# Validate the payload is well-formed JSON before overwriting the tree copy.
# Prefer `jq` if installed; fall back to Python's json module.
if command -v jq >/dev/null 2>&1; then
  jq -e '.["$schema"] | test("draft-04")' "${TMPFILE}" >/dev/null \
    || { echo "ERROR: downloaded file is not a draft-04 JSON schema"; exit 1; }
else
  python -c "import json, sys; json.load(open(sys.argv[1], encoding='utf-8'))" "${TMPFILE}" \
    || { echo "ERROR: downloaded file is not valid JSON"; exit 1; }
fi

mv "${TMPFILE}" "${OUT}"
trap - EXIT

# Record provenance using jq when available, fall back to grep/cut.
if command -v jq >/dev/null 2>&1; then
  SHA="$(curl -fsSL "https://api.github.com/repos/${REPO}/commits/${REF}" | jq -r .sha)"
else
  SHA="$(curl -fsSL "https://api.github.com/repos/${REPO}/commits/${REF}" \
        | grep -m1 '"sha":' | cut -d'"' -f4)"
fi

echo ">>> Pinned to commit ${SHA}"
echo "${SHA}" > src/pytest_ves/schemas/.provenance-sha

echo ">>> Diff against HEAD (git diff -- ${OUT}):"
git --no-pager diff -- "${OUT}" || true

cat <<EOF
>>> Done.

Next steps:
  1. If the diff is non-empty, update NOTICE with the new SHA.
  2. Bump project version in pyproject.toml (minor for schema updates).
  3. Add a CHANGELOG.md entry under [Unreleased] describing the upstream change.
  4. git add -A && git commit -m "chore(schema): refresh from onap@${SHA:0:7}"
EOF
