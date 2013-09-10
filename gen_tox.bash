#!/usr/bin/env bash
# ############################################################################
#
# Generator configuration for the "tox"
#
# ############################################################################

# <id>:<version>
PYTHON_DICT=( "py26:python2.6" 
	 		  "py27:python2.7" 
			  "py32:python3.2" 
			  "py33:python3.3" 
			  "pypy:pypy" )

# <id>:<version>
DJANGO_DICT=( "django14:1.4.x" 
			  "django15:1.5.x" 
			  "django16:1.6.x" 
			  "djangolatest:latest" )

# <id>:<version>
PYMONEYED_DICT=( "pm04:0.4"
				 "pmlatest:latest"
				 "pmpython3:python3" )

# condition[<id> <id> ...]: skip[<id> <id> ...]
TOX_SKIP_CONDITIONS=( "pmlatest pm04: py32 py33" 
					  "py33 py32: django14")

function test_conditions() {
	for condition_item in "${TOX_SKIP_CONDITIONS[@]}"
	do
		for condition in ${condition_item%%:*}
		do
			for skip in ${condition_item##*:}
			do 
				for var in "$@"
				do
					
					if [ "$condition" == "$var" ]
					then
						for vars in "$@"
						do
							if [ "$skip" == "$vars" ]
							then
								echo "Condition '$condition' skip '$skip'"
								return
							fi							
						done
					fi 
				done
			done
		done
	done
}

function get_tox() {

cat <<EOF
[tox]
envlist =
EOF

for python_item in "${PYTHON_DICT[@]}"
do

python_id="${python_item%%:*}"
python_ver="${python_item##*:}"

for django_item in "${DJANGO_DICT[@]}"
do

django_id="${django_item%%:*}"
django_ver="${django_item##*:}"

for pymoneyed_item in "${PYMONEYED_DICT[@]}"
do

pymoneyed_id="${pymoneyed_item%%:*}"
pymoneyed_ver="${pymoneyed_item##*:}"

if [ "$(test_conditions $python_id $django_id $pymoneyed_id)" ]
then
	continue
fi

echo "    $python_id-$django_id-$pymoneyed_id,"

done
done
done

}

function get_config() {
cat <<EOF

[testenv]
commands=
    pip install -e .[tests] -q --log={envlogdir}/pip-extra-install.log
    {envpython} runtests.py {posargs}

[django]
1.4.x  = Django>=1.4,<1.5
1.5.x  = Django>=1.5,<1.6
1.6.x  = https://github.com/django/django/archive/stable/1.6.x.zip
latest = https://github.com/django/django/tarball/master

[pymoneyed]
0.4    = py-moneyed>=0.4,<0.5
latest = https://github.com/limist/py-moneyed/archive/master.zip
python3 = https://github.com/fizista/py-moneyed/archive/python3.zip

EOF
}

function gen_testenv() {
PYTHON_ID=$1
PYTHON_VER=$2

DJANGO_ID=$3
DJANGO_VER=$4

PYMONEYED_ID=$5
PYMONEYED_VER=$6

cat <<EOF

[testenv:$PYTHON_ID-$DJANGO_ID-$PYMONEYED_ID]
basepython=$PYTHON_VER
deps=
    {[django]$DJANGO_VER}
    {[pymoneyed]$PYMONEYED_VER}
    
EOF
}



get_tox

get_config

for python_item in "${PYTHON_DICT[@]}"
do

python_id="${python_item%%:*}"
python_ver="${python_item##*:}"

cat <<EOF

# ############################################################################
# Python $python_ver
# ############################################################################

EOF

for django_item in "${DJANGO_DICT[@]}"
do

django_id="${django_item%%:*}"
django_ver="${django_item##*:}"

cat <<EOF

###### django $django_ver

EOF

for pymoneyed_item in "${PYMONEYED_DICT[@]}"
do



	
	pymoneyed_id="${pymoneyed_item%%:*}"
	pymoneyed_ver="${pymoneyed_item##*:}"

	if [ "$(test_conditions $python_id $django_id $pymoneyed_id)" ]
	then
		continue
	fi

	gen_testenv "$python_id" "$python_ver" "$django_id" "$django_ver" "$pymoneyed_id" "$pymoneyed_ver"
	
done
done
done
