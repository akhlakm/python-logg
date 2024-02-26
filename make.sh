#!/usr/bin/env bash

publish() {
    # Run tests
    pytest || exit 1

    # Bump the version number.
    grep version pyproject.toml
    VERSION=$(sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml)
    VERSION=$(python -c "v='$VERSION'.split('.');print('%s.%s.%d' %(v[0], v[1], int(v[2])+1))")
    echo "   >>>"
    sed -i "s/\(version = \"\)[^\"]*\"/\1$VERSION\"/" pyproject.toml
    sed -i "s/\(__version__ = \"\)[^\"]*\"/\1$VERSION\"/" pylogg/__init__.py
    grep version pyproject.toml

    # Add to git and push.
    git add pyproject.toml pylogg/__init__.py
    git commit -m "Bump to v$VERSION"
    git push

    # Create a new git tag using the pyproject.toml version
    # and push the tag to origin.
    version=$(sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml)
    git tag v$version && git push origin v$version

    echo "OK"
}

prepare() {
    pre-commit run --all-files
}

"$@"
