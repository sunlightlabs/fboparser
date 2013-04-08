#!/bin/bash

function process_file () {
    f="${1}"
    f1=$(basename $f)
    [ -e json_files/${f1}.json ] && rm json_files/${f1}.json
    [ -e json_files/${f1}.errors ] && rm json_files/${f1}.errors
    [ -e freq_files/${f1}.errors ] && rm freq_files/${f1}.errors
    [ -e freq_files/${f1}.txt ] && rm freq_files/${f1}.txt
    (  cd fboparser && \
         ../fbo-lexer/bin/python3.3 -m fbo_raw.parser ../${f} \
            > ../json_files/${f1}.json \
            2> ../json_files/${f1}.errors
    )
    (  cd fboparser && \
         ../fbo-lexer/bin/python3.3 -m fbo_raw.importer ../${f} \
            > ../freq_files/${f1}.txt \
            2> ../freq_files/${f1}.errors
    )
    wait
    [ ! -s json_files/${f1}.errors ] && rm json_files/${f1}.errors
    [ ! -s freq_files/${f1}.errors ] && rm freq_files/${f1}.errors
    echo Done
    ls -1sh json_files/${f1}*
    ls -1sh freq_files/${f1}*
}

if [ "$#" -gt 0 ]; then
    while [ "$#" -gt 0 ]; do
        echo "${1}"
        process_file "${1}"
        shift
    done
else
    for f in raw_files/FBOFeed2*; do
        echo -n ${f}...
        process_file "${f}"
    done
fi
