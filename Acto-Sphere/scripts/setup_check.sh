#!/bin/bash

echo "=== Acto-Sphere Environment Check ==="

check_cmd() {
    if command -v $1 &> /dev/null; then
        echo " [OK] $1 is installed ($( $1 --version | head -n 1 ))"
    else
        echo " [RR] $1 is MISSING. Please install it."
    fi
}

check_cmd docker
check_cmd python3
check_cmd node
check_cmd go
check_cmd dotnet
check_cmd ruby

if [ -f "Acto-Sphere/py/requirements.txt" ]; then
    echo " [OK] Python requirements found."
else
    echo " [RR] requirements.txt missing."
fi

echo "=== Check Complete ==="
