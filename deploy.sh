#!/bin/bash
#
# This script will deploy the assembled zip of the application and its signed
# XML file to the remote repository.

if [ ! -f target/*.zip ]; then
    echo "ERROR: .zip missing."
    exit 1
elif [ ! -f target/*.zip.xml ]; then
    echo "ERROR: .zip.xml missing."
    exit 1
fi

scp target/*zip* jakewharton_repository@r.jakewharton.com:/home/jakewharton_repository/r.jakewharton.com/staging/
ssh jakewharton_repository@r.jakewharton.com "/usr/bin/env python /home/jakewharton_repository/staging.py"
