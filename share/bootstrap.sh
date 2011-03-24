#!/bin/bash
VERSION="0.1"

BASEURL=$1

TMPDIR=$(mktemp --tmpdir -d bootstrap.XXXXX)

DISTRO="Unknown"
MODULES=""

# Support Functions
function gotemp {
    cd ${TMPDIR}
}

function runfile {
    $(head -n 1 $1 | cut -d\! -f 2) $1 ${BASEURL} ${DISTRO}
}

function detect {
    gotemp

    wget -q -O ${TMPDIR}/detect.py ${BASEURL}/detect.py
    DISTRO=$(runfile detect.py)
}

function getscript {
    gotemp

    wget -q -O ${TMPDIR}/$1 ${BASEURL}/${DISTRO}/$1
    if [[ $? -ne 0 ]]
    then
        exit $?
    fi
}

function getmodules {
    # Active is a single line separated with spaces of the scripts to run in
    # order from the distro dir
    MODULES=$(wget -q -O - ${BASEURL}/${DISTRO}/active)
}

function provision {
    detect
    getmodules

    for MOD in ${MODULES}
    do
        gotemp
        getscript ${MOD}
        runfile ${MOD}
    done
}

function have_prog {
    [ -x "$(which $1)" ]
}

function ensure_wget {
    if have_prog wget; then echo "wget found"
    elif have_prog yum; then yum install -y wget
    elif have_prog apt-get; then apt-get install  -y wget
    elif have_prog zypper; then zyper install -y wget
    else
        echo "Cannot install wget!"
        exit 2
    fi
}

ensure_wget
provision

