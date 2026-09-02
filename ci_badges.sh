#!/bin/bash
pip install anybadge
mkdir -p public/quality/

exit_status=false
args_list=()
for arg in $*
do
    if [ "$arg" == "--exit-status" ]; then
        exit_status=true
    else
        args_list+=($arg)
    fi
done

# Black badge
black . --check --diff > .blackout 2>&1
black_status=$?
if [[ $black_status -eq 0 ]]; then
    BLACK_RESULT=passing
else
    BLACK_RESULT=failing
fi
anybadge -l black -v $BLACK_RESULT -f ./public/quality/black.svg passing=green failing=red

# Isort badge
isort -c --diff . > .isortout 2>&1
isort_status=$?
if [[ $isort_status -eq 0 ]]; then
    ISORT_RESULT=passing
else
    ISORT_RESULT=failing
fi
anybadge -l isort -v $ISORT_RESULT -f ./public/quality/isort.svg passing=green failing=red

# Pylint badge
pylint "${args_list[@]}" -f text --exit-zero > .pylintout 2> .pylinterror
anybadge -l pylint -v $(cat .pylintout | tail -n2 | awk '{print $7}' | cut -d"/" -f1) -f ./public/quality/pylint.svg 5=red 8=orange 9=yellow 9.5=yellowgreen 10=green

# Bandit badge
BANDIT_RESULT=failing
bandit --configfile pyproject.toml --output .banditout --format txt --recursive . 2> .banditerror
BANDIT_STATUS=$?
if [[ $BANDIT_STATUS -eq 0 ]]; then
    BANDIT_RESULT=passing
elif [[ $BANDIT_STATUS -eq 1 ]]; then
    BANDIT_RESULT="low severity"
    MEDIUM_SEVERITY=$(grep -o 'Medium: [0-9]*' .banditout | awk '{print $2}' | head -n 1)
    HIGH_SEVERITY=$(grep -o 'High: [0-9]*' .banditout | awk '{print $2}' | head -n 1)

    if [[ HIGH_SEVERITY -gt 0 ]]; then
        BANDIT_RESULT="high severity"
    elif [[ MEDIUM_SEVERITY -gt 0 ]]; then
        BANDIT_RESULT="medium severity"
    fi
fi
anybadge -l bandit -v "$BANDIT_RESULT" -f ./public/quality/bandit.svg failing=red "high severity"=orange "medium severity"=yellow "low severity"=yellow_green passing=green

# Building htmls
echo "<pre>" > ./public/quality/black.html
cat .blackout >> ./public/quality/black.html
echo "</pre>" >> ./public/quality/black.html

echo "<pre>" > ./public/quality/isort.html
cat .isortout >> ./public/quality/isort.html
echo "</pre>" >> ./public/quality/isort.html

echo "<pre>" > ./public/quality/pylint.html
cat .pylinterror >> ./public/quality/pylint.html
cat .pylintout >> ./public/quality/pylint.html
echo "</pre>" >> ./public/quality/pylint.html

echo "<pre>" > ./public/quality/bandit.html
cat .banditerror >> ./public/quality/bandit.html
cat .banditout >> ./public/quality/bandit.html
echo "</pre>" >> ./public/quality/bandit.html

# print quality tools output
cat .blackout
cat .isortout
cat .pylinterror
cat .pylintout
echo "--------------------------------------------------"
echo "Bandit security check:"
cat .banditerror
cat .banditout

if $exit_status; then
    if [ "$isort_status" -ne "0" ] || [ "$black_status" -ne "0" ]; then
        exit -1
    fi
fi
