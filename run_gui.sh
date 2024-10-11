#!/bin/bash

# Verifica se python3 está disponível, caso contrário usa python
if command -v python3 &>/dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

$PYTHON -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt-get update
sudo apt-get install python3-tk
$PYTHON main.py --gui