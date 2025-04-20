#! /bin/bash

# Create python environment
python -m venv venv

# Activate the python environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Initialized the project"

