# runs 2 commands simultaneously:

./nhsupsserver & # your first application
P1=$!
python3 -u nhstelnet.py & # your second application
P2=$!
wait $P1 $P2