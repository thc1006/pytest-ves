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
curl -fsSL \
  "https://raw.githubusercontent.com/${REPO}/${REF}/${SCHEMA_PATH}" \
  -o "${OUT}"

# Record provenance.
SHA="$(curl -fsSL "https://api.github.com/repos/${REPO}/commits/${REF}" \
      | grep -m1 '"sha":' | cut -d'"' -f4)"

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
