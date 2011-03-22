#!/bin/bash
VERSION="0.1"

BASEURL=$1
USER=$2
PASSWORD=$3

TMPDIR=$(mktemp --tmpdir -d bootstrap.XXXXX)

DISTRO="Unknown"
MODULES=""

# Support Functions
function gotemp {
    cd ${TMPDIR}
}

function runfile {
    $(head -n 1 $1 | cut -d\! -f 2) $1
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
    MODULES=$(wget -q -O - ${BASEURL}/${DISTRO}/active)
}

function provision {
    detect

    for MOD in ${MODULES}
    do
        gotemp
        getscript ${MOD}
        runfile ${MOD}
    done
}

provision

