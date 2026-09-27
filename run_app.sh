#!/usr/bin/env bash
# Crypto Tokenomics Analyzer - 1-Click Launcher (Linux / macOS)

set -e

echo "========================================================"
echo "    Starting Crypto Tokenomics Analyzer & Engine...     "
echo "========================================================"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Run Streamlit
python3 -m streamlit run app.py --server.address=127.0.0.1
