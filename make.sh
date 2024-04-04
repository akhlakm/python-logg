#!/bin/bash
#           ---   Makefile like bash script for development    ---
#  --- Source this script in your terminal to set up the dev environment ---
#      --- Execute the script to see a list of available commands ---
# ------------------------------------------------------------------------------

[[ -n $MKWD ]] || export MKWD=$(echo $(command cd $(dirname '$0'); pwd))
CONDAENV=python-logg

## -----------------------------------------------------------------------------

if [[ $(basename "${0}") != "make.sh" ]]; then
    # Script sourced, load or create condaenv
    if ! conda activate $CONDAENV; then
        # Create a conda environment.
        echo "Setting up $CONDAENV conda environment."
        conda create -n $CONDAENV python=3.10 || return 10
        conda activate $CONDAENV || return 11
    fi

    export PYTHONPATH=$MKWD

    alias cdmk="cd $MKWD/"
    alias mk="$MKWD/make.sh"
    echo "Environment set up. You can now use 'mk' to execute this script."

    return 0
fi


publish() {
    # Run tests
    pytest || exit 1

    # Bump the version number.
    grep version pylogg/__init__.py
    VERSION=$(sed -n 's/version = "\(.*\)"/\1/p' pylogg/__init__.py)
    VERSION=$(python -c "v='$VERSION'.split('.');print('%s.%s.%d' %(v[0], v[1], int(v[2])+1))")
    echo "   >>>"
    sed -i "s/\(__version__ = \"\)[^\"]*\"/\1$VERSION\"/" pylogg/__init__.py
    grep version pylogg/__init__.py

    # Add to git and push.
    git add pylogg/__init__.py
    git commit -m "Bump to v$VERSION"
    git push

    # Create a new git tag using the pylogg/__init__.py version
    # and push the tag to origin.
    version=$(sed -n 's/version = "\(.*\)"/\1/p' pylogg/__init__.py)
    git tag v$version && git push origin v$version

    echo "OK"
}

setup() {
    pip install -e .[dev]
    pip install pytest pre-commit
    pre-commit install
}

prepare() {
    pre-commit run --all-files
    pytest
}

test() {
    pytest -vv -s
}

## EXECUTE OR SHOW USAGE.
## -----------------------------------------------------------------------------
if [[ "$#" -lt 1 ]]; then
    echo -e "\nUSAGE:  mk <command> [options ...]"
    echo -e "\tSource this script to setup the terminal environment."
    echo -e "\nAvailable commands:"
    echo -e "------------------------------------------------------------------"
    echo -e "    setup      Install dev requirements and setup env."
    echo
    echo -e "    prepare    Prepare files to publish."
    echo
    echo -e "    test       Run tests."
    echo
    echo -e "    publish    Publish current changes as a new version."
    echo
else
    cd $MKWD
    "$@"
fi
