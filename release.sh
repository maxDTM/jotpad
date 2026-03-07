#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./release.sh 1.2.0"
    exit 1
fi

VERSION=$1

# Python source
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/jotpad/__init__.py

# Man page
sed -i "s/\"jotpad [0-9.]*\"/\"jotpad $VERSION\"/" man/jotpad.1

# PKGBUILD
sed -i "s/pkgver=.*/pkgver=$VERSION/" packaging/arch/PKGBUILD
sed -i "s/pkgrel=.*/pkgrel=1/" packaging/arch/PKGBUILD

# RPM spec
sed -i "s/^Version:.*/Version:        $VERSION/" packaging/rpm/jotpad.spec

# Debian changelog (adds new entry)
sed -i "1s/.*/jotpad ($VERSION-1) unstable; urgency=medium/" packaging/debian/changelog

echo "Updated to $VERSION"
echo ""
echo "Next steps:"
echo "  git add -A"
echo "  git commit -m \"v$VERSION\""
echo "  git tag v$VERSION"
echo "  git push origin master && git push origin v$VERSION"
echo "  Then update AUR with new sha256sum"