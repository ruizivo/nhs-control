# runs 2 commands simultaneously:
./nhsupsserver & # first application
P1=$!
python3 -u nhstelnet.py & # second application
P2=$!
wait $P1 $P2