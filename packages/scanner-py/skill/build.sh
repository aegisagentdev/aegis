#!/usr/bin/env bash
# Rebuild the two downloadable Agent Skill archives.
#
#   skill/aegis-skill.zip          thin  — SKILL.md only, installs `pip install aegis`
#   skill/aegis-skill-offline.zip  offline — bundles the wheels for an airgapped install
#
# The archives are release artifacts (attached to a GitHub Release), not committed to git.
# Run from the repo root:  bash skill/build.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VERSION="$(python3 -c 'import tomllib,pathlib;print(tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["version"])')"
echo "building skill archives for aegis $VERSION"

# --- thin ---
( cd "$HERE/thin" && rm -f ../aegis-skill.zip && zip -qr ../aegis-skill.zip aegis )
echo "  -> aegis-skill.zip"

# --- offline: vendor aegis + deps, incl. pydantic-core across platforms/pythons ---
W="$HERE/offline/aegis/wheels"
rm -rf "$W" && mkdir -p "$W"
pip download "aegis==$VERSION" -d "$W" >/dev/null
for p in manylinux2014_x86_64 manylinux2014_aarch64 macosx_11_0_arm64 macosx_10_12_x86_64 win_amd64; do
  for v in 310 311 312 313; do
    pip download pydantic-core --only-binary=:all: --platform "$p" --python-version "$v" -d "$W" >/dev/null 2>&1 || true
  done
done
( cd "$HERE/offline" && rm -f ../aegis-skill-offline.zip && zip -qr ../aegis-skill-offline.zip aegis )
echo "  -> aegis-skill-offline.zip"

echo "done. attach both zips to the GitHub Release for $VERSION."
