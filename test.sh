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
        echo "  cmd: \"$cmd\""
        echo "  output  : $output"
        echo "  expected: $expected"
    else
        echo "[ PASS ] $testnum $description"
    fi
}

# Test to see if exit code of cmd (arg 1) is 1
# arg 2: optional documentation
# arg 3: optionally set to 0 if want expected to not be an error
test-error() {
    testnum=$[ $testnum + 1]

    cmd=$1
    description=${2-""}

    eval $cmd >/dev/null
    output=$(echo $?)

    if [[ $output != ${3-"1"} ]]
    then
        echo "[ FAIL ] $testnum $description"
        echo "  output  : $output"
        echo "  expected: ${3-'1'}"
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
    
    # Argument parsing
    # Acceptable
    test-error "$py modify-color.py -h +10 000000" "arg success" 0
    test-error "$py modify-color.py -s +10% 000000" "arg success" 0
    test-error "$py modify-color.py -b -10 000000" "arg success" 0
    test-error "$py modify-color.py --hue -10% 000000" "arg success" 0
    test-error "$py modify-color.py --saturation 10 000000" "arg success" 0
    test-error "$py modify-color.py --brightness 10% 000000" "arg success" 0
    test-error "$py modify-color.py --red +10 000000" "arg success" 0
    test-error "$py modify-color.py --green +10 000000" "arg success" 0
    test-error "$py modify-color.py --blue +10 000000" "arg success" 0
    test-error "$py modify-color.py --red +10 --blue -10 --green +10% 000000" "arg success" 0

    # Not acceptable
    test-error "$py modify-color.py --out x  000000" "arg error"
    test-error "$py modify-color.py --out --in hsv  000000" "arg error"
    test-error "$py modify-color.py -h ++10  000000" "arg error"
    test-error "$py modify-color.py -h +10%%  000000" "arg error"
    test-error "$py modify-color.py -h +a  000000" "arg error"
    test-error "$py modify-color.py -hx +a  000000" "arg error"

    # Hex conversion
    test "$py modify-color.py --out rgb_float '#0077ff'" "0.0,0.47,1.0" "valid hex conversion"
    test-error "$py modify-color.py '#0077ffaa'" "invalid hex length"
    test-error "$py modify-color.py '#00rr00'" "invalid hex chars"

    # Self conversions
    test "$py modify-color.py 0a7b29" "#0A7B29" "hex converts to self"
    test "$py modify-color.py --in hsb --out hsb 100,20,30" "100,20,30" "hsb converts to self"
    test "$py modify-color.py --in rgb --out rgb 100,20,30" "100,20,30" "rgb converts to self"
    test "$py modify-color.py --in rgb_float --out rgb_float 0.1,0.2,0.3" "0.1,0.2,0.3" "rgb_float converts to self"
    test "$py modify-color.py --in hsb_float --out hsb_float 0.1,0.2,0.3" "0.1,0.2,0.3" "hsb_float converts to self"

    # Equivalence conversion
    test "$py modify-color.py --out rgb_float 194E2A" "0.1,0.31,0.16" "hex -> rgb_float"
    test "$py modify-color.py --out hsb 194E2A" "139,68,31" "hex -> hsb"

    # Normalize
    test "$py modify-color.py --in rgb_float 1.0,0,0" "#FF0000" "normalize test"

    # Test setting
    test "$py modify-color.py --in hsb --out hsb --hue 200 --saturation 50 --brightness 50 0,0,0" "200,50,50" "hsb set"
}

run-tests python2
run-tests python3
