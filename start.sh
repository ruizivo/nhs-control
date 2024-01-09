#!/bin/bash

# ./nhsupsserver.sh start
./nhsupsserver

# Waiting nhs telnet start
while ! nc -z localhost 2000; do
    echo "Waiting for nhs telnet start..."
    sleep 1
done

# Starting the service
echo "Starting the service in python that reads data from the UPS and sends it to mqtt..."
# python3 -u nhstelnet.py
