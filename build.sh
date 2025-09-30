#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data

# Set up data file if it doesn't exist
if [ ! -f data/financas.json ]; then
    echo '{"transacoes": [], "proximo_id": 1}' > data/financas.json
fi

# Make sure the app has write permissions
chmod -R 755 data