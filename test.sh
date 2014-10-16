#!/bin/bash
testnum=0

# test to see if output of cmd (arg 1) matches expected output (arg 2)
# arg 3: optional test description
test () {
    testnum=$[ $testnum + 1]

    cmd=$1
    expected=$2
    output=$(eval $cmd | tr -d '\n')
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

# Test to see if exit code of cmd (arg 1) is 1
# arg 2: optional documentation
test-error() {
    testnum=$[ $testnum + 1]

    cmd=$1
    description=${2-""}

    eval $cmd >/dev/null

    if [[ $? != "1" ]]
    then
        echo "[ FAIL ] $testnum $description"
        echo "  output  : 0"
        echo "  expected: 1"
    else
        echo "[ PASS ] $testnum $description"
    fi
}

# Execute all tests over specified python version (arg 2)
run-tests () {
    defaultpython="python3"
    pythonversion="${1-$defaultpython}"
    py="/bin/$pythonversion"

    testnum=0

    echo "-------------- $pythonversion --------------"

    # Docs
    test "$py modify-color.py | head -1" "modify-color" "docs"

    # Hex conversion
    test "$py modify-color.py '#0077ff'" "(0.0, 0.467, 1.0)" "valid hex conversion"
    test-error "$py modify-color.py '#0077ffaa'" "invalid hex length"
    test-error "$py modify-color.py '#00rr00'" "invalid hex chars"
    test "$py modify-color.py '#0a7b29'" "#0A7B29" "hex converts to self"
}

run-tests python2
run-tests python3
