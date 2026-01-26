#!/bin/bash

# Usage:
# ./ci-infra/helpers/run-tests.sh outdir test-names.txt
# Input:
# - outdir will contain status/progress file, and log files of individual tests
# - (optional) test-names.txt contains integration tests to be run, one per line.
# Output:
# - logs are one test per file, in outdir/log-timestamp/
# - list of succeded/failed tests are in outdir/status.txt
# If line starts with:
# - PEND (or contains just test name), test will be run
# - SKIP means skip this test
# - OK or ERR are set after test is run

set -ue
# set -v
OUTD1="$1"
TNFILE="${2:-}"

TIME=$(date +%Y%m%d-%H%M%S)
TSTATUS="$OUTD1/status.txt"

[ ! -d "$OUTD1" ] && mkdir "$OUTD1"
OUTD2="$OUTD1/log-$TIME"
mkdir "$OUTD2"

if [ ! -f "$TSTATUS" ]
then
    if [ -n "$TNFILE" ]
    then
        /bin/cp "$TNFILE" "$TSTATUS"
    else
        /bin/ls tests/integration/targets/ >"$TSTATUS"
    fi
fi
sed -i 's/^[a-z]/PEND\t&/' "$TSTATUS"
if grep -q -v -E "^(OK|ERR|PEND|SKIP)" "$TSTATUS"
then
    echo "ERROR file content $TSTATUS" 1>&2
    exit 1
fi
/bin/cp "$TSTATUS" "$OUTD2/status.txt"

TEST_NAMES=$(grep "^PEND" "$TSTATUS" | awk '{print $2}')
# shellcheck disable=SC2086
echo "Pending tests: "$TEST_NAMES
# shellcheck disable=SC2086
TEST_COUNT=$(echo $TEST_NAMES | wc -w)
ii=0
for TN in $TEST_NAMES
do
    echo "Running test $TN ($ii/$TEST_COUNT)"
    (
        echo ansible-test integration --local "$TN"
        echo "======================"
        set +e
        ansible-test integration --local "$TN"
        RET=$?
        set -e
        if [ "$RET" == "0" ]
        then
            status="OK"
        else
            status="ERR"
        fi
        sed -i "s/^PEND\t$TN\$/$status\t$TN/" "$TSTATUS"
        echo "======================"
        echo "RESULT $status"
    ) >"$OUTD2/$TN.log" 2>&1
    res=$(grep $'\t'"$TN\$" "$TSTATUS" | awk '{print $1}')
    echo "  result $res $TN"
    ii=$((ii+1))
done
