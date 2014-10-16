#!/bin/bash
testnum=0

test () {
    testnum=$[ $testnum + 1]

    cmd=$1
    expected=$2
    output=$(eval $cmd)
    description=${3-""}
    if [[ $expected != $output ]]
    then
        echo "[ FAIL ] $testnum $description"
        echo "  output  : $output"
        echo "  expected: $expected"
    else
        echo "[ PASS ] $testnum $description"
    fi
}

run-tests () {
    defaultpython="python3"
    pythonversion="${1-$defaultpython}"
    py="/bin/$pythonversion"

    testnum=0

    echo "-------------- $pythonversion --------------"

    # Docs
    test "$py modify-color.py | head -1" "modify-color" "docs"
}

run-tests python2
run-tests python3
