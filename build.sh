#!/bin/bash

function run {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "$1 errored with $status" >&2
        exit $status
    fi
    return $status
}

ACCESS_KEY=$1
SECRET_KEY=$2
PAYERSACCOUNTS=$3
BUCKET=$4

# Add Drill to PATH
export PATH=/opt/drill/bin:$PATH

TEMPDIR="/media/ephemeral0/"
#TEMPDIR="/temp/"

~/DBRConsolidation/buildchartdata.py ${ACCESS_KEY} ${SECRET_KEY} ${PAYERSACCOUNTS} ${BUCKET}
