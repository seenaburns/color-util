#!/bin/bash
testnum=0
EXEC="color-util"

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
        echo "  expected: ${3-1}"
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
    test "$py $EXEC | head -1" "color-util" "docs"
    
    # Argument parsing
    # Acceptable
    test-error "$py $EXEC -h +10 000000" "arg success" 0
    test-error "$py $EXEC -s +10% 000000" "arg success" 0
    test-error "$py $EXEC -b -10 000000" "arg success" 0
    test-error "$py $EXEC --hue -10% 000000" "arg success" 0
    test-error "$py $EXEC --saturation 10 000000" "arg success" 0
    test-error "$py $EXEC --brightness 10% 000000" "arg success" 0
    test-error "$py $EXEC --red +10 000000" "arg success" 0
    test-error "$py $EXEC --green +10 000000" "arg success" 0
    test-error "$py $EXEC --blue +10 000000" "arg success" 0
    test-error "$py $EXEC --red +10 --blue -10 --green +10% 000000" "arg success" 0

    # Not acceptable
    test-error "$py $EXEC --out x  000000" "arg error"
    test-error "$py $EXEC --out --in hsv  000000" "arg error"
    test-error "$py $EXEC -h ++10  000000" "arg error"
    test-error "$py $EXEC -h +10%%  000000" "arg error"
    test-error "$py $EXEC -h +a  000000" "arg error"
    test-error "$py $EXEC -hx +a  000000" "arg error"

    # Hex conversion
    test "$py $EXEC --out rgb_float '#0077ff'" "0.0,0.47,1.0" "valid hex conversion"
    test-error "$py $EXEC '#0077ffaa'" "invalid hex length"
    test-error "$py $EXEC '#00rr00'" "invalid hex chars"

    # Self conversions
    test "$py $EXEC 0a7b29" "#0A7B29" "hex converts to self"
    test "$py $EXEC --in hsb --out hsb 100,20,30" "100,20,30" "hsb converts to self"
    test "$py $EXEC --in rgb --out rgb 100,20,30" "100,20,30" "rgb converts to self"
    test "$py $EXEC --in rgb_float --out rgb_float 0.1,0.2,0.3" "0.1,0.2,0.3" "rgb_float converts to self"
    test "$py $EXEC --in hsb_float --out hsb_float 0.1,0.2,0.3" "0.1,0.2,0.3" "hsb_float converts to self"

    # Equivalence conversion
    test "$py $EXEC --out rgb_float 194E2A" "0.1,0.31,0.16" "hex -> rgb_float"
    test "$py $EXEC --out hsb 194E2A" "139,68,31" "hex -> hsb"

    # Normalize
    test "$py $EXEC --in rgb_float 1.0,0,0" "#FF0000" "normalize test"

    # Test setting
    test "$py $EXEC --in hsb --out hsb --hue 200 --saturation 50 --brightness 50 0,0,0" "200,50,50" "hsb set"
    test "$py $EXEC --in hsb --out hsb --hue +20 --saturation +50 --brightness -10 100,100,50" "120,100,40" "hsb set"
    test "$py $EXEC --in hsb --out hsb --hue +20% --saturation -50% --brightness 10% 100,100,50" "120,50,5" "hsb set"
    test "$py $EXEC --out rgb --red -50 --green 10% --blue 10 ff5522" "205,8,10" "rgb set"

    test-error "$py $EXEC --hue 200 --red 100 111111" "modify mode switch error"

    # Read from stdin
    test "echo '001122' | $py $EXEC --out rgb" "0,17,34" "read from stdin"
    test-error "echo '' | $py $EXEC --out rgb" "read from stdin"
    test "$py $EXEC 000000 --red 100 --green 150 --blue 50 | $py $EXEC --hue +10%" "#559632" "chaining"
}

run-tests python2
run-tests python3
