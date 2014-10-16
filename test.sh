#!/bin/bash
testnum=0

test () {
    testnum=$[ $testnum + 1]

    cmd=$1
    expected=$2
    output=$(eval $cmd)
    if [[ $expected != $output ]]
    then
        echo "[ FAIL ] $testnum"
        echo "  output  : $output"
        echo "  expected: $expected"
    else
        echo "[ PASS ] $testnum"
    fi
}

