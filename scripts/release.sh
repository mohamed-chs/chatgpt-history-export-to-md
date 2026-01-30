#!/bin/bash
set -e

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Error: Version argument missing."
  echo "Usage: $0 <version>"
  exit 1
fi

echo "Releasing version $VERSION..."

# 1. Update version
# This updates pyproject.toml and uv.lock
uv version "$VERSION"

# 2. Commit changes
git add pyproject.toml uv.lock
git commit -m "chore: bump version to $VERSION"

# 3. Create and push tag
git tag "v$VERSION"
git push
git push origin "v$VERSION"

echo "Release v$VERSION initiated!"
